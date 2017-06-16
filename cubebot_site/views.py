#the start of cubebot
import os

from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
import json, requests, re

from db import db

from api_resources.trigger import Trigger, TriggerList
from api_resources.fbwebhooks import FBWebhook, sendBotMessage
from api_resources.FBLogin import FBLogin
from api_resources.getstarted import GetStarted, Menu, Greeting, ChatExtension, Whitelist
from .model import TriggerModel, ContentModel, UserModel
from .security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


app = Flask(__name__)

api = Api(app)
# creating the app and configuring db and enabling api

# flask_login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))


# *** Creating the loginForm class -- we could relocate off this page at somepoint in the future ***
class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[InputRequired(message='A username is required'), Length(min=4, max=15, message='Username must have at least 4 characters.')])
    password = PasswordField('Password:', validators=[InputRequired(message='A password is required'), Length(min=8, max=80, message='Password must be at least 8 characters long.')])
    remember = BooleanField('Remember Me')
    recaptcha = RecaptchaField()
# *** Creating the loginForm class -- we could relocate off this page at somepoint in the future ***

# *** Creating the RegisterForm class -- we could relocate off this page at somepoint in the future ***
class RegisterForm(FlaskForm):
    username = StringField('Username:', validators=[InputRequired(), Length(min=4, max=15, message='Username must have at least 4 characters.')])
    password = PasswordField('Password:', validators=[InputRequired(), Length(min=8, max=80, message='Password must be at least 8 characters long.')])
    email = StringField('Email:', validators=[InputRequired(), Email(message='Invalid Email'), Length(max=50)])
    recaptcha = RecaptchaField()
# *** Creating the RegisterForm class -- we could relocate off this page at somepoint in the future ***


@app.route('/') #root directory - homepage of cubebot
def home():
    return render_template("index.html", app_name = "CubeBot")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm() # *** login form ***

    if form.validate_on_submit(): ## form has valid entries and submitted
        # return '<h1>' + form.username.data + ' ' + form.password.data +'</h1>'
        # check to see if username is in our dB
            #if so, check to see if password matches
            # if so, redirect user to 'dashboard' logged in page
            #else,
        checkUser = UserModel.find_by_username(username=form.username.data)
        if checkUser is not None: ## this just confirms username is in DB
            if check_password_hash(checkUser.password, form.password.data):
                login_user(checkUser, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return '<h1>Invalid Username or Password</h1>' ##need to make this better
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():

        hashedPassword = generate_password_hash(form.password.data, method='sha256') ## this works to hash password
        newUser = UserModel(username=form.username.data, email=form.email.data, password=hashedPassword, FBuserID="", FBAccessToken="")
        newUser.save_to_db()
        context = {"greeting": "Welcome to qBit {}".format(newUser.username), "message":"Thanks For Registering!"}

        return render_template('dashboard.html', context=context)


    return render_template('signup.html', form=form)





@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)


@app.route('/triggers') # cubebot triggers webview
def triggers():
	triggerNames = db.session.query(TriggerModel.name).all()
	# this becomes a list of tuples [('a',), ('b',)] for each 'name' value in the TriggerModel triggers table

	triggerWords = [', '.join(map(str, x)) for x in triggerNames]
	# now we've coverted every item in the tuples to string and joined them to create a list

	return render_template("/triggers.html", context=triggerWords)

@app.route('/library') # cubebot library webview
def library():
    ## Next Steps:
        ## need to check for user or require login
        ## return ContentModel Data for current user
    fileValue = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).order_by(ContentModel.id.desc()).limit(9)
    # print(type(fileValue)) #this is a flask_sqlalchemy.BaseQuery

    results = fileValue[::1] #turns into a list
    imageUrlList = []
    for item in results:
        imageUrlList.append(item[3])

    titleList = []
    for item in results:
        titleList.append(item[1])

    urlList = []
    for item in results:
        urlList.append(item[2])

    idList = []
    for item in results:
        idList.append(item[0])
    print(idList)
    #
    # print(results)


    return render_template("/library.html", context=results, imageUrlList=imageUrlList, titleList=titleList, urlList=urlList, idList=idList)

## since we send the context data, we shoud be able to complete the file share via MessengerExtensions from JS on webview;
## dont see why we should call the server/db again just to send from server.
## instead, send a tracker back to the server to keep the sharinging event history etc.

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/_load_ajax', methods=["GET", "POST"]) # this is to handle internal post requests
def load_ajax():

    if request.method == "POST":
        libraryShareContent = request.get_json()
        print(libraryShareContent)

        if libraryShareContent['file'] == 2:
            print(type(libraryShareContent))
        else:
            print("I didn't get the right number back")

### So in general, we'll need to take the data coming back and save it to our database for that particular user
    ## use recpeient_id; check that it exists in our UserModel( need to create still)
    ## Save content_id, thread_id, date to our database
    ## is there anything else we can get from the thread_id??

        # sender_id = 1347495131982426
        # sender_id = 1749436805074216
        # sendBotMessage(libraryShareContent, sender_id)
        # print(request.json['attachment'])
        return jsonify(libraryShareContent)


#connecting the resource to the api

api.add_resource(Trigger, '/api/trigger/<string:name>') # http://127.0.0.1:5000/student/Rolf
api.add_resource(TriggerList, '/api/triggers')
api.add_resource(FBWebhook, '/api/fbwebhook/')
api.add_resource(Greeting, '/api/fbsetup/')
api.add_resource(GetStarted, '/api/fbsetup/getstarted')
api.add_resource(Menu, '/api/fbsetup/menu')
api.add_resource(ChatExtension, '/api/fbsetup/chatext')
api.add_resource(Whitelist, '/api/fbsetup/whitelist')
api.add_resource(FBLogin, '/API_FB_login')






## API Connections for the following:
    # Webhook to FB Messenger
        #what can we do?

    # Webhook to Cubes Service
        #send content info to Cubes
        #receive thumbnail and link to file


## Model
    # User
        #FB Login
        #CubesProfile

    # Content
        #Type (pdf, word, link, photo)
        #Date
        #From-Contact
        #From-Channel

    # Content overlay/mods -- can we access FB Messenger Filters??


    # q= get related content on any qbot content //maybe create a cube of related content
        #Twitter
        #Pinterest
        #FB
        #

    # Channels
        #FB Messenger Group id (stuff shared in groups)
        #FB Messenger Friend id (stuff shared between friends)
        #InputConnections
            #Dropbox
            #Gdrive
            #Cubes Library
