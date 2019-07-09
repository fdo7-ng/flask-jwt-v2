# Project JWT


## Requirement 

pip install flask flask-restful flask-jwt-extended passlib flask-sqlalchemy flask-migrate
pip install python-env
pip install flask-login flask-wtf


## Create VENV
$ virtualenv -p python3 venv
### following command will activate virtual environment on macOs/Linux
$ source venv/bin/activate


## Database initialization and migration

Each time a change is made to the database schema, a migration script is added to the repository with the details of the change. To apply the migrations to a database, these migration scripts are executed in the sequence they were created.

1 create migration db folder
(venv) $ flask db init
2 generate migration script and display list of changes
(venv) $ flask db migrate -m "users table"
3 apply changes
(venv) $ flask db upgrade

https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database

## Reference
https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb

