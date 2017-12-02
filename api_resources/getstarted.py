from flask import request, render_template
from flask_restful import Resource, reqparse
import json, requests, re
from api_resources import FB_PAGE_TOKEN


# FB_PAGE_TOKEN = "" need to create config file still

class GetStarted(Resource):
    def get(self):
        data_getStarted = {
            "get_started":{
                "payload":"GET_STARTED_PAYLOAD"
                }
            }
        print(data_getStarted)

        post_message_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+FB_PAGE_TOKEN
        response_Postdata = json.dumps(data_getStarted)
        print(response_Postdata)
        print(type(response_Postdata))
        requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_Postdata)

        get_started_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?fields=get_started&access_token='+FB_PAGE_TOKEN
        return requests.get(get_started_url).json()

class Greeting(Resource):
    def get(self):
        data = {
            "greeting":
                [
                    {
                      "locale":"default",
                      "text":"Helping you get feedback from trusted friends."
                    }, {
                      "locale":"en_US",
                      "text":"Hey {{user_first_name}}, I'll help you collect feedback on video and article links from trusted friends across Messenger."
                    }
                ]
            }
        post_message_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+FB_PAGE_TOKEN
        response_data = json.dumps(data)
        print(response_data, "response_data")
        print(type(response_data))
        requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_data)

        get_message_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?fields=greeting&access_token='+FB_PAGE_TOKEN
        requests.get(get_message_url).json()
        return requests.get(get_message_url).json()

class Menu(Resource):
    def get(self):
        dataMenu = {
          "persistent_menu":[
            {
              "locale":"default",
              "composer_input_disabled": False,
              "call_to_actions":[
                {
                "type":"web_url",
                "title":"qBurr Library",
                "url":"https://4425ff68.ngrok.io/library",
                "webview_height_ratio":"tall"
                },
                {
                "type":"web_url",
                "title":"qBurr Ratings",
                "url":"https://4425ff68.ngrok.io/content/reviews",
                "webview_height_ratio":"tall"
                },
                {
                  "title":"My Account",
                  "type":"nested",
                  "call_to_actions":[
                    {
                      "type":"web_url",
                      "title":"qBurr Home",
                      "url":"https://4425ff68.ngrok.io",
                      "webview_height_ratio":"full"
                    },
                    {
                      "title":"Add Sources",
                      "type":"postback",
                      "payload":"FILE_SOURCES_PAYLOAD"
                    },
                    {
                      "title":"Upgrade to PRO",
                      "type":"postback",
                      "payload":"UPGRADE_PRO_PAYLOAD"
                    }
                  ]
                }
              ]
            },
            {
              "locale":"zh_CN",
              "composer_input_disabled":False
            }
          ]

        }

        post_message_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+FB_PAGE_TOKEN
        response_data = json.dumps(dataMenu)
        print(response_data, "response_data")
        print(type(response_data))
        requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_data)

        get_menu_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?fields=persistent_menu&access_token='+FB_PAGE_TOKEN
        print("hi there")
        print(requests.get(get_menu_url).json())
        return requests.get(get_menu_url).json()

class ChatExtension(Resource):
    def get(self):
        data_ChatExt = {
            "home_url" : {
                "url": "https://4425ff68.ngrok.io/library",
                "webview_height_ratio": "tall",
                 "webview_share_button": "show",
                "in_test":True
                }
            }
        # print(data_ChatExt)

        post_message_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+FB_PAGE_TOKEN
        response_Postdata = json.dumps(data_ChatExt)
        print(response_Postdata, "response_Postdata")
        print(type(response_Postdata))
        requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_Postdata)

        get_chatext_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?fields=home_url&access_token='+FB_PAGE_TOKEN
        print("hi there")
        print(requests.get(get_chatext_url).json())
        return requests.get(get_chatext_url).json()
        # requests.get(get_started_url).json(),


class Whitelist(Resource):
    def get(self):
        data_Whitelist = {
            "whitelisted_domains":[
                "https://4425ff68.ngrok.io/library",
                "https://4425ff68.ngrok.io/content/reviews"
                ]
            }
        # print(data_ChatExt)

        post_message_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?access_token='+FB_PAGE_TOKEN
        response_Postdata = json.dumps(data_Whitelist)
        print(response_Postdata, "response postData")
        print(type(response_Postdata))
        requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_Postdata)

        get_whitelist_url = 'https://graph.facebook.com/v2.6/me/messenger_profile?fields=whitelisted_domains&access_token='+FB_PAGE_TOKEN
        print("hi there")
        print(requests.get(get_whitelist_url).json())
        return requests.get(get_whitelist_url).json()
