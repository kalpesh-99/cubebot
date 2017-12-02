from flask import request, render_template, session
from flask_restful import Resource, reqparse
import json, requests, re
from cubebot_site.model import TriggerModel, ContentModel

from api_resources import FB_PAGE_TOKEN, FB_AccountLink_Code
from .getLinkData import getLinkImage
from .getAttachment import getAttachment
from cubebot_site.model import UserModel

from db import db

def triggers():
    triggerNames = db.session.query(TriggerModel.name).all()
    # this becomes a list of tuples [('a',), ('b',)] for each 'name' value in the TriggerModel triggers table

    triggerWords = [', '.join(map(str, x)) for x in triggerNames]
    # now we've coverted every item in the tuples to string and joined them to create a list
    return triggerWords

verify_token = "cubebot_testing"
# FB_PAGE_TOKEN = "" need to create config file still



class FBWebhook(Resource): # so Item iherrits from resrouce

    def get(self):
        hubMode = request.args.get('hub.mode')
        hubToken = request.args.get('hub.verify_token')
        hubChallenge = request.args.get('hub.challenge')

        if hubMode == "subscribe" and hubToken == verify_token:
            return int(hubChallenge), 200 ## note hubChallenge is really string, FB was looking for integer
        return "Failed validation.", 403


    def post(self):

        data = request.get_json()  #data is class dict
        # json_data = json.dumps(data, sort_keys=True) #json_data is class str
        # print(json.dumps(data, sort_keys=True))
        # print(type(json_data))

        if data['object'] == 'page':
            print(data)
            print(type(data))

            for entry in data['entry']:
                entry_id = entry['id']
                entry_time = entry['time']
                try:
                    for messaging_event in entry['messaging']:
                        sender_id = messaging_event['sender']['id']
                        recepient_id = messaging_event['recipient']['id']

                        if messaging_event.get('message'):
                            message_dict = messaging_event.get('message')
                            # print(message_dict)
                            # print(type(message_dict))

                            if message_dict.get('text'):
                                # messageText = message_dict.get('text')
                                if message_dict.get('attachments'):
                                    messageType = 2
                                    print("text with attachment it seems")
                                    textAttachment = message_dict.get('attachments')
                                    ReceivedTextAtt.receivedTextAttachment(textAttachment, sender_id, messageType) #added ReceivedTextAtt. as resource

                                else:
                                    messageType = 1
                                ## I think these 2 lines below should be part of the else block
                                    messageText = message_dict.get('text')
                                    receivedMessage(messageText, sender_id, messageType)

                            elif message_dict.get('attachments'):
                                print("not text, looks like an attachment")
                                attachmentList = message_dict.get('attachments')

                                attachmentText = getAttachment(attachmentList)
                                receivedAttachment(attachmentList, attachmentText, sender_id)
                                # break


                        elif messaging_event.get('postback'):
                            postback_dict = messaging_event.get('postback')
                            postbackPayload = postback_dict.get('payload')
                            print(postback_dict)
                            print(postbackPayload)
                            receivedPostback(postbackPayload, sender_id)

                        elif messaging_event.get('account_linking'):
                            account_linking_dict = messaging_event.get('account_linking')
                            print(account_linking_dict, 'checking content for account_linking')
                            if account_linking_dict['authorization_code'] == FB_AccountLink_Code:
                                print(account_linking_dict['authorization_code'], 'looking for auth code' )
                                postbackPayload = account_linking_dict.get('status')
                                print(postbackPayload, 'looing for status here')
                                receivedPostback(postbackPayload, sender_id)
                except:
                    pass

                try:
                    for messaging_event in entry['changes']:
                        thread_id = messaging_event['value']['thread_id']
                        print(thread_id, "is this the conversation Data?")
                except:
                    pass

        return 200

