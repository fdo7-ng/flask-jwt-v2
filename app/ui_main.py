# ui_main.py
# https://scotch.io/tutorials/authentication-and-authorization-with-flask-login

from flask import Blueprint
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return 'Index'

@main.route('/profile')
def profile():
    return 'Profile'