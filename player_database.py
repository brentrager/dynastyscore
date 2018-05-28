from app import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
import datetime
from external_apis.myfantasyleague import MyFantasyLeague
from config import pp

db = SQLAlchemy(app)

allPlayers = MyFantasyLeague.get_all_players()

keys = set()

for player in allPlayers:
    for key, val in player.iteritems():
        keys.add(key)

class Player(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    for key in keys:
        if key == 'id':
            pass
        else:
            locals()[key] = db.Column(key, db.String)

    def __init__(self, object):
        for key, value in object.iteritems():
            if key == 'id':
                self.id = int(object[key])
            else:
                setattr(self, key, value)

    def __repr__(self):
        return '<Player Image Path %s>' % self.id

playerTableName = Player.__tablename__
playerTable = db.metadata.tables[playerTableName]

if (playerTableName in db.engine.table_names()):
    playerTable.drop(db.engine)

playerTable.create(db.engine)

for player in allPlayers:
    db.session.add(Player(player))
db.session.commit()
