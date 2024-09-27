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
import time
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length
from pymongo import MongoClient
import pika
from dataclasses import dataclass
import json
import os

app = Flask(__name__)
app.secret_key = 'secret_key'

# MongoDB setup
mongo_client = MongoClient("mongodb", port=27017, username='admin', password='password')
db = mongo_client['MyFullstackProject']
users_collection = db['Users']
gifts_collection = db['Gifts']

# RabbitMQ setup
time.sleep(10)
time.sleep(10)
connection_params = pika.ConnectionParameters(
    host='rabbitmq',
    port=5672,
    credentials=pika.PlainCredentials(
        username='user', password='password'
    )
)
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
channel.queue_declare(queue='gift_requests_queue')

@dataclass
class User:
    name: str
    email: str
    password: str

@dataclass
class GiftRequest:
    link: str
    user_email: str

class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=50)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])

def get_user(email):
    return users_collection.find_one({"email": email})

def add_user(user):
    users_collection.insert_one(user.__dict__)

def add_gift(gift):
    gifts_collection.insert_one(gift)

def publish_gift_request(gift_request):
    channel.basic_publish(exchange='', routing_key='gift_requests_queue', body=json.dumps(gift_request.__dict__))

@app.route('/')
def index():
    if 'email' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        user = get_user(form.email.data)
        if user:
            flash("Email already registered.", 'danger')
            return redirect(url_for('login'))
        new_user = User(name=form.name.data, email=form.email.data, password=form.password.data)
        add_user(new_user)
        session['email'] = new_user.email
        return redirect(url_for('home'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form.email.data)
        if user and user['password'] == form.password.data:
            session['email'] = user['email']
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
        gift_request = GiftRequest(link=gift_link, user_email=user_email)
        publish_gift_request(gift_request)
        flash("Gift request submitted. Processing...", 'info')

    user_gifts = list(gifts_collection.find({"user_email": session['email']}))
    return render_template('home.html', user_gifts=user_gifts)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/delete_gift/<gift_id>', methods=['DELETE'])
def delete_gift(gift_id):
    gifts_collection.delete_one({"_id": gift_id})
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
