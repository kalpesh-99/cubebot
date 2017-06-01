#the start of cubebot
import os

from flask import Flask, request, render_template, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import json, requests, re

from db import db

from api_resources.trigger import Trigger, TriggerList
from api_resources.fbwebhooks import FBWebhook, sendBotMessage
from api_resources.getstarted import GetStarted, Menu, Greeting, ChatExtension, Whitelist
from .model import TriggerModel, ContentModel

app = Flask(__name__)

api = Api(app)
# creating the app and configuring db and enabling api



@app.route('/') #root directory - homepage of cubebot
def home():
    return render_template("index.html", app_name = "CubeBot")


@app.route('/triggers') # cubebot triggers webview
def triggers():
	triggerNames = db.session.query(TriggerModel.name).all()
	# this becomes a list of tuples [('a',), ('b',)] for each 'name' value in the TriggerModel triggers table

	triggerWords = [', '.join(map(str, x)) for x in triggerNames]
	# now we've coverted every item in the tuples to string and joined them to create a list

	return render_template("/triggers.html", context=triggerWords)

@app.route('/library') # cubebot library webview
def library():
    # library = db.session.query(ContentModel.title).all()
    # # this becomes a list of tuples [('a',), ('b',)] for each 'name' value in the TriggerModel triggers table
    # libraryURLs = db.session.query(ContentModel.url).all()
    # libraryiDs = db.session.query(ContentModel.id).all()
    #
    # libraryFileList = [', '.join(map(str, x)) for x in library][::-1]
    # libraryURLsList = [', '.join(map(str, x)) for x in libraryURLs][::-1]
    # context = dict(zip(libraryFileList, libraryURLsList))
    # print(type(context))
    # # now we've coverted every item in the tuples to string and joined them to create a list
    # libraryFileiDs = [', '.join(map(str, x)) for x in libraryiDs][::-1]
    # print(libraryFileiDs)

    # x = 1
    #
    # print(len((ContentModel.find_by_id(x))))
    # print(type(ContentModel.find_by_id(x)))

    fileValue = db.session.query(ContentModel.id, ContentModel.title, ContentModel.url).order_by(ContentModel.id.desc()).limit(5)
    # print(type(fileValue)) #this is a flask_sqlalchemy.BaseQuery

    results = fileValue[::1] #turns into a list
    # print(results)


    return render_template("/library.html", context=results)

## since we send the context data, we shoud be able to complete the file share via MessengerExtensions from JS on webview;
## dont see why we should call the server/db again just to send from server.
## instead, send a tracker back to the server to keep the sharinging event history etc.



@app.route('/_load_ajax', methods=["GET", "POST"]) # this is to handle internal post requests
def load_ajax():

    if request.method == "POST":
        libraryShareContent = request.get_json()
        print(libraryShareContent)

        if libraryShareContent['file'] == 2:
            print(type(libraryShareContent))
        else:
            print("I didn't get the right number back")

        # sender_id = 1347495131982426
        # sender_id = 1749436805074216
        # sendBotMessage(libraryShareContent, sender_id)
        # print(request.json['attachment'])
        return jsonify(libraryShareContent)


#connecting the resource to the api

api.add_resource(Trigger, '/api/trigger/<string:name>') # http://127.0.0.1:5000/student/Rolf
api.add_resource(TriggerList, '/api/triggers')
api.add_resource(FBWebhook, '/api/fbwebhook/')
api.add_resource(Greeting, '/api/fbsetup/')
api.add_resource(GetStarted, '/api/fbsetup/getstarted')
api.add_resource(Menu, '/api/fbsetup/menu')
api.add_resource(ChatExtension, '/api/fbsetup/chatext')
api.add_resource(Whitelist, '/api/fbsetup/whitelist')






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
