from flask import request, render_template, redirect, url_for
from flask_restful import Resource, reqparse
import json, requests, re
from cubebot_site.model import TriggerModel, ContentModel, UserModel
from api_resources import FB_PAGE_TOKEN

from db import db
from flask_login import login_user

## This was for FB SDK using JS method ... we had to build manual login flow to handle mobile browsers/webviews in app
## I'll leave this in for refrence purposes for now

class FBLogin(Resource):
    def get(self):
        # hubMode = request.args.get('hub.mode')
        # hubToken = request.args.get('hub.verify_token')
        # hubChallenge = request.args.get('hub.challenge')
        #
        # if hubMode == "subscribe" and hubToken == verify_token:
        #     return int(hubChallenge), 200 ## note hubChallenge is really string, FB was looking for integer
        # return "Failed validation.", 403
        return("get call")


    def post(self):
        # handle the post json object, that contains userID and accessToken
        # want to check userID vs system, and accept newUser
        data = request.get_json()
        print(data)

        if data['userID']:
            userID = data['userID']
            print(userID +'data_userID')
            accessToken = data['accessToken']
            print(accessToken +'data_accessToken')

            FBuserID_Check = UserModel.find_by_FBuserID(userID)
            if FBuserID_Check:
                print(FBuserID_Check)
                print('if FBuserID_Check')
                print(FBuserID_Check.FBAccessToken)
                print('if FBuserID_Check.FBAccessToken')
                FBuserID_Check.FBAccessToken = accessToken #This is setting the new access token to the original FBuserID
                print(accessToken)
                FBuserID_Check.save_to_db() #This is saves the new access token to the original FBuserID
                login_user(FBuserID_Check, remember=True)
                print("post login")

            else:
                newUser = UserModel(username=None, email=None, password=None, FBuserID=userID, FBAccessToken=accessToken)
                newUser.save_to_db()
                login_user(newUser)
            return 11



        # return("POST call")