def getUserDetails(sender_id):
    ## might want to create a user Class to handle this, so we can call members of the user class (first_name etc) in other areas of the code
    user_details_url = "https://graph.facebook.com/v2.9/%s"%sender_id
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':FB_PAGE_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json() #this calls FB api to get user data; json format
    print(user_details, "looking for get user details json data")
    user_first_name = user_details['first_name']
    user_profile_pic = user_details['profile_pic']
    # user_profile_id = user_details['id']
    # print(user_profile_id, 'from get user details')
    print(user_profile_pic, 'should be profile pic url?')
    checkUser = UserModel.find_by_FBuserPSID(FBuserPSID=sender_id)
    if checkUser:
        print(checkUser.id, "OK, does this work to get user id from getUserDetails fx?")
        checkUserID = checkUser.id
    else:
        checkUserID = 99
        print(checkUserID, "case where no psid in userModel yet")

    print(user_first_name, user_profile_pic, checkUserID)
    return user_first_name, user_profile_pic, checkUserID

def getSharedThreadIDdetails(sender_id, access_token, thread_id):
    FBnode = thread_id
    accessToken = access_token
    fbUserID = sender_id

    getSharedTIDurl = "https://graph.facebook.com/v2.6/{0}?access_token={1}&tid={2}".format(fbUserID, accessToken, FBnode)
    getSharedTIDdata = requests.get(getSharedTIDurl)
    sharedTIDdata = getSharedTIDdata.json()
    print(sharedTIDdata, 'looking for shared tid json data')

    # user_details_url = "https://graph.facebook.com/v2.9/%s"%sender_id
    # user_details_params = {'fields':'id', 'access_token':FB_PAGE_TOKEN}
    # user_details = requests.get(user_details_url, user_details_params).json() #this calls FB api to get user data; json format
    # print(user_details, "looking for get user details json data")

    # user_first_name = user_details['first_name']
    # user_profile_pic = user_details['profile_pic']
    # user_profile_id = user_details['id']
    # print(user_profile_id, 'from get user details')
    # print(user_profile_pic, 'should be profile pic url?')
    sharedToFirstName = "Yoda"

    return sharedToFirstName

def receivedPostback(postbackPayload, sender_id):
    # print(sender_id)
    payload = postbackPayload
    print(payload, "from receivedPostback")
    print(sender_id, "from receivedPostback")
    name = getUserDetails(sender_id)[0]
    print(name, "from receivedPostback after making getUserDetails call")

    if payload == "GET_STARTED_PAYLOAD": ## we probably shoudn't use +getUserDetails(sender_id)[0] below ##
        msg = "Welcome " +name + "! When you share files from your Library, I'll help you get feedback using a simple 5-star rating system. Login to get started!"
        response_msg = {
            "attachment":{
              "type":"template",
              "payload":{
                "template_type":"button",
                "text":msg,
                "buttons":[
                  {
                    "type":"account_link",
                    "url":"https://4425ff68.ngrok.io/login"
                  }
                ]
              }
            }
        }
        print(response_msg, 'from payload if')

    elif payload == "linked":
        msg = "Great your account has been {0}!".format(payload)
        response_msg = {"text": msg}

    else:
        msg = "I got the following postback: " +payload
        response_msg = {"text": msg}

    print(response_msg, "this is the responseItem just before sendBotMessage from receivedPostback")
    sendBotMessage(response_msg, sender_id)

