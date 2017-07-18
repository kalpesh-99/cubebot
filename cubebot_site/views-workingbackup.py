#the start of cubebot
import os

from flask import Flask, flash, g, jsonify, render_template, redirect, request, session, url_for
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
import json, requests, re

from db import db

from api_resources import FB_PAGE_TOKEN, FB_AccountLink_Code, FB_APP_ID, FB_APP_NAME, FB_APP_SECRET
from api_resources.trigger import Trigger, TriggerList
from api_resources.fbwebhooks import FBWebhook, sendBotMessage, getUserDetails
from api_resources.FBLogin import FBLogin
from api_resources.getstarted import GetStarted, Menu, Greeting, ChatExtension, Whitelist
from .model import TriggerModel, ContentModel, UserModel
from .security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from facebook import get_user_from_cookie, GraphAPI

# Facebook app details
FB_redirect_URI = "http://cdb93c00.ngrok.io/test_cb"
FB_login_url = "https://www.facebook.com/v2.9/dialog/oauth"

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
    return render_template("index.html", app_name = FB_APP_NAME)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():

        hashedPassword = generate_password_hash(form.password.data, method='sha256') ## this works to hash password
        newUser = UserModel(username=form.username.data, email=form.email.data, password=hashedPassword, FBuserID="", FBuserPSID="", FBAccessToken="", FBname="" )
        newUser.save_to_db()
        context = {"greeting": "Welcome to qBit {}".format(newUser.username), "message":"Thanks For Registering!"}

        return render_template('dashboard.html', context=context)

    checkForArgs = request.args
    # pkeys = params.keys()
    print(checkForArgs, 'this is check for args')
    getKeyArgs = list(checkForArgs.keys())
    print(getKeyArgs, 'this is list of args keys')

    getKeyValue = list(checkForArgs.values())
    print(getKeyValue, 'this is key values?')

    if 'errorMessage' in getKeyArgs:
        error = getKeyValue[0]
        flash(error)

    url = FB_login_url + '?client_id={0}&redirect_uri={1}'.format(FB_APP_ID, FB_redirect_URI)

    return render_template('signup.html', form=form, FBurl=url)



@app.route('/login', methods=['GET', 'POST'])
def login():
    url = "" ## fburl this probably isn't the best way to handle this issue
    form = LoginForm() # *** login form ***

    if form.validate_on_submit(): ## form has valid entries and submitted
        # return '<h1>' + form.username.data + ' ' + form.password.data +'</h1>'
        # check to see if username is in our dB
            #if so, check to see if password matches
            # if so, redirect user to 'dashboard' logged in page
            #else,
        checkUser = UserModel.find_by_username(username=form.username.data)
        session['username'] = form.username.data
        if checkUser is not None: ## this just confirms username is in DB
            if check_password_hash(checkUser.password, form.password.data):
                ## for account linking to an email user, we need to give some more thought ##
                login_user(checkUser, remember=form.remember.data)
                return redirect(url_for('library')) ## IF user is Account Linking via EmailAccount - we need to send user to different url

        return '<h1>Invalid Username or Password</h1>' ##need to make this better


    checkForArgs = request.args
    if checkForArgs:
        print(checkForArgs, 'this is check for args')
        getKeyArgs = list(checkForArgs.keys())
        print(getKeyArgs, 'this is list of args keys')

        getKeyValue = list(checkForArgs.values())
        print(getKeyValue, 'this is key values?')
        if 'account_linking_token' in getKeyArgs:
            accountLinkToken = checkForArgs['account_linking_token']
            print(accountLinkToken, 'shoud be account link token')
            redirectURL = checkForArgs['redirect_uri']
            print(redirectURL, 'should be redirect url')
            handle_accountLinking(redirectURL)

            getPSIDurl = "https://graph.facebook.com/v2.6/me?access_token={0}&fields=recipient&account_linking_token={1}".format(FB_PAGE_TOKEN,accountLinkToken)
            getPSIDdata = requests.get(getPSIDurl)
            PSIDdata = getPSIDdata.json()
            print(PSIDdata, 'looking for psid json data')
            if PSIDdata['recipient']:
                userPSID = PSIDdata['recipient']
                print(userPSID, 'here is the psid via accout linking code')
                session['psid'] = userPSID

        else:
            return redirect(url_for('signup'))
            ## we need to hanle case open chatbot session, goto library, need to login fb user, then send to library? return redirect(url_for('library'))

    url = FB_login_url + '?client_id={0}&redirect_uri={1}'.format(FB_APP_ID, FB_redirect_URI)



    return render_template('login.html', form=form, FBurl=url)
