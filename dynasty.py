from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from flask import send_from_directory
from app import app
from dynasty_rankings_generator import logger
from collections import OrderedDict
import config
from config import logger, pp, log_and_raise_error
import json
import re
from flask_sqlalchemy import SQLAlchemy
from model import db, Ranking, RankingImage
import uuid
import os
from external_apis.yahoo import yahoo

import dynasty_rankings_generator as DRG

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/generate-dynasty-score/", methods=["POST"], endpoint="generate-dynasty-score")
def generate_dynasty_score():
    rankings = {}
    path = ""
    try:
        result = validate_post_data(dict(request.form))
        if "error" in result:
            logger.error("Error validating post data: %s" % result["error"])
            return result["error"]

        path = "/%s/%s/%s/%s/" % (result["leagueHost"], result["leagueId"], result["timestamp"], result["rankingsType"])
        rankings = {}
        rankings = check_for_rankings_in_database(path)
        if rankings:
            logger.info("Loaded existing rankings from database for %s" % path)
            return render_template("rankings.html", rankings=DRG.reorder_rankings(rankings))

        startingRosterConfig = OrderedDict([("QB", result["qbs"]), ("RB", result["rbs"]), ("WR", result["wrs"]), ("TE", result["tes"]), ("FLEX", result["flexes"]), ("K", result["ks"]), ("DST", result["dsts"]), ("DL", result["dls"]), ("LB", result["lbs"]), ("DB", result["dbs"]), ("IDP", result["idps"])])
        rankings = DRG.generate_all_rankings(leagueHost=result["leagueHost"], yahooKey=result["yahooKey"], leagueId=result["leagueId"], rankingsType=result["rankingsType"], ppr=result["ppr"], startingRosterConfig=startingRosterConfig)
        if rankings:
            save_rankings_in_database(path, rankings)
    except ValueError, e:
        import traceback
        logger.error("Value Error: %s\n%s" % (e, traceback.format_exc()))
    except Exception:
        import traceback
        logger.error("Generic exception: %s" % traceback.format_exc())
    logger.info("%s rankings for %s" % ("Loaded" if rankings else "Could not load", path))
    if rankings:
        return render_template("rankings.html", rankings=rankings)
    else:
        return render_template("form.html", error="Error loading rankings. <a href=\"https://hard-g.com/support.html\" class=\"alert-link\">Contact Support</a>.")

@app.route("/image/<leagueHost>/<leagueId>/<timestamp>/<rankingsType>/", methods=["GET", "POST"], endpoint="image")
def image(leagueHost, leagueId, timestamp, rankingsType):
    path = "/%s/%s/%s/%s/" % (leagueHost, leagueId, timestamp, rankingsType)
    if request.method == "POST":
        if not check_for_ranking_image_filename_in_database(path):
            if "file" in request.files:
                file = request.files["file"]
                filename = str(uuid.uuid1()) + ".png"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                save_ranking_image_filename_in_database(path, filename)
        return ('', 204)
    else:
        filename = check_for_ranking_image_filename_in_database(path)
        if not filename:
            return ('Not found', 404)
        else:
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/yahoo/leagues/<key>/", endpoint="yahoo-leagues")
def yahoo_leagues(key):
    leagues = yahoo.get_leagues(key)
    return jsonify(**leagues)


@app.route("/dynasty-score/", defaults={"leagueHost": None, "leagueId": None, "timestamp": None, "rankingsType": None, "yqlKey": None})
@app.route("/dynasty-score/<leagueHost>/<leagueId>/<timestamp>/", defaults={"rankingsType": None, "yqlKey": None}, methods=["GET", "POST"])
@app.route("/dynasty-score/<leagueHost>/<leagueId>/<timestamp>/<rankingsType>/", defaults={"yqlKey": None}, methods=["GET", "POST"])
@app.route("/", defaults={"leagueHost": None, "leagueId": None, "timestamp": None, "rankingsType": None, "yqlKey": None}, endpoint="main")
@app.route("/<league:leagueHost>/<leagueId>/<timestamp>/", defaults={"rankingsType": None, "yqlKey": None}, methods=["GET", "POST"], endpoint="rankingsNoType")
@app.route("/<league:leagueHost>/<leagueId>/<timestamp>/<rankingsType>/", defaults={"yqlKey": None}, methods=["GET", "POST"], endpoint="rankings")
@app.route("/yahoo/<yqlKey>/", defaults={"leagueHost": None, "leagueId": None, "timestamp": None, "rankingsType": None}, endpoint="yahoo-form")
def dynasty_score(leagueHost, leagueId, timestamp, rankingsType, yqlKey):
    if not leagueHost or not leagueId or not timestamp:
        leagues = None
        if yqlKey:
            verifier = request.args.get("oauth_verifier", default=None)
            yahoo.get_yql_token(yqlKey, verifier)
            leagues = yahoo.get_leagues(yqlKey)
        return render_template("form_page.html", yahooLeagues=leagues, yahooKey=yqlKey)

    if request.method == "POST":
        data = dict(request.form)
        data["timestamp"] = timestamp
        result = validate_post_data(data)
        if "error" in result:
            logger.error("Error validating post data: %s" % result["error"])
            return render_template("form_page.html", error=result["error"])

        logger.info("Loading rankings for: %s" % result)
        return render_template("rankings_loader.html", postData=json.dumps(result))
    else:
        path = "/%s/%s/%s/" % (leagueHost, leagueId, timestamp)
        if rankingsType: path += "%s/" % rankingsType
        rankings = check_for_rankings_in_database(path)
        logger.info("%s rankings in database for %s" % ("Found" if rankings else "Couldn't find", path))
        if not rankings:
            return render_template("form_page.html", error="Rankings not found")
        leagueName = "%s league %s" % (leagueHost, leagueId)
        title = "%s - %s - Rankings" % (leagueName, timestamp)
        if "League Name" in rankings:
            leagueName = rankings["League Name"]
            title = "%s - %s - Rankings" % (leagueName, timestamp)

        return render_template("rankings_loaded.html", rankings=DRG.reorder_rankings(rankings), title=title, leagueName=leagueName, leagueHost=leagueHost, leagueId=leagueId, timestamp=timestamp, rankingsType=rankingsType)

