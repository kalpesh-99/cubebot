from db import db
from flask_login import UserMixin

# via mobolic/facebook-sdk for python
# class User(db.Model):
#     __tablename__ = 'users'
#
#     id = db.Column(db.String, nullable=False, primary_key=True)
#     created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
#     updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
#                         onupdate=datetime.utcnow)
#     name = db.Column(db.String, nullable=False)
#     profile_url = db.Column(db.String, nullable=False)
#     access_token = db.Column(db.String, nullable=False)


class UserModel(UserMixin, db.Model):
	__tablename__ = 'users' #for db SQLAlchemy setup

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True)	#max username length
	email = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(80))
	FBuserID = db.Column(db.String(32))
	FBAccessToken = db.Column(db.String(128))



	def __init__(self, username, email, password, FBuserID, FBAccessToken):
		self.username = username
		self.email = email
		self.password = password
		self.FBuserID = FBuserID
		self.FBAccessToken = FBAccessToken

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()

	@classmethod #makes the code a bit nicer, as we're not using 'self' in the method
	def find_by_username(cls, username):		## ths is a function that will find users in our db
		return cls.query.filter_by(username=username).first()  #note (cls, username) is =username

	@classmethod
	def find_by_id(cls, _id):		## to create a simlar mapping function based on id this time
		return cls.query.filter_by(id=_id).first()

	@classmethod
	def find_by_FBuserID(cls, FBuserID):
		return cls.query.filter_by(FBuserID=FBuserID).first()





class TriggerModel(db.Model):
    __tablename__ = 'triggers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    category = db.Column(db.String(80))

    def __init__(self, name, category):
        self.name = name
        self.category = category

    def json(self):
        return {'name': self.name, 'category': self.category }


    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

## New DB Model Class to Manage Content
class ContentModel(db.Model):
    __tablename__ = 'content'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180)) #file name, link title etc
    category = db.Column(db.String(80)) #pdf, link, etc.
    url = db.Column(db.VARCHAR(2083)) #these could get long, not sure if there's something better than string to save these
    urlImage = db.Column(db.VARCHAR(2083)) #url for link image
    source = db.Column(db.String(80)) #dropbox, youtube, evernote etc.

    def __init__(self, title, category, url, urlImage):
        self.title = title
        self.category = category
        self.url = url
        self.urlImage = urlImage

    def json(self):
        return {'id': self.id, 'title': self.title, 'category': self.category, 'url': self.url }


    @classmethod
    def find_by_category(cls, category):
        return cls.query.filter_by(category=category).all()


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
