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
from api_resources.fbwebhooks import FBWebhook, sendBotMessage, getUserDetails, ReceivedTextAtt, getHTML, getSharedThreadIDdetails
from api_resources.FBLogin import FBLogin
from api_resources.getstarted import GetStarted, Menu, Greeting, ChatExtension, Whitelist
from api_resources.getLinkData import getLinkContent
from api_resources.thoughtsOn import getThought
from api_resources.qreviews import getRecentReviews
from api_resources.qreviewsFilter import getFilterReviews

from .model import TriggerModel, ContentModel, UserModel, ThreadModel, ThreadContentModel, ReviewsModel
from .security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from facebook import get_user_from_cookie, GraphAPI

# Facebook app details
FB_redirect_URI = "https://4425ff68.ngrok.io/test_cb"
FB_login_url = "https://www.facebook.com/v2.9/dialog/oauth"

app = Flask(__name__)

api = Api(app)
# creating the app and configuring db and enabling api

# flask_login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

per_page = 9

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
        context = "Thanks For Registering!"
        login_user(newUser, remember=True)
        # return render_template('dashboard.html', context=context, form=form, formLink=formLink)
        return redirect(url_for('dashboard', context=context))

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


def handle_accountLinking(redirectURL):
    urlForAccountLinking = redirectURL + '&authorization_code={0}'.format(FB_AccountLink_Code)
    print(urlForAccountLinking, "testing handle to account linking function")
    session['my_link'] = urlForAccountLinking
    return urlForAccountLinking

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

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
                print(checkUser.FBuserPSID, 'fb user psid check')
                if checkUser.FBuserPSID is None and userPSID is not None:
                    checkUser.FBuserPSID = userPSID
                    print(checkUser.FBuserPSID, 'added FB PSID to User')
                elif checkUser.FBuserPSID is not None and userPSID is not None:
                    checkUser.FBuserPSID = userPSID
                    print(checkUser.FBuserPSID, 'need to updated the PSID for user')
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
    checkArgs = request.args.get("context")
    print(checkArgs, 'this is checkArgs get for context')

    if checkArgs:
        context = checkArgs
        print(context, "checking post checkArgs context")
    else:
        context ={}


    form = LinkSubmitForm() # *** link submit form ***
    if form.validate_on_submit():

        print(user_id, "link submit button pressed by this db user")

        formLink = form.link.data
        ## create function/call to save url to db for this username
        ## ADD LOGIC TO DETECT IF USER_ID HAS FB USER ID OR PSID
        formLinkData = getLinkContent(formLink, "webform")


        if formLinkData:
            imgURL = formLinkData[0]
            linkTitle = formLinkData[1]
            linkURL = formLinkData[2]
            linkType = formLinkData[3]
            linkSource = formLinkData[4]
            print(formLinkData, "recevied form link data from function...")
            # content = newLink
            if linkType:
                urlCategory = linkType
            else:
                urlCategory = "link"

            if current_user.FBuserPSID:
                print("user has fb user psid")
                urlContent = ContentModel(linkTitle, urlCategory, linkURL, imgURL, linkSource, user_id) ## temp fix for userid/FBuserPSID
            else:
                print("user does NOT have fb psid")
                urlContent = ContentModel(linkTitle, urlCategory, linkURL, imgURL, linkSource, user_id)

            try:
                urlContent.save_to_db() ## cleaner code, saving the object to the DB using SQLAlchemy
            except:
                return {"message": "An error occured inserting the item."}, 500 #internal server error


        flash("Added to Library :)")


        return redirect(url_for('dashboard'))


    return render_template('dashboard.html', context=context, name=current_user.username, form=form)


@app.route('/triggers') # cubebot triggers webview
def triggers():
	triggerNames = db.session.query(TriggerModel.name).all()
	# this becomes a list of tuples [('a',), ('b',)] for each 'name' value in the TriggerModel triggers table

	triggerWords = [', '.join(map(str, x)) for x in triggerNames]
	# now we've coverted every item in the tuples to string and joined them to create a list

	return render_template("/triggers.html", context=triggerWords)

@app.route('/library', methods=['GET', 'POST'])
@app.route('/library/<int:page>', methods=['GET', 'POST']) # cubebot library webview
@login_required
def library(page=1):

    view = request.headers.get('User-Agent')
    print(view, 'looking for browser header details')
    print(type(view))
    if "Messenger" in view:
        print("looks like browser = Messenger")
        setMessengerContextDetails = True
    else:
        print("browser NOT in Messenger")
        setMessengerContextDetails = False

    userID = current_user.id
    print(userID, 'this is the db id from users table')
    FBname = current_user.FBname
    print(FBname, 'this is the db FB Name from users table')

    ## Next Steps:
        ## need to check for user or require login
        ## return ContentModel Data for current user
    if FBname == "":
         print("no name will need to use user id to query db for content")
         userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.user_id == current_user.id).order_by(ContentModel.id.desc()).paginate(page, per_page, False)
    else:
        userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.user_id == current_user.id).order_by(ContentModel.id.desc()).paginate(page, per_page, False)
        # ## TESTING... QUERY BY USER.ID IS PROBABLY BEST TO HANDLE USERNAME AND FB.USERS
        # userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.user_id == current_user.id).order_by(ContentModel.id.desc()).limit(9)

        # urlImages = userContentQuery.urlImage
        userContent = userContentQuery.items
        print(userContent, "what do we see here?")
        print(type(userContent))
        print(userContentQuery, "should be the object")
        print(type(userContentQuery))
        print(userContentQuery.has_next, "has next?")
        print(userContentQuery.has_prev, "has next?")

    return render_template("/library.html", userContent=userContentQuery, inMessenger=setMessengerContextDetails)

## since we send the context data, we shoud be able to complete the file share via MessengerExtensions from JS on webview;
## dont see why we should call the server/db again just to send from server.
## instead, send a tracker back to the server to keep the sharinging event history etc.

@app.route('/library/friends') # cubebot library webview
@login_required
def friends():
    userID = current_user.id
    print(userID, 'this is the db id from users table')
    FBname = current_user.FBname
    print(FBname, 'this is the db FB Name from users table')

    # need a list of thread_id's for current user
    ## checking for FB user ... NEED TO HANDLE CASE FOR NON-FB USER
    if FBname == "":
         print("no name, we need to use user id to query db for content")
        #  userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.user_id == current_user.id).order_by(ContentModel.id.desc()).limit(9)
    else:
        print("does this else get run at all?")
        userThreadQuery = db.session.query(ThreadModel.id, ThreadModel.thread_id).filter(ThreadModel.thread_userID == current_user.id).order_by(ThreadModel.id.desc()).all()
        print(userThreadQuery, 'pre if is none - did we get something??')
        if userThreadQuery is None:
            print("nothing to see here :-[ ")
        print(userThreadQuery, 'did we get something??')
        # userThreads = userThreadQuery[::1] ## interesting didn't need to do this as per library userContent query
        # print(userThreads, 'do we see anything more??')

        userThreadsList = []
        for item in userThreadQuery:
            userThreadsList.append(item[1])
        print(userThreadsList)
        numberOfThreads = len(userThreadsList)
        print(numberOfThreads, "this is how many friends we've shared with")

        userThreadIDList = []
        for item in userThreadQuery:
            userThreadIDList.append(item[0])
        print(userThreadIDList)

    numberOfThreads = 3
    userThreadIDList = [1, 2, "a", "b"]

    # need a list of content for each thread_id

    return render_template("/friends.html", FBChatCount=numberOfThreads, threadIDList=userThreadIDList)

@app.route('/library/friends/<int:thread_id>', methods=['GET', 'POST'])
@app.route('/library/friends/<int:thread_id>/<int:page>', methods=['GET', 'POST'])
@login_required
def show_thread(thread_id, page=1):

    view = request.headers.get('User-Agent')
    print(view, 'looking for browser header details')
    print(type(view))
    if "Messenger" in view:
        print("looks like browser = Messenger")
        setMessengerContextDetails = True
    else:
        print("browser NOT in Messenger")
        setMessengerContextDetails = False


    threadID = thread_id
    print(threadID, "this should be the thread id")
    print(thread_id, "this should be the thread_id")
    getThread_ID = db.session.query(ThreadModel.thread_id).filter(ThreadModel.id == thread_id).first()
    Thread_ID_Value = getThread_ID[0]
    print(getThread_ID, "this should be the getThread_ID value")
    print(Thread_ID_Value, "this should be the Thread_ID_Value value")

    if Thread_ID_Value:
        print(Thread_ID_Value, "looks like we have this Thread_ID_Value in DB")
        getThreadContentQuery = db.session.query(ThreadContentModel.id, ThreadContentModel.contentID).filter(ThreadContentModel.threadID == Thread_ID_Value).order_by(ThreadContentModel.id.desc()).all()
        print(getThreadContentQuery, "getThreadContentQuery looks like this")



        if getThreadContentQuery:

            threadContent = getThreadContentQuery
            print(threadContent, "what does this look like?")


            userContentForThisThread = []
            for item in getThreadContentQuery:
                userContentForThisThread.append(item[1])
            # print(userContentForThisThread, "this should be the list of ThreadContent ids")

            # getThreadLibraryContent = getLibraryContent(userContentForThisThread)
            getThreadLibraryContent = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.id.in_(userContentForThisThread)).order_by(ContentModel.id.desc()).paginate(page, per_page, False)

            print(getThreadLibraryContent, "what is this??")
            ThreadLibraryContent = getThreadLibraryContent.items
            print(ThreadLibraryContent, "any item info?")

            return render_template("/threadLibrary.html", FBChatCount=thread_id, threadContent=getThreadLibraryContent, inMessenger=setMessengerContextDetails)
        else:
            responseString = "Aw snap, shared content is gone"
            return render_template("/threadLibrary.html", responseString=responseString)

    return render_template("/friends.html", FBChatCount=thread_id)



@app.route('/library/filter/<string:filter_type>', methods=['GET', 'POST'])
@app.route('/library/filter/<string:filter_type>/<int:page>', methods=['GET', 'POST'])
@login_required
def show_filter(filter_type, page=1):

    view = request.headers.get('User-Agent')
    print(view, 'looking for browser header details')
    print(type(view))
    if "Messenger" in view:
        print("looks like browser = Messenger")
        setMessengerContextDetails = True
    else:
        print("browser NOT in Messenger")
        setMessengerContextDetails = False


    category = filter_type
    print(category, "this should be the thread id")
    print(filter_type, "this should be the thread_id")

    userID = current_user.id
    print(userID, 'this is the db id from users table')
    FBname = current_user.FBname
    print(FBname, 'this is the db FB Name from users table')


    ## Filter Type Notes:
        # filterDictionary = {
        # '1':'video',
        # '2':'article',
        # '3':'product',
        # '4':'video.tv_show',
        # '5':'video.movie',
        # '6':'website',
        # '7':'image',
        # '8':'instapp:photo',
        # '9':'pinterestapp:pin',
        # '10':'airbedandbreakfast:listing',
        # '11':'flipboard:magazine'
        # }

    if FBname == "":
         print("no name will need to use user id to query db for content")
         userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.user_id == current_user.id).order_by(ContentModel.id.desc())
    else:
        userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.user_id == current_user.id).order_by(ContentModel.id.desc())
        # userFilteredContentQuery = userContentQuery.filter(ContentModel.category == category).paginate(page, per_page, False)

    userFilteredContentQuery = userContentQuery.filter(ContentModel.category == category).paginate(page, per_page, False)

    if userFilteredContentQuery:
        print(userFilteredContentQuery, "this should be the filter content object")

        # userContentForThisFilter = []
        # for item in userFilteredContentQuery:
        #     userContentForThisFilter.append(item[0])
        #
        # print(userContentForThisFilter, "this should be the list of content for this filter")
        return render_template("/filterLibrary.html", FBChatCount=category, threadContent=userFilteredContentQuery, inMessenger=setMessengerContextDetails)
        #     else:
        #         responseString = "Aw snap, shared content is gone"
        #         return render_template("/threadLibrary.html", responseString=responseString)


    # getCategory = db.session.query(ThreadModel.thread_id).filter(ThreadModel.id == thread_id).first()
    # Thread_ID_Value = getThread_ID[0]
    # print(getThread_ID, "this should be the getThread_ID value")
    # print(Thread_ID_Value, "this should be the Thread_ID_Value value")
    #
    # if Thread_ID_Value:
    #     print(Thread_ID_Value, "looks like we have this Thread_ID_Value in DB")
    #     getThreadContentQuery = db.session.query(ThreadContentModel.id, ThreadContentModel.contentID).filter(ThreadContentModel.threadID == Thread_ID_Value).order_by(ThreadContentModel.id.desc()).all()
    #     print(getThreadContentQuery, "getThreadContentQuery looks like this")
    #
    #
    #
    #     if getThreadContentQuery:
    #
    #         threadContent = getThreadContentQuery
    #         print(threadContent, "what does this look like?")
    #
    #
    #         userContentForThisThread = []
    #         for item in getThreadContentQuery:
    #             userContentForThisThread.append(item[1])
    #         # print(userContentForThisThread, "this should be the list of ThreadContent ids")
    #
    #         # getThreadLibraryContent = getLibraryContent(userContentForThisThread)
    #         getThreadLibraryContent = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.id.in_(userContentForThisThread)).order_by(ContentModel.id.desc()).paginate(page, per_page, False)
    #
    #         print(getThreadLibraryContent, "what is this??")
    #         ThreadLibraryContent = getThreadLibraryContent.items
    #         print(ThreadLibraryContent, "any item info?")
    #
    #         return render_template("/threadLibrary.html", FBChatCount=thread_id, threadContent=getThreadLibraryContent, inMessenger=setMessengerContextDetails)
    #     else:
    #         responseString = "Aw snap, shared content is gone"
    #         return render_template("/threadLibrary.html", responseString=responseString)

    return render_template("/filterLibrary.html", FBChatCount="failed")



@app.route('/_load_ajax', methods=["GET", "POST"]) # this is to handle internal post requests
def load_ajax():

    if request.method == "POST":
        libraryShareContent = request.get_json()
        print(libraryShareContent)
        thread_id = libraryShareContent['thread_id']
        print(thread_id, "should be the thread id")
        userPSID = libraryShareContent['psid']
        print(userPSID, "should be the user psid")
        threadType = libraryShareContent['thread_type']
        print(threadType, "should be the thread type")
        contentID = libraryShareContent['file']
        print(contentID, "should be the content id")

        user = current_user
        print(user.id, "should be current_user id from db")


        checkUser = UserModel.find_by_FBuserPSID(FBuserPSID=userPSID)
        if checkUser:
            userFBID = checkUser.FBuserID
            userFBAccessToken = checkUser.FBAccessToken
            print(checkUser, "checUser object")
            print(userFBID, "is this my fb user id?")
            print(userFBAccessToken, "is this my fb user id?")
            print(checkUser.id, "this should be users db user id")
        # looking to use thread id to get more info on the recepient
            sharedToData = getSharedThreadIDdetails(userFBID, userFBAccessToken, thread_id)
            print(sharedToData, "looking for shared to recepient data")

        if threadType == 'USER_TO_USER':
            thread_type = 1
        else:
            thread_type = 2 #group

        thread_channel = "Messenger"

        checkThread = ThreadModel.find_by_threadID(thread_id=thread_id)
        if checkThread:
            print(thread_id, " already exists in our DB")
            print("continue direclty to save content to ThreadContentModel")
            # save content share transaction to ThreadContentModel
            newThreadContent = ThreadContentModel(thread_id, contentID)
            try:
                newThreadContent.save_to_db()
                print(newThreadContent, "new threadContent saved to db")
                checkIfThreadContentSaved = True
            except:
                print(newThread, "couldn't save threadContent to db for some reason")


        else:
            print(thread_id, "is NOT in our DB yet - We should save it")
            newThread = ThreadModel(thread_id, thread_type, thread_channel, user.id)
            try:
                newThread.save_to_db()
                print(newThread, "new thread saved to db")
                checkIfThreadSaved = True
            except:
                print(newThread, "couldn't save to db for some reason")

            if checkIfThreadSaved == True:
                print("ok, we can now go ahead and save to ThreadContentModel")
                newThreadContent = ThreadContentModel(thread_id, contentID)
                try:
                    newThreadContent.save_to_db()
                    print(newThreadContent, "new threadContent saved to db")
                    checkIfThreadContentSavedNewThread = True
                except:
                    print(newThread, "couldn't save threadContent to db for some reason")
                if checkIfThreadContentSavedNewThread == True:
                    print("Created new Thread and Saved new ThreadContent!!!")



        if libraryShareContent['file'] == 2:
            print(type(libraryShareContent))
        else:
            print("I didn't get the right number back")


        return jsonify(libraryShareContent)

@app.route('/_load_ajax_review_public', methods=["GET", "POST"]) # this is to handle internal post requests
# reviewson.html has ajax call to this endpoint; redirect code after call: http://aa75436e.ngrok.io (might need to modify this)
def load_ajax_review_public():
    #CURRENTLY ONLY USING 1 homepageLinkID
    if request.method == "POST":
        contentReview = request.get_json()
        print(contentReview)

        user_ID = contentReview['userID']
        print(user_ID, "should be our user id")

        content_id = contentReview['thoughtsON']
        print(content_id, "should be the content id")

        reviewerID = contentReview['friend']
        print(reviewerID, "should be the user psid")

        reviewValue = contentReview['thoughtValue']
        print(reviewValue, "should be the review value")

        thoughtTitle = contentReview['thoughtTitle']
        print(thoughtTitle, "should be the title ")

        checkContentID = content_id
        print(checkContentID, "checking for checkContentID")

        if checkContentID == "1":
            print("path of public 1")
            publicReviewContent = -1
            newPublicReview = ReviewsModel(reviewValue, -1, publicReviewContent, -1)

        elif checkContentID == "2":
            print("path public 2")
            publicReviewContent = -2
            newPublicReview = ReviewsModel(reviewValue, -1, publicReviewContent, -1)

        elif checkContentID == "3":
            print("path public 2")
            publicReviewContent = -3
            newPublicReview = ReviewsModel(reviewValue, -1, publicReviewContent, -1)

        try:
            newPublicReview.save_to_db()
            print(newPublicReview, "new review saved to db")
            checkIfReviewSaved = True
        except:
            print(newPublicReview, "couldn't save review")
            checkIfReviewSaved = False

        return jsonify(contentReview)



@app.route('/_load_ajax_review', methods=["GET", "POST"]) # this is to handle internal post requests
# reviewson.html has ajax call to this endpoint; redirect code after call: http://aa75436e.ngrok.io (might need to modify this)
def load_ajax_review():
    if request.method == "POST":
        contentReview = request.get_json()
        print(contentReview)

        user_ID = contentReview['userID']
        print(user_ID, "should be our user id")

        content_id = contentReview['thoughtsON']
        print(content_id, "should be the content id")

        reviewerID = contentReview['friend']
        print(reviewerID, "should be the user psid")

        reviewValue = contentReview['thoughtValue']
        print(reviewValue, "should be the review value")

        thoughtTitle = contentReview['thoughtTitle']
        print(thoughtTitle, "should be the title ")

        checkUser = UserModel.find_by_FBuserPSID(FBuserPSID=user_ID) #will need sort out non-fb (username)later
        if checkUser:
            print(checkUser.FBname, "yes, user for which content was rated is in db")
            print(checkUser.id, "user.id, in our db")
            print(checkUser.FBuserPSID, "psid, sender_id for bot message?")
            idForUser = checkUser.id
            contentTitle = thoughtTitle

            newReview = ReviewsModel(reviewValue, idForUser, content_id, reviewerID)
            try:
                newReview.save_to_db()
                print(newReview, "new review saved to db")
                checkIfReviewSaved = True
            except:
                print(newReview, "couldn't save review")
                checkIfReviewSaved = False


            if checkIfReviewSaved == True:
                message = "Congrats, someone gave you a {0} star rating on {1}.".format(reviewValue, contentTitle)
                messageText = {"text":message} #maybe add rating value and link to thoughtsON page?
                sendMessage = sendBotMessage(messageText, checkUser.FBuserPSID)
            # return ?

        # if useer: record rating value in db
        # send user message using botMessage?

        return jsonify(contentReview)

