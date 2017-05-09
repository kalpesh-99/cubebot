#the start of cubebot
import os

from flask import Flask, request, render_template
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

from resources.trigger import Trigger, TriggerList


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')  #just means the db is in the rood code directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'kalsecretkey'
api = Api(app)
# creating the app and configuring db and enabling api
@app.before_first_request
def create_table():
	db.create_all()



@app.route('/') #root directory - homepage of cubebot
def home():

    return render_template("index.html", app_name = "CubeBot")

@app.route('/triggers') #root directory - homepage of cubebot
def triggers():

    return render_template("/triggers.html")




#connecting the resource to the api
api.add_resource(Trigger, '/api/trigger/<string:name>') # http://127.0.0.1:5000/student/Rolf
api.add_resource(TriggerList, '/api/triggers')
# api.add_resource(UserRegister, '/register')
# api.add_resource(Store, '/store/<string:name>')
# api.add_resource(StoreList, '/stores')


if __name__ == '__main__': 	## this ensures app runs only from intital launch, not on subsequent imports
	from db import db 	#this is done to avoid circular imports by having it up top
	db.init_app(app)
	app.run(port=5000, debug=True)


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