class ReceivedTextAtt(Resource): # Trying api to create content for user
    parser = reqparse.RequestParser()  #this ensures we're only dealing with the price, anything else that comes in gets erased;
    parser.add_argument('link',
        type=str,
        required=True,
        help="The category field cannont be left blank!"
    )

    def post(self, username):
        data = ReceivedTextAtt.parser.parse_args()
        print(data, 'looking for api content data')
        print(username, 'looking for user from api call')
        checkUser = UserModel.find_by_username(username=username) #at some point create a function for this used in views.py too
        if checkUser is not None:
            print(checkUser, 'looking for db check data')
            user_id = checkUser.id
            print(user_id, 'looking for user id number ')
            content = data['link']
            print(content, 'looking for content url post username')
            imgURL = getHTML(content, 'api')
            print(imgURL, 'looking for img url')
            urlCategory = "link"
            ## note: link domain is the 4th item passed in from getHTML function - not implemented here yet
            urlContent = ContentModel("content title", urlCategory, content, imgURL, "source", user_id)
            try:
                urlContent.save_to_db() ## cleaner code, saving the object to the DB using SQLAlchemy
            except:
                return {"message": "An error occured inserting the item."}, 500 #internal server error



        else:
            print("didn't find a match")
        ## now check if user id is in db, (don't bother authenticating for now?)
        ## actually need Username as this is from a web call for users signed in by email
        ## take user and add content




    def receivedTextAttachment(textAttachment, sender_id, messageType):
        print(textAttachment)
        print(type(textAttachment))
        for text in textAttachment:
            for key in text:
                if key == 'title':
                    linkTitle = text['title']
                    print(linkTitle, "THIS IS THE LINK FROM KEY TITLE")

                if key == 'url':
                    textURL = text['url']
                    print(textURL)
                    textURLData = getHTML(textURL, 'app')
                    print(textURLData, 'should be 3 tuple items from getHTML function')
                    imgURL = textURLData[0]
                    checkLinkTitle = textURLData[1]
                    linkURL = textURLData[2]
                    linkType = textURLData[3]
                    linkDomain = textURLData[4]
                    ## to catch case where link has generic title
                    if checkLinkTitle != "generic":
                        print("NOT Test for GENERIC TITLE")
                        linkTitle = checkLinkTitle



                    # print("does text url and sender_id appear above?")
                    if linkType:
                        urlCategory = linkType
                    else:
                        urlCategory = "link"

                    print(imgURL, linkTitle, urlCategory, linkURL, linkDomain, sender_id, " link info before saving to db from receivedTextAttachment")
                    checkUser = getUserDetails(sender_id)
                    checkUserID = checkUser[2]  ## should revisit returned data format from getUserDetails fx
                    print(checkUserID, "should be user id from receivedTextAttachment fx")

                    # urlContent = ContentModel(text['title'], urlCategory, textURL, imgURL, sender_id)
                    urlContent = ContentModel(linkTitle, urlCategory, linkURL, imgURL, linkDomain, checkUserID)
                    try:
                        urlContent.save_to_db() ## cleaner code, saving the object to the DB using SQLAlchemy
                        saveCheck = True
                    except:
                        saveCheck = False
                        return {"message": "An error occured inserting the item."}, 500 #internal server error
        # textURL = textAttachment['url']
        # print(textURL)
                    if saveCheck == True:
                        messageText = getAttachment(textAttachment)
                        receivedMessage(messageText, sender_id, messageType)





def getHTML(self, caller):
    linkData = getLinkImage(self, caller)
    print(linkData, "looking for 3 values being returned")
    # imgURL = getLinkImage(self, caller)
    imgURL = linkData[0]
    linkTitle = linkData[1]
    linkURL = linkData[2]
    linkType = linkData[3]
    linkDomain = linkData[4]
    print(imgURL, "looking for link data item 0, should be img url")
    print(self, 'post get Link Image function')
    whoCalledit = caller
    print(whoCalledit, 'who called it?')
    print(imgURL, 'img url or none?')

    return imgURL, linkTitle, linkURL, linkType, linkDomain

def someFxForLinks(self):
    # linkTitle = data['entry','time']
    print(self)
    # pass

