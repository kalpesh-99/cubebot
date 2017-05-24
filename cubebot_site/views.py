#the start of cubebot
import os

from flask import Flask, request, render_template
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

from db import db

from api_resources.trigger import Trigger, TriggerList
from api_resources.fbwebhooks import FBWebhook
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

@app.route('/library') # cubebot triggers webview
def library():
    library = db.session.query(ContentModel.title).all()
    # this becomes a list of tuples [('a',), ('b',)] for each 'name' value in the TriggerModel triggers table
    libraryURLs = db.session.query(ContentModel.url).all()


    libraryFileList = [', '.join(map(str, x)) for x in library][::-1]
    libraryURLsList = [', '.join(map(str, x)) for x in libraryURLs][::-1]
    context = dict(zip(libraryFileList, libraryURLsList))

    # now we've coverted every item in the tuples to string and joined them to create a list

    return render_template("/library.html", context=context)


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

    # Channels
        #FB Messenger Group id (stuff shared in groups)
        #FB Messenger Friend id (stuff shared between friends)
        #InputConnections
            #Dropbox
            #Gdrive
            #Cubes Library
