from app import app
from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy(app)

class Ranking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    path = db.Column(db.String, unique=True)
    rankings = db.Column(db.String)

    def __init__(self, path, rankings):
        self.path = path
        self.rankings = rankings

    def __repr__(self):
        return '<Ranking Path %s>' % self.path

class RankingImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    path = db.Column(db.String, unique=True)
    filename = db.Column(db.String)

    def __init__(self, path, filename):
        self.path = path
        self.filename = filename

    def __repr__(self):
        return '<Ranking Image Path %s>' % self.path

class OauthToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    key = db.Column(db.String, unique=True)
    token = db.Column(db.String)

    def __init__(self, key, token):
        self.key = key
        self.token = token

    def __repr__(self):
        return '<Token Key %s>' % self.key
