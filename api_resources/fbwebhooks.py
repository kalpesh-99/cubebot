from flask import request, render_template, session
from flask_restful import Resource, reqparse
import json, requests, re
from cubebot_site.model import TriggerModel, ContentModel

from api_resources import FB_PAGE_TOKEN, FB_AccountLink_Code
from .getLinkData import getLinkImage
from .getAttachment import getAttachment

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
                                receivedTextAttachment(textAttachment, sender_id)

                            else:
                                messageType = 1

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

        return 200

def getUserDetails(sender_id):
    ## might want to create a user Class to handle this, so we can call members of the user class (first_name etc) in other areas of the code
    user_details_url = "https://graph.facebook.com/v2.9/%s"%sender_id
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':FB_PAGE_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json() #this calls FB api to get user data; json format
    user_first_name = user_details['first_name']
    user_profile_pic = user_details['profile_pic']
    # user_profile_id = user_details['id']
    # print(user_profile_id, 'from get user details')
    print(user_profile_pic, 'should be profile pic url?')

    return user_first_name, user_profile_pic


def receivedPostback(postbackPayload, sender_id):
    # print(sender_id)
    payload = postbackPayload
    # print(payload)
    # print(sender_id)
    if payload == "GET_STARTED_PAYLOAD": ## we probably shoudn't use +getUserDetails(sender_id)[0] below ##
        msg = "Welcome " +getUserDetails(sender_id)[0] + "! When you share files from your Library, I'll keep them organized across Messenger."
        response_msg = {
            "attachment":{
              "type":"template",
              "payload":{
                "template_type":"button",
                "text":msg,
                "buttons":[
                  {
                    "type":"account_link",
                    "url":"https://cdb93c00.ngrok.io/login"
                  }
                ]
              }
            }
        }
    elif payload == "linked":
        msg = "Great your account has been {0}!".format(payload)
        response_msg = {"text": msg}

    else:
        msg = "I got the following postback: " +payload
        response_msg = {"text": msg}
    # print(responseItem)
    sendBotMessage(response_msg, sender_id)

def receivedTextAttachment(textAttachment, sender_id):
    print(textAttachment)
    print(type(textAttachment))
    for text in textAttachment:
        for key in text:
            if key == 'url':
                textURL = text['url']
                print(textURL)
                imgURL = getHTML(textURL)
                print(imgURL)
                print(sender_id)
                print("does text url and sender_id appear above?")
                urlCategory = "link"
                urlContent = ContentModel(text['title'], urlCategory, textURL, imgURL, sender_id)
                try:
                	urlContent.save_to_db() ## cleaner code, saving the object to the DB using SQLAlchemy
                except:
                	return {"message": "An error occured inserting the item."}, 500 #internal server error
    # textURL = textAttachment['url']
    # print(textURL)

def getHTML(self):
    imgURL = getLinkImage(self)
    return imgURL

def someFxForLinks(self):
    # linkTitle = data['entry','time']
    print(self)
    # pass

def receivedAttachment(attachmentList, attachmentText, sender_id):
    for text in attachmentList:
        for key in text:
            if key == 'url':
                textURL = text['url']
                print(textURL)
                imgURL = getHTML(textURL)
                print(imgURL)
                print(sender_id)
                print("does text url and sender_id appear above?")
                urlCategory = "link"
                urlContent = ContentModel(text['title'], urlCategory, textURL, imgURL, sender_id)
                try:
                	urlContent.save_to_db() ## cleaner code, saving the object to the DB using SQLAlchemy
                except:
                	return {"message": "An error occured inserting the item."}, 500 #internal server error

    response_msg = {"text":attachmentText}
    sendBotMessage(response_msg, sender_id)

def receivedMessage(messaging_text, sender_id, messageType):
    # print(sender_id)

    incomingMessage = messaging_text

    #this could be it's own function: to check message elements for keywords/triggers
    messageList = re.sub(r"[^a-zA-Z0-9\s]",' ',incomingMessage).lower().split()
    print(messageList)
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


    user = getUserDetails(sender_id)
    print(user)

    # user_details_url = "https://graph.facebook.com/v2.9/%s"%sender_id
    # user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':FB_PAGE_TOKEN}
    # user_details = requests.get(user_details_url, user_details_params).json() #this calls FB api to get user data; json format

    # replyMessage = 'Hi '+user_details['first_name'] +'! Looks like you said... ' + incomingMessage
    print(messageType)

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
    # print(responseItem)
    sendBotMessage(response_msg, sender_id)



def sendBotMessage(response_msg, sender_id):

    post_message_url = 'https://graph.facebook.com/v2.9/me/messages?access_token='+FB_PAGE_TOKEN
    response_data = json.dumps({"recipient":{"id":sender_id}, "message":response_msg})
    print(response_data)
    print(type(response_data))

    return requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_data)
            # print(botMessage.json())