@app.route('/content/thoughtson/public', methods=['GET', 'POST'])
def show_public():
    #CURRENTLY ONLY USING 1 homepageLinkID
    homepageLinkID = request.args.get('homepageLinkID', type = int)
    print(homepageLinkID)

    if homepageLinkID == 1:
        contentURL = "https://www.youtube.com/watch?v=VY-VQ0KvhgU"
        contentImageURL = "https://i.ytimg.com/vi/VY-VQ0KvhgU/maxresdefault.jpg"
        contentTitle = "Learn Something New Every Day!"
        contentID = -1

    elif homepageLinkID == 2:
        contentURL = "https://www.youtube.com/watch?v=ZlU8ujPraOk"
        contentImageURL = "https://img.youtube.com/vi/ZlU8ujPraOk/1.jpg"
        contentTitle = "Example 2 Title"
        contentID = -2

    elif homepageLinkID == 3:
        contentURL = "https://www.youtube.com/watch?v=ZlU8ujPraOk"
        contentImageURL = "https://img.youtube.com/vi/ZlU8ujPraOk/2.jpg"
        contentTitle = "Example 3 Title"
        contentID = -3

    print(contentID, "what content id is being set?")
    publicRatingQuery = db.session.query(ReviewsModel.id, ReviewsModel.rateValue, ReviewsModel.reviewsOn_contentID).filter(ReviewsModel.reviewsOn_contentID == contentID).order_by(ReviewsModel.id.desc()).all()

    ratingList = []
    for item in publicRatingQuery:
        ratingList.append(item[1])

    print(ratingList, 'looking at rating list')
    publicRateCount = len(ratingList)
    print(publicRateCount)
    publicRate = sum(ratingList) / publicRateCount
    rating = "{0:0.1f}".format(publicRate)
    print(rating)

    return render_template("/publicThoughtsON.html", contentID=contentID, contentURL=contentURL, contentImageURL=contentImageURL, contentTitle=contentTitle, rating=rating)


@app.route('/content/thoughtson/<int:thoughtID>', methods=['GET', 'POST'])
@login_required
def show_thought(thoughtID):
    thoughtson = getThought(thoughtID, current_user)
    if thoughtson:
        thoughtData = thoughtson
        # print(thoughtData[0], thoughtData[1], thoughtData[2], thoughtData[3])
        fbName = thoughtData[0]
        userID = thoughtData[1]
        isMessengerBrowser = thoughtData[2]
        thoughtContentID = thoughtData[3]
        reviewsForContent = thoughtData[4]
        print(fbName, userID, isMessengerBrowser, 'from views')
        counter = 0
        for item in thoughtContentID:
            print(item, 'qThoughtContent from views')
            print(item.average, 'qThoughtContent id? from views')
            print(item.titleContent, 'qThoughtContent id? from views')
            print(item.cID, 'qThoughtContent id? from views')
            # print(item.contentURL, 'qDistinctContent id?')
            # print(item.contentiURL, 'qDistinctContent id?')
            counter +=1
        print(counter, "total count of ratings from views")



    else:
        thoughtData = "Building ... work in progress"

    return render_template("/thoughtson.html", thoughtContentID=thoughtContentID, reviewsForContent=reviewsForContent, fbName=fbName, userID=userID )


@app.route('/content/reviewson/<int:thoughtID>', methods=['GET', 'POST'])
def show_review(thoughtID):
    # reviewsOn = getThought(thoughtID, current_user)
    thoughtContentID = thoughtID
    print(thoughtContentID, "this should be the content id")
    reviewContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.id == thoughtContentID).order_by(ContentModel.id.desc())
    if reviewContentQuery:
        thoughtData = reviewContentQuery
        print(thoughtData, "thought data")
        # print(thoughtData[0], thoughtData[1], thoughtData[2], thoughtData[3])
        # thoughtContentID = thoughtData[3]
        fbName = request.args.get('fbName', type = str)
        userID = request.args.get('userID', type = int)
        reviewer = request.args.get('reviewer', type = int)
        print(fbName, userID, reviewer, 'from views')
    else:
        thoughtData = "Building ... work in progress"

    return render_template("/reviewson.html", thoughtContentID=thoughtData, qbertFBName=fbName, userID=userID, reviewer=reviewer )


@app.route('/content/reviews', methods=['GET', 'POST'])
@app.route('/content/reviews/<int:page>', methods=['GET', 'POST'])
@login_required
def qreviews(page=1):
    myRecentReviews = getRecentReviews(current_user)
    print(myRecentReviews, "from view")
    userContent = myRecentReviews.paginate(page, per_page, False)
    return render_template("reviews_feed.html", userContent = userContent)

@app.route('/content/reviews/filter/<string:filter_type>', methods=['GET', 'POST'])
@app.route('/content/reviews/filter/<string:filter_type>/<int:page>', methods=['GET', 'POST'])
@login_required
def qreviewsFilter(filter_type, page=1):
    myFilterReviews = getFilterReviews(current_user, filter_type)
    print(myFilterReviews, "from view")
    userContent = myFilterReviews.paginate(page, per_page, False)
    return render_template("reviews_feed.html", userContent = userContent)


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
