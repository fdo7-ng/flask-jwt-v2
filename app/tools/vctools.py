from flask import Flask, jsonify, request, redirect
import requests # Performs request to external site
from flask import render_template, flash, url_for
# from app import app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired
import json
from app.tools.console_tools import connect_viserver, get_attribute
from pyVmomi import vim
import jsonify
import os
from flask import Blueprint

from flask_login import current_user, login_required
from app.models import UserModel
from datetime import datetime


vctools = Blueprint('vctools', __name__)

class LaunchFormVC1(FlaskForm):
    #vcenter = StringField('vCenter', validators=[DataRequired()])
    vcenter = RadioField('vCenter',
        choices = [ ('10.159.11.51','10.159.81.51'),
                    ('10.159.81.248','10.159.81.248'),
                    ('10.159.18.21','10.159.18.21'),
                    ('10.159.18.51','10.159.18.51'),
                    ('172.16.168.21','172.16.168.21')],
        default='10.159.18.51')
    launch = SubmitField('launch')

class LaunchFormVC2(FlaskForm):
    vcenter = StringField('vCenter', validators=[DataRequired()])
    username= StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    launch = SubmitField('launch')

class LaunchConsoleForm(FlaskForm):
    vcenter = StringField('vCenter', validators=[DataRequired()])
    vmid= StringField('vmId', validators=[DataRequired()])
    launch = SubmitField('launch')

# Initializes Variable
def rpt_init(options):
    temp = {}
    temp['name'] = "name"
    temp['moId'] = "moId"
    for opt in options:
        temp[opt] = opt
    return temp

def rpt_init2(options):
    temp = {}
    temp['name'] = "name"
    temp['moId'] = "moId"
    temp['powerState'] = "powerState"
    for opt in options:
        temp[opt] = opt
    return temp

# Selectable Options
OPTION_LIST = {
    'guestFullName' : 'summary.config.guestFullName',
    'template' : 'summary.config.template',
    'vmPath' : 'summary.config.vmPathName',
    'guestId': 'summary.config.guestId',
    'guestFullName' : 'summary.config.guestFullName',
    'intanceuuid' : 'summary.config.instanceUuid',
    'uuid' : 'summary.config.uuid',
    'numCpu': 'summary.config.numCpu',
    'cpuReservation': 'summary.config.cpuReservation',
    'memoryReservation': 'summary.config.memoryReservation',
    'memorySizeMB': 'summary.config.memorySizeGB',
    'numEthernetCards': 'summary.config.numEthernetCards',
    'numVirtualDisks': 'summary.config.numVirtualDisks',
    'hostName': 'summary.guest.hostName',
    'ipAddress': 'summary.guest.ipAddress',
    'toolsRunningStatus': 'summary.guest.toolsRunningStatus',
    'toolsVersionStatus': 'summary.guest.toolsVersionStatus',
    'cpuAllocation.limit': 'config.cpuAllocation.limit',
    'cpuallocation.reservation': 'config.cpuAllocation.reservation',
    'memoryAllocation.limit': 'config.memoryAllocation.limit',
    'memoryAllocation.reservation': 'config.memoryAllocation.reservation',
    'powerState': 'runtime.powerState'
}


@vctools.route('/vc_main')
@login_required
def vc_main():
    return render_template('vctool_main.html', title='VC TOOLS', user=current_user)
    #return "flask vcenter vctools"

@vctools.route('/vc_rpt')
def vc_rpt():
    print("Running vCenter Report")
    vcenter = '10.159.18.21'
    username = 'ansible1@vsphere.local'
    password = 'Passw0rd!'


    si = connect_viserver(vcenter, username, password)
    if si == None:
        return render_template('500.html'), 500
    else:
        print("Successfully connected to vc: ", vcenter)


    content = si.RetrieveContent()

    container = content.rootFolder  # starting point to look into
    viewType = [vim.VirtualMachine]  # object types to look for
    recursive = True  # whether we should look into it recursively
    containerView = content.viewManager.CreateContainerView(
        container, viewType, recursive)
    rpt=[]
    children = containerView.view
    for child in children:
        #print_vm_info(child)
        temp = {}
        temp['moId'] = child._moId
        temp['name'] = child.summary.config.name
        temp['vmPath']= child.summary.config.vmPathName
        temp['guestFullName'] = child.summary.config.guestFullName
        temp['intanceuuid'] = child.summary.config.instanceUuid
        temp['uuid'] = child.summary.config.uuid
        rpt.vctoolsend(temp)

    data = json.dumps(rpt)
    return data

