from __future__ import print_function
from cubebot_site.model import ContentModel
from db import db

def getLibraryContent(contentIDList):
    userContentForThisThread = contentIDList
    print(userContentForThisThread, "from the new getLibraryContent function")
    # userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.id.in_(contentList).order_by(ContentModel.id.desc()).limit(9)
    userContentQuery = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url, ContentModel.urlImage).filter(ContentModel.id.in_(userContentForThisThread)).order_by(ContentModel.id.desc()).limit(9)
    print(type(userContentQuery))
    print(userContentQuery,"anyting worth seeing here??")


    if userContentQuery is None:
        print("nothing to see here :-[ ")

    print(userContentQuery, 'did we get something???')
    userContent = userContentQuery[::1]
    print(userContent, 'do we see anything more???')

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

    return userContentImageUrlList, userContentTitleList, userContentUrlList, userContentIdList
