from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import UserModel
from datetime import datetime

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        
        
        
@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', posts=posts, current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = UserModel.query.filter_by(username=form.username.data).first()
        #user = UserModel.find_by_username( form.username.data )
        print(user)
        if user is None or not UserModel.check_password(form.password.data, user.password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, username=form.username.data)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<username>')
@login_required
def user(username):
    user = UserModel.query.filter_by(username=username).first_or_404()
    #user = UserModel.find_by_username(username)
    return render_template('user.html', user=user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        
        user = UserModel(username=form.username.data, email=form.email.data, 
                         fullname=form.fullname.data, 
                         password=UserModel.generate_hash(form.password.data))
                     
        new_user = UserModel(
            username = form.username.data,
            email = form.email.data,
            fullname = form.fullname.data,
            password = UserModel.generate_hash(form.password.data)
        )
        new_user.save_to_db()
        
        if UserModel.find_by_username(data['username']):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        else:
            flash('message: Something went wrong')
            return render_template('register.html', title='Register', form=form)
            
        
        
    return render_template('register.html', title='Register', form=form)
    
    
    # if form.validate_on_submit():
    #     if UserModel.find_by_username(form.username.data):
    #         flash('message: User {} already exists'.format(form.username.data))
        
    #     new_user = UserModel(
    #         username = form.username.data,
    #         email = form.email.data,
    #         fullname = form.fullname.data,
    #         password = UserModel.generate_hash(form.password.data)
    #     )
    #     print(new_user)
    #     try:
    #         new_user.save_to_db()
            
    #         if UserModel.find_by_username(form.username.data):
    #             access_token = create_access_token(identity = form.username.data)
    #             refresh_token = create_refresh_token(identity = form.username.data)
    #             flash('message: User {} was created'.format(form.username.data))  
    #             flash('Congratulations, you are now a registered user!')
    #             return redirect(url_for('login'))     
    #         else:
    #             return render_template('register.html', title='Register', form=form)     
    #     except:
    #         flash('message: Something went wrong')
    #     return render_template('register.html', title='Register', form=form)
        
    # return render_template('register.html', title='Register', form=form)


    #     user = UserModel(username=form.username.data, email=form.email.data)
    #     user.set_password(form.password.data)
    #     db.session.add(user)
    #     db.session.commit()
    #     flash('Congratulations, you are now a registered user!')
    #     return redirect(url_for('login'))
    # return render_template('register.html', title='Register', form=form)