# def login():
#     form = LoginForm() # *** login form ***
#
#
#     if form.validate_on_submit(): ## form has valid entries and submitted
#         # return '<h1>' + form.username.data + ' ' + form.password.data +'</h1>'
#         # check to see if username is in our dB
#             #if so, check to see if password matches
#             # if so, redirect user to 'dashboard' logged in page
#             #else,
#         checkUser = UserModel.find_by_username(username=form.username.data)
#         if checkUser is not None: ## this just confirms username is in DB
#             if check_password_hash(checkUser.password, form.password.data):
#                 login_user(checkUser, remember=form.remember.data)
#                 return redirect(url_for('library'))
#
#
#             return '<h1>Invalid Username or Password</h1>' ##need to make this better
        # return redirect(url_for('library'))


    # Code for account linking - letting user login via fB and link account (sender_id to FBuserID mapping)
    # checkForArgs = request.args
    # if checkForArgs:
    #     print(checkForArgs, 'this is check for args')
    #     getKeyArgs = list(checkForArgs.keys())
    #     print(getKeyArgs, 'this is list of args keys')
    #
    #     getKeyValue = list(checkForArgs.values())
    #     print(getKeyValue, 'this is key values?')
    #     if 'account_linking_token' in getKeyArgs:
    #         accountLinkToken = checkForArgs['account_linking_token']
    #         print(accountLinkToken, 'shoud be account link token')
    #         redirectURL = checkForArgs['redirect_uri']
    #         print(redirectURL, 'should be redirect url')
    #         handle_accountLinking(redirectURL)
    #
    #         getPSIDurl = "https://graph.facebook.com/v2.6/me?access_token={0}&fields=recipient&account_linking_token={1}".format(FB_PAGE_TOKEN,accountLinkToken)
    #         getPSIDdata = requests.get(getPSIDurl)
    #         PSIDdata = getPSIDdata.json()
    #         print(PSIDdata, 'looking for psid json data')
    #         if PSIDdata['recipient']:
    #             userPSID = PSIDdata['recipient']
    #             print(userPSID, 'here is the psid via accout linking code')
    #             session['psid'] = userPSID
    #
    #
    #     url = FB_login_url + '?client_id={0}&redirect_uri={1}'.format(FB_APP_ID, FB_redirect_URI)
    # url = "" ## fburl this probably isn't the best way to handle this issue
    # return render_template('login.html', form=form, FBurl=url)
    # return render_template('login.html', form=form)

def handle_accountLinking(redirectURL):
    urlForAccountLinking = redirectURL + '&authorization_code={0}'.format(FB_AccountLink_Code)
    print(urlForAccountLinking, "testing handle to account linking function")
    session['my_link'] = urlForAccountLinking
    return urlForAccountLinking





