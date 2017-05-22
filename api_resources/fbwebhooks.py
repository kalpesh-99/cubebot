from flask import request, render_template
from flask_restful import Resource, reqparse
import json, requests, re
from cubebot_site.model import TriggerModel
from api_resources import FB_PAGE_TOKEN

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

        data = request.get_json()

        if data['object'] == 'page':
            print(data)

            for entry in data['entry']:
                entry_id = entry['id']
                entry_time = entry['time']

                for messaging_event in entry['messaging']:
                    sender_id = messaging_event['sender']['id']
                    recepient_id = messaging_event['recipient']['id']

                    # eventually will need to add logic to detect other types of messaging events

                    if messaging_event.get('message'):
                        if 'text' in messaging_event['message']:
                            messaging_text = messaging_event['message']['text'] #.encode('unicode_escape') #encode to handle emojis
                        else:
                            messaging_text = "doh, no text!"
                        receivedMessage(messaging_text, sender_id)

                    elif messaging_event.get('postback'):
                        postbackPayload = messaging_event["postback"]["payload"]
                        print(postbackPayload)
                        receivedPostback(postbackPayload, sender_id)
                        # if 'GET_STARTED_PAYLOAD' in postbackText:
                        #     receivedPostback(postbackText, sender_id)
                        #



        return 200

def receivedPostback(postbackPayload, sender_id):
    # print(sender_id)
    payload = postbackPayload
    # print(payload)
    # print(sender_id)
    msg = "Welcome buddy :)"
    response_msg = {"text": msg}
    # print(responseItem)
    sendBotMessage(response_msg, sender_id)


def receivedMessage(messaging_text, sender_id):
    # print(sender_id)
    incomingMessage = messaging_text

    #this could be it's own function: to check message elements for keywords/triggers
    messageList = re.sub(r"[^a-zA-Z0-9\s]",' ',incomingMessage).lower().split()
    print(messageList)
    triggersList = triggers() #["pic", "Pic"]
    for message in messageList:
        if message in triggersList:
            responseItem = "image"
            break
        responseItem = incomingMessage

    user_details_url = "https://graph.facebook.com/v2.9/%s"%sender_id
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':FB_PAGE_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json() #this calls FB api to get user data; json format

    replyMessage = 'Hi '+user_details['first_name'] +'! Looks like you said... ' + incomingMessage
    profileUrl = user_details['profile_pic']

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
    return requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_data)
            # print(botMessage.json())


        # if data['object'] == 'page':
        #
        #     for entry in data['entry']:
        #         entry_id = entry['id']
        #         entry_time = entry['time']
        #
        #         for messaging_event in entry['messaging']:
        #             sender_id = messaging_event['sender']['id']
        #             recepient_id = messaging_event['recipient']['id']
        #
        #             # eventually will need to add logic to detect other types of messaging events
        #
        #             if messaging_event.get('message'):
        #                 if 'text' in messaging_event['message']:
        #                     messaging_text = messaging_event['message']['text'] #.encode('unicode_escape') #encode to handle emojis
        #                 else:
        #                     messaging_text = "doh, no text!"
        #                 receivedMessage(messaging_text, sender_id)

                    # else:
