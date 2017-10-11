#the start of cubebot
import os

from flask import Flask, flash, g, jsonify, render_template, redirect, request, session, url_for
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, TextField
from wtforms.validators import InputRequired, Email, Length, URL
import json, requests, re

from db import db

from api_resources import FB_PAGE_TOKEN, FB_AccountLink_Code, FB_APP_ID, FB_APP_NAME, FB_APP_SECRET
from api_resources.trigger import Trigger, TriggerList
from api_resources.fbwebhooks import FBWebhook, sendBotMessage, getUserDetails, ReceivedTextAtt, getHTML
from api_resources.FBLogin import FBLogin
from api_resources.getstarted import GetStarted, Menu, Greeting, ChatExtension, Whitelist
from .model import TriggerModel, ContentModel, UserModel
from .security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from facebook import get_user_from_cookie, GraphAPI

# Facebook app details
FB_redirect_URI = "https://310aef3c.ngrok.io/test_cb"
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

class LinkSubmitForm(FlaskForm):
    link = TextField('Enter Link:', validators=[InputRequired(), Length(max=1024, message='link must be less than 1,024 characters.'), URL(require_tld=False, message='Sorry, check your link!')])
    # recaptcha = RecaptchaField()
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
        login_user(newUser, remember=True)
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
    ## Maybe add sometype of tracker or defualt mode for form submit url
    url = "" ## fburl this probably isn't the best way to handle this issue
    form = LoginForm() # *** login form ***

    checkForArgs = request.args
    print(checkForArgs, 'just checking to see if this is triggered on username path')
    session['checkArgs'] = checkForArgs
    print(session['checkArgs'], 'session stored')


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
            temp = True
            print(temp, 'checking for temp')
            if PSIDdata['recipient']:
                userPSID = PSIDdata['recipient']
                print(userPSID, 'here is the psid via accout linking code')
                session['psid'] = userPSID

            # form = LoginForm() # *** login form ***
            # checkForArgsAgain = request.args
            # print(checkForArgsAgain, 'checking for args again here ???????')
            # if form.validate_on_submit():
            #     print("this submit() and checkForArgsAgain path")
            #     checkUser = UserModel.find_by_username(username=form.username.data)
            #     session['username'] = form.username.data
            #     if checkUser is not None: ## this just confirms username is in DB
            #         if check_password_hash(checkUser.password, form.password.data):
            #             ## for account linking to an email user, we need to give some more thought ##
            #             url = FB_login_url + '?client_id={0}&redirect_uri={1}'.format(FB_APP_ID, FB_redirect_URI)
            #             login_user(checkUser, remember=form.remember.data)
            #             print("http://{0}".format(url), 'looking for this URL username to accountlink')
            #             return redirect(url) ## IF user is Account Linking via EmailAccount - we need to send user to different url
            #
            #     return '<h1>Invalid Username or Password</h1>' ##need to make this better

    else: ### hmmm maybe need separate path for Login AccountLining to Username
        print("does this work for no args and form submit??")
        # formArgs = session.get('checkArgs')
        # print(formArgs, 'args passed in via session.get')

        Link = session.get('my_link') ## remember this is for account linking
        print(Link, 'link from session.get account linking link from login before form.submit()')
        formUserPSID = session.get('psid')
        print(formUserPSID, 'this is psid related to form username')

        # form = LoginForm() # *** login form ***
        if form.validate_on_submit():

            print("submit button pressed")
            checkUser = UserModel.find_by_username(username=form.username.data)
            if checkUser is not None:
                print("username exists")
                if check_password_hash(checkUser.password, form.password.data):
                    print('passwork check was successful')
                    login_user(checkUser, remember=form.remember.data)
                    if Link:
                        print(formUserPSID, 'seeing if psid trickled down form area')
                        checkUser.FBuserPSID = formUserPSID
                        try:
                            db.session.commit()
                            print(checkUser, 'updated username with psid ')
                        except:
                            print(checkUsername, 'could not update username with psid')
                        ### Add code here to send to get FB credentials of user in chat window
                        return redirect(Link)
                    else:
                        return redirect(url_for('dashboard'))
            else: ##Added to capture case user attemtps login by username but has no account.
                return redirect(url_for('signup'))


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
            userPSID = session.get('psid')
            print(userPSID, 'this is the PSID from checkUser code in test_cb')

            Link = session.get('my_link') ## remember this is for account linking
            print(Link, 'link from session.get account linking link')

            checkUser = UserModel.find_by_FBuserID(FBuserID=FBuserID) ## what about checking to see if user has registered by email account/username??
            username = session.get('username')
            if username:
                print(username, 'new code for checking username for FB Account linking')
                checkUsername = UserModel.find_by_username(username=username)
                if checkUsername:
                    checkUsername.FBuserPSID = userPSID
                    checkUsername.FBuserID = FBuserID
                    checkUsername.FBAccessToken = tempAccessToken
                    print(checkUsername.FBuserPSID, 'set checkUsername PSID and FBuserID')
                    print(checkUsername.FBuserID, 'set checkUsername PSID and FBuserID')
                    print(checkUsername.FBAccessToken, 'set checkUsername PSID and FBuserID and access_token') #### this works to save username <--> fb credentials ###
                    try:
                        db.session.commit()
                        print(checkUsername, 'updated FB psid and id to username')
                    except:
                        print(checkUsername, 'could not update FB psid and id to username')
                    login_user(checkUser, remember=True)
                else:
                    print(checkUsername, 'username is currently not in db need to send to signup page')
                    # send to Signup Page or Login with Facebook

            if checkUser is not None:
                print(checkUser, 'fb user id is in db')
                if checkUser.FBuserPSID is None:
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
                if Link:
                    print(Link, 'session get method for checking for account link passed to handle_code')
                    return redirect(Link)
                else:
                    # login_user(newUser, remember=True)
                    return redirect(url_for('dashboard'))


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
                    login_user(newUser, remember=True)
                    return redirect(url_for('dashboard'))


        return redirect(url_for('login'), code=302)

    print(pkeys, 'pkeys printed')

    return 'success'


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    username = current_user.username
    user_id = current_user.id
    form = LinkSubmitForm() # *** link submit form ***
    if form.validate_on_submit():

        print(user_id, "link submit button pressed by this db user")

        newLink = form.link.data
        # print(newLink, "looking for submitted link")
        # print(username, "looking for username of link submitter")
        ## create function/call to save url to db for this username
        ## ADD LOGIC TO DETECT IF USER_ID HAS FB USER ID OR PSID
        imgURL = getHTML(newLink, "webform")

        if imgURL:
            print(imgURL, "recevied img url from function...")
            content = newLink
            urlCategory = "link"
            if current_user.FBuserPSID:
                print("user has fb user psid")
                urlContent = ContentModel("content title", urlCategory, content, imgURL, current_user.FBuserPSID)
            else:
                print("user does NOT have fb psid")
                urlContent = ContentModel("content title", urlCategory, content, imgURL, user_id)

            try:
                urlContent.save_to_db() ## cleaner code, saving the object to the DB using SQLAlchemy
            except:
                return {"message": "An error occured inserting the item."}, 500 #internal server error


        flash("Added to Library :)")


        return redirect(url_for('dashboard'))


    return render_template('dashboard.html', name=current_user.username, form=form)


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
    view = request.headers.get('User-Agent')
    print(view, 'looking for browser header details')
    userID = current_user.id
    print(userID, 'this is the db id from users table')
    FBname = current_user.FBname
    print(FBname, 'this is the db FB Name from users table')


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
    if FBname == "":
         print("no name will need to use user id to query db for content")
         userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.user_id == current_user.id).order_by(ContentModel.id.desc()).limit(9)
    else:
        userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.user_id == current_user.FBuserPSID).order_by(ContentModel.id.desc()).limit(9)
        # ## TESTING... QUERY BY USER.ID IS PROBABLY BEST TO HANDLE USERNAME AND FB.USERS
        # userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.user_id == current_user.id).order_by(ContentModel.id.desc()).limit(9)

    if userContentQuery is None:
        print("nothing to see here :-[ ")

    print(userContentQuery, 'did we get something??')
    userContent = userContentQuery[::1]
    print(userContent, 'do we see anything more??')

    userContentImageUrlList = []
    for item in userContent:
        userContentImageUrlList.append(item[3])
    print(userContentImageUrlList)

    userContentTitleList = []
    for item in userContent:
        userContentTitleList.append(item[1])
    print(userContentTitleList)

    userContentUrlList = []
    for item in userContent:
        userContentUrlList.append(item[2])
    print(userContentUrlList)

    userContentIdList = []
    for item in userContent:
        userContentIdList.append(item[0])
    print(userContentIdList)



## below is the non-current user content query -- to be removed

    # fileValue = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).order_by(ContentModel.id.desc()).limit(9)
    # # print(type(fileValue)) #this is a flask_sqlalchemy.BaseQuery
    #
    # results = fileValue[::1] #turns into a list
    # imageUrlList = []
    # for item in results:
    #     imageUrlList.append(item[3])
    #
    # titleList = []
    # for item in results:
    #     titleList.append(item[1])
    #
    # urlList = []
    # for item in results:
    #     urlList.append(item[2])
    #
    # idList = []
    # for item in results:
    #     idList.append(item[0])
    # print(idList)
    # #
    # # print(results)


    return render_template("/library.html", context=userContent, imageUrlList=userContentImageUrlList, titleList=userContentTitleList, urlList=userContentUrlList, idList=userContentIdList)

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
api.add_resource(ReceivedTextAtt, '/api/content/<string:username>') #trying to add content via api for user


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
