import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'db/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = 'jwt-secret-string'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'some-secret-string'
# app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
# app.config['JWT_BLACKLIST_ENABLED'] = True
# app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']