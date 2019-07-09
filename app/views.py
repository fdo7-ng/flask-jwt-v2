from app import app
from flask import jsonify

@app.route('/index2')
def index2():
    return jsonify({'message': 'Hello, World! original index from jwt tutorial, view.py module'})