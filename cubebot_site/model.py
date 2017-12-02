from db import db
from flask_login import UserMixin


class UserModel(UserMixin, db.Model):
	__tablename__ = 'users' #for db SQLAlchemy setup

	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True)	#max username length
	email = db.Column(db.String(50), unique=True)
	password = db.Column(db.String(80))
	FBuserID = db.Column(db.String(32))
	FBuserPSID = db.Column(db.String(32))
	FBAccessToken = db.Column(db.String(128))
	FBname = db.Column(db.String(32))
	content = db.relationship('ContentModel', lazy='dynamic') ## connecting users to content
	thread = db.relationship('ThreadModel', lazy='dynamic') ## connecting users to threads
	reviewsOn = db.relationship('ReviewsModel', lazy='dynamic') ## connecting users to threads

	def __init__(self, username, email, password, FBuserID, FBuserPSID, FBAccessToken, FBname):
		self.username = username
		self.email = email
		self.password = password
		self.FBuserID = FBuserID  ## Actual FB ID for user
		self.FBuserPSID = FBuserPSID  ## This is our product scoped id for FB User
		self.FBAccessToken = FBAccessToken
		self.FBname = FBname

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

	@classmethod
	def find_by_FBuserPSID(cls, FBuserPSID):
		return cls.query.filter_by(FBuserPSID=FBuserPSID).first()



## New DB Model Class to Manage Content
class ContentModel(db.Model):
	__tablename__ = 'content'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(180)) #file name, link title etc
	category = db.Column(db.String(80)) #pdf, link, etc.
	url = db.Column(db.VARCHAR(2083)) #these could get long, not sure if there's something better than string to save these
	urlImage = db.Column(db.VARCHAR(2083)) #url for link image
	source = db.Column(db.VARCHAR(2083)) #dropbox, youtube, evernote etc.
	user_id = db.Column(db.Integer, db.ForeignKey('users.id')) ## connecting users to content
	user = db.relationship("UserModel", uselist=False)
	# ThreadContent = db.relationship('ThreadContentModel', lazy='dynamic') do we need this yet?
	reviewsOn = db.relationship('ReviewsModel', lazy='dynamic') #do we need this yet?

	def __init__(self, title, category, url, urlImage, source, user_id):
		self.title = title
		self.category = category
		self.url = url
		self.urlImage = urlImage
		self.source = source
		self.user_id = user_id ## connecting users to content

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


## new db model to handle reviews on content data
class ReviewsModel(db.Model):
	__tablename__ = 'reviews'

	id = db.Column(db.Integer, primary_key=True)
	rateValue = db.Column(db.Integer)
	reviewsOn_userID = db.Column(db.Integer, db.ForeignKey('users.id'))
	reviewsOn_contentID = db.Column(db.Integer, db.ForeignKey('content.id'))
	reviewsOn_content = db.relationship("ContentModel")
	reviewsOn_threadID = db.Column(db.Integer, db.ForeignKey('thread.id'))

	def __init__(self, rateValue, reviewsOn_userID, reviewsOn_contentID, reviewsOn_threadID):
		self.rateValue = rateValue
		self.reviewsOn_userID = reviewsOn_userID
		self.reviewsOn_contentID = reviewsOn_contentID
		self.reviewsOn_threadID = reviewsOn_threadID

	def json(self):
		return {'rateValue': self.rateValue, 'user': self.reviewsOn_userID, 'content': self.reviewsOn_contentID, 'reviewer': self.reviewsOn_threadID }

	@classmethod
	def find_by_reviewsOn_threadID(cls, reviewsOn_threadID):
		return cls.query.filter_by(reviewsOn_threadID=reviewsOn_threadID).all()

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()

	def delete_from_db(self):
		db.session.delete(self)
		db.session.commit()

## New DB Model Class for Conversation / Threads
class ThreadModel(db.Model):
	__tablename__ = 'thread'

	id = db.Column(db.Integer, primary_key=True)
	thread_id = db.Column(db.BigInteger) #can be a long integer
	thread_type = db.Column(db.Integer) #one-on-one or group
	thread_channel = db.Column(db.String(80)) # Messenger, iMessages, Web etc.
	thread_userID = db.Column(db.Integer, db.ForeignKey('users.id'))
	# threadContent = db.relationship('ThreadContentModel', lazy='dynamic') do we need this yet?
	# reviewsOn = db.relationship('ReviewsModel', lazy='dynamic') do we need this yet?

	def __init__(self, thread_id, thread_type, thread_channel, thread_userID):
		self.thread_id = thread_id
		self.thread_type = thread_type
		self.thread_channel = thread_channel
		self.thread_userID = thread_userID

	def json(self):
		return {'thread_id': self.thread_id, 'type': self.thread_type, 'channel': self.thread_channel, 'user': self.thread_userID }

	@classmethod
	def find_by_threadID(cls, thread_id):
		return cls.query.filter_by(thread_id=thread_id).all()

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()

	def delete_from_db(self):
		db.session.delete(self)
		db.session.commit()


## New DB Model Class to handle content in Threads; one row for each content in a thread,
## ... so each thread can generate multiple rows in this table
class ThreadContentModel(db.Model):
	__tablename__ = 'ThreadContent'

	id = db.Column(db.Integer, primary_key=True)
	threadID = db.Column(db.Integer, db.ForeignKey('thread.id'))
	contentID = db.Column(db.Integer, db.ForeignKey('content.id'))

	def __init__(self, threadID, contentID):
		self.threadID = threadID
		self.contentID = contentID

	@classmethod
	def find_by_ThreadContentID(cls, threadID):
		return cls.query.filter_by(threadID=threadID).all()

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()

	def delete_from_db(self):
		db.session.delete(self)
		db.session.commit()




## DB Model Class for keyword triggers while chatting with bot
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