@app.route('/test_cb')
def handle_code():
    params = request.args
    pkeys = list(params.keys())

    if 'error' in pkeys:
        print(params['error'], 'looking for error value')
        if params['error'] == 'access_denied' and params['error_reason'] == 'user_denied':
            errorStatement = 'Sorry, please Login or Sign Up to continue.'
        else:
            errorStatement = "Oh dear! {0} because {1}".format(params['error'], params['error_reason'])
        # print("Error in authenticating: {0}".format(json.dumps(params)))
        return redirect(url_for('signup', errorMessage=errorStatement))

    if 'code' in pkeys:
        access_code = params['code']
        code_exch_URI = "https://graph.facebook.com/v2.9/oauth/access_token?client_id={0}&redirect_uri={1}&client_secret={2}&code={3}".format(FB_APP_ID, FB_redirect_URI, FB_APP_SECRET, access_code)
        # print(code_exch_URI, ' printing the code_exch_URI')
        response = requests.get(code_exch_URI) #this makes the get request to the code_exch_URI; handing over the access code to get access_token
        # print(response.content)
        content = response.json() #json of content should have access token in it
        # print(content, 'should have access token?')
        if 'access_token' in content:
            tempAccessToken = content['access_token']
            print(tempAccessToken, 'this should be the temp access token') ## got the access token
            getUserProfileURL = "https://graph.facebook.com/me?access_token={0}".format(tempAccessToken)
            getUserProfileData = requests.get(getUserProfileURL)
            UserProfileData = getUserProfileData.json()
            print(UserProfileData, 'is this also the user id?') ## easier way to get profile name and user id??
            if 'id' in UserProfileData:
                FBuserID = UserProfileData['id']
                print(FBuserID, 'looking for FB User ID value')

            else:
                print('did not find user id')

            if 'name' in UserProfileData:
                FBuserName = UserProfileData['name']
                print(FBuserName, 'looking for FB User Name')
                FBuserNameSplit = FBuserName.split(" ")
                FBuserFirstName = FBuserNameSplit[0]
                print(FBuserFirstName, 'looking at first name?') ### Currently not using name for facebok users; need to update Model

            else:
                print('did not find user name')
        # need to extract the access_token, check who the real user is via another fb call?, if user in our db then login to library/dash else, save user as new in db
            #check if fb id exists in database
            checkUser = UserModel.find_by_FBuserID(FBuserID=FBuserID) ## what about checking to see if user has registered by email account/username??
            username = session.get('username')
            if username: 
                print(username, 'new code for checking username for FB Account linking')
                # emailCheckUser = UserModel.find_by_username(username=username)
            userPSID = session.get('psid')
            print(userPSID, 'this is the PSID from checkUser code in test_cb')

            Link = session.get('my_link') ## remember this is for account linking

            if checkUser is not None:
                print(checkUser, 'fb user id is in db')
                if checkUser.FBuserPSID != userPSID:
                    checkUser.FBuserPSID = userPSID
                    print(checkUser.FBuserPSID, 'added FB PSID to User')
                else:
                    print(checkUser.FBuserPSID, ' not saved, FB PSID already assigned to User')

                if checkUser.FBAccessToken != tempAccessToken:
                    checkUser.FBAccessToken = tempAccessToken
                    # try:
                    #     db.session.commit()
                    #     print(checkUser.FBAccessToken, 'updated FB access token')
                    # except:
                    #     print(checkUser.FBAccessToken, 'could not update FB access token')

                else:
                    print(checkUser.FBAccessToken, 'FB access token not updated')

                try:
                    db.session.commit()
                    print(checkUser.FBAccessToken, 'updated FB access token')
                except:
                    print(checkUser.FBAccessToken, 'could not update FB access token')
                login_user(checkUser, remember=True)

                # Link = session.get('my_link')
                # if Link:
                #     print(Link, 'session get method for checking for account link passed to handle_code')
                #     return redirect(Link)
                # else:
                #     return redirect(url_for('library', context_name=FBuserFirstName[0]))
                # we want it to redirect to the account linking url if Login happens from Login Button in chat
            else:
                print(checkUser, 'fb user id is currently not in db')
                newUser = UserModel(username=None, email=None, password=None, FBuserID=FBuserID, FBuserPSID=userPSID, FBAccessToken=tempAccessToken, FBname=FBuserFirstName)
                try:
                    newUser.save_to_db()
                    print(newUser, "new user saved to db")
                except:
                    print(newUser, "couldn't save to db for some reason")
            #if fb id in db; then login user
            #if fb id not in db; then create new user with FB token, id, and name and login
            if Link:
                print(Link, 'session get method for checking for account link passed to handle_code')
                return redirect(Link)
            else:
                return redirect(url_for('library'))


        return redirect(url_for('login'), code=302)

    print(pkeys, 'pkeys printed')

    return 'success'


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
@login_required
def library():
    userID = current_user.id
    print(userID, 'this is the db id from users table')
    FBname = current_user.FBname

    # ### temp code to handel facebook login name capture to display on library page
    # try:
    #     params = request.args
    #     if params['context_name']:
    #         FBname = params['context_name']
    #         print(FBname)
    # except:
    #     pass
    # ### END-temp code to handel facebook login name capture to display on library page

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
api.add_resource(FBWebhook, '/api/fbwebhook')
api.add_resource(Greeting, '/api/fbsetup')
api.add_resource(GetStarted, '/api/fbsetup/getstarted')
api.add_resource(Menu, '/api/fbsetup/menu')
api.add_resource(ChatExtension, '/api/fbsetup/chatext')
api.add_resource(Whitelist, '/api/fbsetup/whitelist')
api.add_resource(FBLogin, '/API_FB_login')


### New code for manual facebook login ###

# @app.route('/fblogin')
# def fbloginHome():
#     text = '<a href="%s">Authenticate with facebook</a>'
#     print(text, 'happening at our /fblogin page')
#     return text % auth() # string subsitution to insert the href link based on the auth()
#
#
# @app.route('/auth')
# def auth():
# 	url = FB_login_url + '?client_id={0}&redirect_uri={1}'.format(FB_APP_ID, FB_redirect_URI)
# 	return url #this is the url that is  used in the href for fbloginhome(), the redirect leads to /test_cb

### END New code for manual facebook login ###



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
