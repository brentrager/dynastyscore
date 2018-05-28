import logging
import logging.handlers
logger = logging.getLogger("dynasty")
logger.setLevel(logging.DEBUG)
rfh = logging.handlers.RotatingFileHandler("dynasty.log", maxBytes=25000000, backupCount=5)
rfh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s")
rfh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(rfh)
logger.addHandler(ch)

def log_and_raise_error(error):
    logger.error(error)
    raise ValueError(error)

import pprint
pp = pprint.PrettyPrinter(indent=4)

import json
config = {}
try:
    fp = open("config.json", "r")
    config = json.load(fp)
    fp.close()
except (OSError, IOError, ValueError) as e:
    config["mode"] = "production"
    logger.error("Error loading config: %s" % e)

mode = config["mode"]
db = config["db"]
serverName = config["serverName"]
preferredScheme = config["preferredScheme"]
uploadFolder = config["uploadFolder"]
yql_callback_uri = config["yql_callback_uri"]
yql_consumer_key = config["yql_consumer_key"]
yql_consumer_secret = config["yql_consumer_secret"]
