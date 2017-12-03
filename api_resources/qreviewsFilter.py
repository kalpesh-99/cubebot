from flask import request, render_template, session
from sqlalchemy import func
from db import db
from cubebot_site.model import ContentModel, ReviewsModel, UserModel

per_page = 9

def getFilterReviews(current_user, filter_type, page=1):
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
    # print(userID, 'this is the db id from users table')
    FBname = current_user.FBname
    # print(FBname, 'this is the db FB Name from users table')
    userFBPSID = current_user.FBuserPSID
    # print(userFBPSID, 'this is the db FB Name from users table')

    if userID:
        # print(userID, "if userID true statement test")
        contentFilter = filter_type
        print(contentFilter, 'filter for reviews')

        # qDistinctContent = db.session.query(ReviewsModel.id.label('reviewNumber'), ReviewsModel.rateValue, ReviewsModel.reviewsOn_contentID, func.round(func.avg(ReviewsModel.rateValue),1).label('average'), func.count(ReviewsModel.rateValue), func.sum(ReviewsModel.rateValue), ContentModel.id.label('cID'), ContentModel.title.label('titleContent'), ContentModel.category, ContentModel.url.label('contentURL'), ContentModel.urlImage.label('contentiURL'), ContentModel.source).join(ContentModel).filter(ReviewsModel.reviewsOn_userID == userID).filter(ContentModel.category == contentFilter).group_by(ReviewsModel.reviewsOn_contentID).order_by(func.avg(ReviewsModel.rateValue).desc()).order_by(ReviewsModel.id.desc())

        qDistinctContent = db.session.query(ReviewsModel.id.label('reviewNumber'), ReviewsModel.rateValue, ReviewsModel.reviewsOn_contentID, func.round(func.avg(ReviewsModel.rateValue),1).label('average'), func.count(ReviewsModel.rateValue), func.sum(ReviewsModel.rateValue), ContentModel.id.label('cID'), ContentModel.title.label('titleContent'), ContentModel.category, ContentModel.url.label('contentURL'), ContentModel.urlImage.label('contentiURL'), ContentModel.source).join(ContentModel).filter(ReviewsModel.reviewsOn_userID == userID).filter(ContentModel.category == contentFilter).group_by(ReviewsModel.id, ReviewsModel.reviewsOn_contentID, ContentModel.id).order_by(func.avg(ReviewsModel.rateValue).desc()).order_by(ReviewsModel.id.desc())

        counter2 = 0
        for item in qDistinctContent:
            print(item, 'qDistinctContent')
            # print(item.average, 'qDistinctContent id?')
            # print(item.titleContent, 'qDistinctContent id?')
            print(item.cID, 'qDistinctContent id?')
            # print(item.contentURL, 'qDistinctContent id?')
            # print(item.contentiURL, 'qDistinctContent id?')
            counter2 +=1
        print(counter2, "total count of ratings")
            #What can we do to get unique content.id sorted by review.id with avg raview.rateValue

        recentReviewsData = qDistinctContent #temp, returning the query object so we can paginate returns... lists can't be paginated


    return recentReviewsData
