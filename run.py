import os
from cubebot_site import app
from db import db



app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')  #just means the db is in the rood code directory
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://kalpesh:Raksha99!@localhost:5432/postgres'  #just means the db is in the rood code directory


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'kalsecretkey'
# app.config['RECAPTCHA_PUBLIC_KEY'] = '6Ldz3igUAAAAABTCIvnFm11cgCLCLY3HYIFgjVHV'
# app.config['RECAPTCHA_PRIVATE_KEY'] = '6Ldz3igUAAAAANVGqpq7qGA5ta681lb1Se7pCRfP'

#testmode recaptcha
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
app.config['RECAPTCHA_PRIVATE_KEY'] = ' 6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

db.init_app(app)

@app.before_first_request
def create_table():
	db.create_all()

if __name__ == '__main__': 	## this ensures app runs only from intital launch, not on subsequent imports
	from db import db 	#this is done to avoid circular imports by having it up top
	db.init_app(app)
	app.run(port=5000, debug=True)
