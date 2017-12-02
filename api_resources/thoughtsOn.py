from flask import request, render_template, session
from sqlalchemy import func
from db import db
# from flask_restful import Resource, reqparse
# import json, requests, re
from cubebot_site.model import ContentModel, ReviewsModel
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

# ok lets create our query to get the following: content.id, content.title, content.url, contentiURL, reviews.rateValue, reviews.average, thread_id's
    if userID:
        qThoughtContent = db.session.query(ReviewsModel.id.label('reviewNumber'), ReviewsModel.rateValue, ReviewsModel.reviewsOn_contentID, func.round(func.avg(ReviewsModel.rateValue),1).label('average'), func.count(ReviewsModel.rateValue), func.sum(ReviewsModel.rateValue), ContentModel.id.label('cID'), ContentModel.title.label('titleContent'), ContentModel.category, ContentModel.url.label('contentURL'), ContentModel.urlImage.label('contentiURL'),ContentModel.source).join(ContentModel).filter(ContentModel.id == thought).order_by(ReviewsModel.id.desc())
        if qThoughtContent:
            counter = 0
            for item in qThoughtContent:
                print(item, 'qThoughtContent')
                print(item.average, 'qThoughtContent id?')
                print(item.titleContent, 'qThoughtContent id?')
                print(item.cID, 'qThoughtContent id?')
                # print(item.contentURL, 'qDistinctContent id?')
                # print(item.contentiURL, 'qDistinctContent id?')
                counter +=1
            print(counter, "total count of ratings")

            qEachReviewForThought = db.session.query(ReviewsModel.id, ReviewsModel.rateValue, ReviewsModel.reviewsOn_threadID, ReviewsModel.reviewsOn_contentID).filter(ReviewsModel.reviewsOn_contentID == thought).order_by(ReviewsModel.rateValue.desc()).order_by(ReviewsModel.id.desc())
            if qEachReviewForThought:
                counter2 = 0
                for item in qEachReviewForThought:
                    print(item, 'qEachReviewForThought')
                    print(item.id, 'qEachReviewForThought id?')
                    print(item.rateValue, 'qEachReviewForThought value?')
                    print(item.reviewsOn_threadID, 'qEachReviewForThought thread/friend?')
                    # print(item.contentURL, 'qDistinctContent id?')
                    # print(item.contentiURL, 'qDistinctContent id?')
                    counter2 +=1
                print(counter2, "total count of ratings2")


    # eachReviewForContent = qEachReviewForThought.paginate(page, per_page, False)
    eachReviewForContent = qEachReviewForThought
    contentReview = qThoughtContent


    return FBname, userID, setMessengerContextDetails, contentReview, eachReviewForContent