@vctools.route('/vc_rpt_j2', methods=['GET', 'POST'])
def vc_rpt_j2():
    print("Running vCenter Report")
    # vcenter = '10.159.18.21'
    username = 'ansible1@vsphere.local'
    password = 'Passw0rd!'
    print(OPTION_LIST.keys())

    form = LaunchFormVC1()
    if form.validate_on_submit():

        if request.method == "POST" :
            selected_options = request.form.getlist("options")
            #selected = request.form.getlist("opt1")
            print("Selected options: ", selected_options)


            vcenter = form.vcenter.data
            print("Selected vCenter: ", vcenter)

            si = connect_viserver(vcenter, username, password)
            if si == None:
                return render_template('500.html'), 500
            else:
                print("Successfully connected to vc: ", vcenter)

            content = si.RetrieveContent()
            container = content.rootFolder  # starting point to look into
            viewType = [vim.VirtualMachine]  # object types to look for
            recursive = True  # whether we should look into it recursively
            containerView = content.viewManager.CreateContainerView(
                container, viewType, recursive)
            rpt=[]
            rpt.append( rpt_init(selected_options))
            children = containerView.view
            for child in children:
                #print_vm_info(child)
                temp = {}
                temp['name'] = child.name
                temp['moId'] = child._moId
                # temp['template'] = child.summary.config.template
                # temp['vmPath']= child.summary.config.vmPathName
                # temp['guestFullName'] = child.summary.config.guestFullName
                # temp['intanceuuid'] = child.summary.config.instanceUuid
                # temp['uuid'] = child.summary.config.uuid

                for opt in selected_options:
                    temp[opt] = get_attribute(child, OPTION_LIST[opt])
                rpt.append(temp)


            data = json.dumps(rpt)
            loaded = json.loads(data)
            #return data # Returns raw json data
            return render_template('vc_rpt1_report.html', vcenter=vcenter ,data=loaded)

    return render_template('vc_rp1_launch.html',form=form, options= OPTION_LIST.keys())


## method 2 input vcenter, username and password
@vctools.route('/vc_rpt_j2_v2', methods=['GET', 'POST'])
def vc_rpt_j2_v2():
    print("Running vCenter Report - V2")

    form = LaunchFormVC2()
    if form.validate_on_submit():

        if request.method == "POST" :
            selected_options = request.form.getlist("options")
            #selected = request.form.getlist("opt1")
            print("Selected options: ", selected_options)
            vcenter = form.vcenter.data
            username = form.username.data
            password = form.password.data

            print("Selected vCenter: ", vcenter, " username : ", username)

            si = connect_viserver(vcenter, username, password)
            if si == None:
                return render_template('500.html'), 500
            else:
                print("Successfully connected to vc: ", vcenter)
            content = si.RetrieveContent()
            container = content.rootFolder  # starting point to look into
            viewType = [vim.VirtualMachine]  # object types to look for
            recursive = True  # whether we should look into it recursively
            containerView = content.viewManager.CreateContainerView(
                container, viewType, recursive)
            rpt=[]
            rpt.append( rpt_init(selected_options))
            children = containerView.view
            for child in children:
                #print_vm_info(child)
                temp = {}
                temp['name'] = child.name
                temp['moId'] = child._moId
                # temp['template'] = child.summary.config.template
                # temp['vmPath']= child.summary.config.vmPathName
                # temp['guestFullName'] = child.summary.config.guestFullName
                # temp['intanceuuid'] = child.summary.config.instanceUuid
                # temp['uuid'] = child.summary.config.uuid

                for opt in selected_options:
                    temp[opt] = get_attribute(child, OPTION_LIST[opt])
                rpt.append(temp)


            data = json.dumps(rpt)
            loaded = json.loads(data)
            #return data # Returns raw json data
            return render_template('vc_rpt1_report.html', vcenter=vcenter ,data=loaded)

    return render_template('vc_rp2_launch.html',form=form, options= OPTION_LIST.keys())


@vctools.route('/vc_console', methods=['GET', 'POST'])
def vc_console():
    print("Running vCenter Console")
    # vcenter = '10.159.18.21'
    username = 'ansible1@vsphere.local'
    password = 'Passw0rd!'


    form = LaunchFormVC1()
    form1 = LaunchConsoleForm()

    if request.method == "GET":
        return render_template('vc_rp1_launch.html',form=form)
    if form.validate_on_submit():

        if request.method == "POST" :
            selected_options = request.form.getlist("options")
            #selected = request.form.getlist("opt1")
            print("Selected options: ", selected_options)
            vcenter = form.vcenter.data
            print("Selected vCenter: ", vcenter)
            si = connect_viserver(vcenter, username, password)
            if si == None:
                return render_template('500.html'), 500
            content = si.RetrieveContent()
            container = content.rootFolder  # starting point to look into
            viewType = [vim.VirtualMachine]  # object types to look for
            recursive = True  # whether we should look into it recursively
            containerView = content.viewManager.CreateContainerView(
                container, viewType, recursive)
            rpt=[]
            rpt.append( rpt_init2(selected_options))
            children = containerView.view
            for child in children:
                #print_vm_info(child)
                temp = {}
                temp['name'] = child.name
                temp['moId'] = child._moId
                temp['powerState'] = child.runtime.powerState
                rpt.append(temp)

            data = json.dumps(rpt)
            loaded = json.loads(data)
            #return data # Returns raw json data

            console_server='10.159.82.162'
            console_url = 'https://' + console_server + '/consoleurl/'

            return render_template('vc_rpt1_console.html', vcenter=vcenter ,data=loaded, form=form1, url=console_url)


@vctools.route('/get_console/<vcenter>/<vmid>')
def get_concole(vcenter,vmid):
    print("Get console url")
    print("vCenter is : ", vcenter, " vmid : ", vmid)

    headers = {'content-type': 'application/json'}
    post = {
        'vcenter': vcenter,
        'vmid': vmid
    }

    console_server='10.159.82.162'
    post_url = 'https://' + console_server + '/consoleurl'
    resp = requests.post(post_url,verify=False,headers=headers, data=json.dumps(post))

    URL=resp.json()['URL'].replace('replace-w-appserverip', console_server)

    return redirect(URL)

    #dump = json.dumps(return_value)
    webbrowser.open(URL)
    return URL



# if __name__ == "__main__":
#     #app.run(host='0.0.0.0',threaded=True)
#     app.run(host="0.0.0.0", port=7050,threaded=True, debug=True)
