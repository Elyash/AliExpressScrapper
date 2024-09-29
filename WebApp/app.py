"""The main app module.
It opens web page with login and sign-up options ->
It stores the sign-up data in Users collection in MongoDB ->
It sends the home page (upon sucessfull login) ->
It fetches the user's gifts from MongoDB's Gift collection ->
It shows the gifts ->
It enable to add and remove gifts, as follow:
    Add:
        -> publish a gift_request to gift_requests_queue
        -> consumes this gift_request from scrapped_gifts_queue
        -> fetches the gift data from mongoDB's Gifts collection
    Remove:
        -> Delete the gift from mongoDB Gifts collection
"""
import bson

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length

from Utils import models, interfaces


app = Flask(__name__)
app.secret_key = 'secret_key'


class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])


@app.route('/')
def index():
    if 'email' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = interfaces.mongo_dbi.get_user(form.email.data)
        if user:
            flash("Email already registered.", 'danger')
            return redirect(url_for('login'))
        new_user = models.User(name=form.name.data, email=form.email.data, password=form.password.data)
        interfaces.mongo_dbi.add_user(new_user)
        session['email'] = new_user.email
        return redirect(url_for('home'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = interfaces.mongo_dbi.get_user(form.email.data)
        if user and user.password == form.password.data:
            session['email'] = user.email
            return redirect(url_for('home'))
        flash("Invalid email or password.", 'danger')
    return render_template('login.html', form=form)

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        gift_link = request.form.get('gift_link')
        user_email = session['email']

        if interfaces.mongo_dbi.get_gift(user_email, gift_link):
            flash("Gift already exists in your gifts.", 'danger')
            return redirect(url_for('home'))
        
        new_gift = models.Gift(user_email=user_email, link=gift_link)
        new_gift_id = interfaces.mongo_dbi.add_gift(new_gift).inserted_id

        interfaces.rabbitmq_dbi.publish_scrape_gift_request(new_gift_id)
        flash("Gift request submitted. Processing...", 'info')

    # Note: here we should pass the gifts with '_id' attributes to allow their deletion by id.
    user_gifts = interfaces.mongo_dbi.get_user_gifts_as_dicts(session['email'])
    return render_template('home.html', user_gifts=user_gifts)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/delete_gift/<gift_id>', methods=['DELETE'])
def delete_gift(gift_id):
    app.logger.warning(gift_id)
    interfaces.mongo_dbi.delete_gift_by_id(bson.ObjectId(gift_id))
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
