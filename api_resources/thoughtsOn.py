from flask import request, render_template, session
from db import db
# from flask_restful import Resource, reqparse
# import json, requests, re
from cubebot_site.model import ContentModel
#
# from api_resources import FB_PAGE_TOKEN, FB_AccountLink_Code
# from .getLinkData import getLinkImage
# from .getAttachment import getAttachment
# from cubebot_site.model import UserModel
per_page = 9


def getThought(thoughtID, current_user, page=1):



    view = request.headers.get('User-Agent')
    print(view, 'looking for browser header details')
    print(type(view))
    if "Messenger" in view:
        print("looks like browser = Messenger")
        setMessengerContextDetails = True
    else:
        print("browser NOT in Messenger")
        setMessengerContextDetails = False


    thought = thoughtID
    print(thoughtID, "this should be the thought id")
    print(thought, "this should be the thought")

    userID = current_user.id
    print(userID, 'this is the db id from users table')
    FBname = current_user.FBname
    print(FBname, 'this is the db FB Name from users table')

    userFBPSID = current_user.FBuserPSID
    print(userFBPSID, 'this is the db FB Name from users table')


    if FBname == "":
         print("no name will need to use user id to query db for content")
         getContentIDquery = db.session.query(ContentModel.id).filter(ContentModel.user_id == userID).order_by(ContentModel.id.desc())
         userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.user_id == current_user.id).order_by(ContentModel.id.desc())
    else:
        getContentIDquery = db.session.query(ContentModel.id).filter(ContentModel.user_id == userFBPSID).order_by(ContentModel.id.desc())
        userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.user_id == current_user.FBuserPSID).order_by(ContentModel.id.desc())
        # userFilteredContentQuery = userContentQuery.filter(ContentModel.category == category).paginate(page, per_page, False)
    #
    userContentIdList = getContentIDquery[0]
    print(userContentIdList, "is this user content id list?")

    userThoughtContentID = userContentIdList[0] ## select which content.id we want to use for this thoughts, in this case the most recent content
    print(userThoughtContentID, "is this user thought content id ")

    userThoughtContentQuery = userContentQuery.filter(ContentModel.id == userThoughtContentID).paginate(page, per_page, False)

    if userThoughtContentQuery:
        print(userThoughtContentQuery, "this should be the filter content object")


    #
    #
    #     return render_template("/filterLibrary.html", FBChatCount=category, threadContent=userFilteredContentQuery, inMessenger=setMessengerContextDetails)


    return FBname, userID, setMessengerContextDetails, userThoughtContentQuery
