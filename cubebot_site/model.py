from db import db

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