def receivedAttachment(attachmentList, attachmentText, sender_id):
    for text in attachmentList:
        for key in text:
            if key == 'title':
                linkTitle = text['title']
                print(linkTitle, "THIS IS THE receivedAttachment TITLE FROM KEY TITLE")

            if key == 'url':
                textURL = text['url']
                print(textURL)
                textURLData = getHTML(textURL, 'app')
                print(textURLData)
                print(sender_id)
                print("does text url data and sender_id appear above?")
                imgURL = textURLData[0]
                checkLinkTitle = textURLData[1]
                linkURL = textURLData[2]
                linkType = textURLData[3]
                linkDomain = textURLData[4]

                if checkLinkTitle != "generic":
                    print("NOT Test for GENERIC TITLE")
                    linkTitle = checkLinkTitle

                if linkType:
                    urlCategory = linkType
                else:
                    urlCategory = "link"

                print(imgURL, linkTitle, urlCategory, linkURL, linkDomain, sender_id, " link info before saving to db from receivedAttachment")
                checkUser = getUserDetails(sender_id)
                checkUserID = checkUser[2]
                print(checkUserID, "should be user id from receivedAttachment fx")
                urlContent = ContentModel(linkTitle, urlCategory, linkURL, imgURL, linkDomain, checkUserID) ## might consider saving content with user.id from db instead of sender id
                try:
                    urlContent.save_to_db() ## cleaner code, saving the object to the DB using SQLAlchemy
                    saveCheck = True
                    print("saved - from receivedAttachment")
                except:
                    saveCheck = False
                    print("not saved - from receivedAttachment")
                    return {"message": "An error occured inserting the item."}, 500 #internal server error

                if saveCheck == True:
                    response_msg = {"text":attachmentText} #this response message could be better.. but does the job for now.
                    sendBotMessage(response_msg, sender_id)

            if key == 'type':
                attachmentType = text['type']
                attachmentURL = text['payload']['url'] ## at some point streamline this with getAttachment.py
                print(attachmentType, "from def receivedMessage")
                print(attachmentURL, "from def receivedMessage")
                checkUser = getUserDetails(sender_id)
                checkUserID = checkUser[2]
                print(checkUserID, "should be user id from receivedAttachment fx")
                imageContent = ContentModel("Messenger Pic", attachmentType, attachmentURL, attachmentURL, "Messenger", checkUserID)
                try:
                	imageContent.save_to_db() ## cleaner code, saving the object to the DB using SQLAlchemy
                except:
                	return {"message": "An error occured inserting the item."}, 500 #internal server error

                response_msg = {"text":attachmentText} #this response message could be better.. but does the job for now.
                sendBotMessage(response_msg, sender_id)

def receivedMessage(messaging_text, sender_id, messageType):
    # print(sender_id)

    incomingMessage = messaging_text

    #this could be it's own function: to check message elements for keywords/triggers
    messageList = re.sub(r"[^a-zA-Z0-9\s]",' ',incomingMessage).lower().split()
    print(messageList, "from receivedMessage")
    triggersList = triggers() #["pic", "Pic"]
    for message in messageList:
        if message == 'https':
            gotLink = "link detected"
            someFxForLinks(gotLink)

        if message in triggersList:
            # responseItem = "image"
            # break
            responseItem = "image"

            break
        responseItem = incomingMessage

    print("just b4 getUserDetails from receivedMessage")
    user = getUserDetails(sender_id)
    print(user, "userDetails post getUserDetails from receivedMessage")

    # user_details_url = "https://graph.facebook.com/v2.9/%s"%sender_id
    # user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':FB_PAGE_TOKEN}
    # user_details = requests.get(user_details_url, user_details_params).json() #this calls FB api to get user data; json format

    # replyMessage = 'Hi '+user_details['first_name'] +'! Looks like you said... ' + incomingMessage
    print(messageType, "just b4 the messageType if statement")

    if messageType == 2:
        replyMessage = "Got it " +user[0] + "! It's been saved to your Library."
    else:
        # replyMessage = 'Hi '+getUserDetails(sender_id)[0] +'! Looks like you said... ' + incomingMessage
        replyMessage = 'Hi '+user[0] +'! Looks like you said... ' + incomingMessage

    # profileUrl = getUserDetails(sender_id)[1]
    profileUrl = user[1]

    if responseItem == 'image':
        print("got image")
        response_msg = {"attachment":{"type":"image", "payload":{"url":profileUrl}}}
    else:
        print("got text")
        response_msg = {"text":replyMessage}
    print(responseItem, "just before going to sendBotMessage")
    print(sender_id, "just before going to sendBotMessage")
    sendBotMessage(response_msg, sender_id)



def sendBotMessage(response_msg, sender_id):

    post_message_url = 'https://graph.facebook.com/v2.9/me/messages?access_token='+FB_PAGE_TOKEN
    response_data = json.dumps({"recipient":{"id":sender_id}, "message":response_msg})
    print(response_data, "from sendBotMessage fx")
    print(type(response_data))

    return requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_data)
            # print(botMessage.json())