def save_rankings_in_database(path, rankings):
    if rankings:
        logger.info("Saving rankings in database for: %s" % path)
        dbRanking = Ranking(path, json.dumps(rankings))
        db.session.add(dbRanking)
        db.session.commit()

def check_for_rankings_in_database(path):
    rankings = {}
    dbRankings = Ranking.query.filter_by(path=path)
    if dbRankings.count():
        rankings = json.loads(dbRankings.first().rankings)
    logger.debug("%s rankings in database for %s" % ("Found" if rankings else "Could not find", path))
    return rankings

def save_ranking_image_filename_in_database(path, rankingImageFilename):
        logger.info("Saving ranking image filename in database for %s: %s" % (path, rankingImageFilename))
        dbRankingImage = RankingImage(path, rankingImageFilename)
        db.session.add(dbRankingImage)
        db.session.commit()

def check_for_ranking_image_filename_in_database(path):
    rankingImageFilename = None
    dbRankingImage = RankingImage.query.filter_by(path=path)
    if dbRankingImage.count():
        rankingImageFilename = dbRankingImage.first().filename
    logger.debug("%s ranking image in database for %s" % ("Found" if rankingImageFilename else "Could not find", path))
    return rankingImageFilename

def validate_post_data(data):
    try:
        leagueHost = "fleaflicker" if not "leagueHost" in data else data["leagueHost"][0]
        if not (leagueHost == "fleaflicker" or leagueHost == "myfantasyleague" or leagueHost == "yahoo"):
            return {"error": "Invalid league host: %s" % leagueHost}

        yahooKey = ""
        if leagueHost == "yahoo" and not "yahooKey" in data:
            return {"error": "No key supplied for yahoo league"}
        yahooKey = "" if "yahooKey" not in data else data["yahooKey"][0]


        leagueId = 0
        try:
            leagueId = 0 if not "leagueId" in data else data["leagueId"][0]
        except ValueError, e:
            logger.error("Error getting league ID: %s" % e)
            return {"error": "Invalid league ID: %s" % leagueId}
        except Exception:
            import traceback
            logger.error("Error getting league ID: %s" % traceback.format_exc())
            return {"error": "Invalid league ID: %s" % leagueId}

        timestamp = data["timestamp"]
        if not isinstance(timestamp, basestring):
            timestamp = timestamp[0]

        if not re.match("\d+\.\d+\.\d+\-\d+\:\d+\:\d+\-(AM|PM)", timestamp):
            logger.error("Error getting timestamp: %s" % timestamp)
            return {"error": "Invalid timestamp: %s" % timestamp}

        rankingsType = "weekly" if not "rankingsType" in data else data["rankingsType"][0]

        if not (rankingsType == "weekly" or rankingsType == "season" or rankingsType == "restofseason"):
            return {"error": "Invalid rankings type value: %s" % rankingsType}

        ppr = "standard" if not "ppr" in data else data["ppr"][0]

        if not (ppr == "standard" or ppr == "ppr" or ppr == "half"):
            return {"error": "Invalid PPR value: %s" % ppr}

        qbs = 1
        rbs = 2
        wrs = 2
        tes = 1
        flexes = 1
        ks = 1
        dsts = 1
        idps = 0
        dls = 0
        lbs = 0
        dbs = 0

        try:
            qbs = 1 if not "qbs" in data else int(data["qbs"][0])
            rbs = 2 if not "rbs" in data else int(data["rbs"][0])
            wrs = 2 if not "wrs" in data else int(data["wrs"][0])
            tes = 1 if not "tes" in data else int(data["tes"][0])
            flexes = 1 if not "flexes" in data else int(data["flexes"][0])
            ks = 1 if not "ks" in data else int(data["ks"][0])
            dsts = 1 if not "dsts" in data else int(data["dsts"][0])
            idps = 1 if not "idps" in data else int(data["idps"][0])
            dls = 1 if not "dls" in data else int(data["dls"][0])
            lbs = 1 if not "lbs" in data else int(data["lbs"][0])
            dbs = 1 if not "dbs" in data else int(data["dbs"][0])

        except ValueError, e:
            logger.error("Error getting position numbers: %s" % e)
            return {"error": "Invalid position numbers"}
        except Exception:
            import traceback
            logger.error("Error getting position numbers: %s" % traceback.format_exc())
            return {"error": "Invalid position numbers"}

        return {"leagueHost": leagueHost, "yahooKey": yahooKey, "leagueId": leagueId, "timestamp": timestamp, "rankingsType": rankingsType, "ppr": ppr, "qbs": qbs, "rbs": rbs, "wrs": wrs, "tes": tes, "flexes": flexes, "ks": ks, "dsts": dsts, "idps": idps, "dls": dls, "lbs": lbs, "dbs": dbs}
    except Exception:
        import traceback
        logger.error("Unknown error: %s" % traceback.format_exc())
        return {"error": "Unknown error"}

#@app.errorhandler(404)
#def page_not_found(e):
#    return "Error: %s" % request.path

if __name__ == "__main__":
    app.run(debug=app.debug, host='127.0.0.1', port=80)
