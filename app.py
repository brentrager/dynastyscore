from flask import Flask
app = Flask(__name__)
import config
from werkzeug.routing import BaseConverter

class LeagueConverter(BaseConverter):
    def __init__(self, url_map):
        super(LeagueConverter, self).__init__(url_map)
        self.regex = '(?:fleaflicker|myfantasyleague|yahoo)'

app.url_map.converters['league'] = LeagueConverter

app.debug = config.mode == "development"
app.config["SQLALCHEMY_DATABASE_URI"] = config.db
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SERVER_NAME"] = config.serverName
app.config["PREFERRED_URL_SCHEME"] = config.preferredScheme
app.config["UPLOAD_FOLDER"] = config.uploadFolder
