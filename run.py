import os
from cubebot_site import app

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')  #just means the db is in the rood code directory
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'kalsecretkey'

@app.before_first_request
def create_table():
	db.create_all()

if __name__ == '__main__': 	## this ensures app runs only from intital launch, not on subsequent imports
	from db import db 	#this is done to avoid circular imports by having it up top
	db.init_app(app)
	app.run(port=5000, debug=True)
