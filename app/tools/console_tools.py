#!/usr/bin/env python3
import atexit
from datetime import datetime
import requests
import json
from requests.auth import HTTPBasicAuth
from pyVmomi import vim
import xmltodict
import ssl
import os

from pyVim.connect import SmartConnectNoSSL, Disconnect
from jmespath import search as jp


def create_dir(path):
    try:
        os.makedirs(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s" % path)


"""
logger usage logger("/var/log", "console","started")
"""


def logger(log_path, log_name, msg):
    print("File name =", log_name)
    print("message - ", msg)

    if os.path.isdir(log_path):
        print("Found path : ", log_path)
    else:
        print("Path Not found:", log_path, " -- Creating")
        create_dir(log_path)

    log_file = os.path.join(log_path, log_name) + \
        "_" + datetime.now().strftime("%d_%m_%Y") + ".log"
    #print(log_file)

    dtime = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

    message = dtime + " -- " + msg + "\r\n"
    print(message)
    with open(log_file, "a+") as f:
        f.write(message)


"""generateConsoleAccessSessionToken
#https://.../caas/2.0/<CUSTOMER-ORG-ID>/customer-private/
#generateConsoleAccessSessionToken
"""


def generate_console_console_token(api_url, username, password, server_id):
    xml_post = """<urn:generateConsoleAccessSessionToken id="serverId" xmlns:urn="urn:didata.com:api:cloud:types"/>"""
    xml_post = xml_post.replace('serverId', server_id)

    headers = {'Content-Type': 'application/xml'}  # set what your server accepts
    response = requests.post(api_url, data=xml_post, headers=headers,
                             auth=HTTPBasicAuth(username, password))

    xml_response = response.content
    print("Encoding - ", response.encoding)

    if xml_response == "":
        return None
    else:
        resp = xmltodict.parse(xml_response)
        token = resp['consoleAccessSessionToken']['#text']
        data = {
            'username': username,
            'token': token
        }
        return data


"""
## UseConsoleSession
# Sample Response:
# <?xml version="1.0" encoding="UTF-8"?>
# <gatewayDetails xmlns="urn:didata.com:api:cloud:admin:types">
# <remoteConsoleHostIpAddress>10.159.18.21</remoteConsoleHostIpAddress>
# <virtualMachineId>vm-2587</virtualMachineId>
# <virtualMachineFolder>3ae4856d-4122-4b68-8954-449e61d82a28</virtualMachineFolder>
# <rdpHostIpAddress>10.159.82.163</rdpHostIpAddress></gatewayDetails>
"""


def use_console_token(api_url, username, token, admusername, admpassword):

    xmldata = """<urn:useConsoleSessionToken xmlns:urn="urn:didata.com:api:cloud:admin:types"><urn:username>replacewusername</urn:username><urn:token>replacewtoken</urn:token></urn:useConsoleSessionToken>"""
    xmldata = xmldata.replace('replacewusername', username)
    xmldata = xmldata.replace('replacewtoken', token)
    print(xmldata)

    headers = {'Content-Type': 'application/xml'}  # set what your server accepts
    response = requests.post(api_url, data=xmldata, headers=headers,
                             auth=HTTPBasicAuth(admusername, admpassword))
    if response.encoding is None:
        response.encoding = 'utf-8'

    content = response.content
    rcode = response.status_code
    print("Response Code ", rcode)
    print("Encoding - ", response.encoding)
    # Convert to xmltodic
    if response.status_code == 200:
        resp = xmltodict.parse(content)
        data = {
            'vcenter': resp['gatewayDetails']['remoteConsoleHostIpAddress'],
            'vmid': resp['gatewayDetails']['virtualMachineId'],
            'vmfolder': resp['gatewayDetails']['virtualMachineFolder'],
            'rdphostIP': resp['gatewayDetails']['rdpHostIpAddress']
        }
        return data
    else:
        return None


def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def find_vm(content, vmname):
    vm = get_obj(content, [vim.VirtualMachine], vmname)
    return vm


def find_vm_by_id(content, vmid):

    container = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True)
    for c in container.view:
        if c._moId == vmid:
            found_vm = c
            return found_vm


"""
Connect to vCenter
"""

def connect_viserver(vcenter, user, password):
    try:
        service_instance = SmartConnectNoSSL(host=vcenter, user=user, pwd=password)
        # doing this means you don't need to remember to disconnect your script/objects
        atexit.register(Disconnect, service_instance)
    except requests.exceptions.SSLError as e:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_NONE

        service_instance = SmartConnectNoSSL(
            host=vcenter, user=user, pwd=password, sslContext=context)
        # doing this means you don't need to remember to disconnect your script/objects
        atexit.register(Disconnect, service_instance)
    except vim.fault.InvalidLogin:
        print("Invalid Login - username or password.")
        return None
    return service_instance



'''
    Traverse thru object attributes
    get_attribute(object, 'summary.config.vmPathName')
    - it will loop thru the paths and return teh vmPathName
'''
def get_attribute(obj, path):
    temp_obj = obj
    str_path = path.split('.')
    for itm in str_path:
        #print("Tracking -- ", itm)
        if hasattr(temp_obj, itm):
            temp_obj = getattr(temp_obj, itm)
        else:
            temp_obj = jp(itm, temp_obj )
    return temp_obj
