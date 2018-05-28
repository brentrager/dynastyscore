from league import League
import yql
from yql.storage import BaseTokenStore
import os
from hashlib import md5
import re
from model import db, OauthToken
import config
from config import logger, pp
from flask import jsonify
from flask import url_for

class TokenStore(BaseTokenStore):
    def __init__(self):
        pass

    def set(self, name, token):
        if hasattr(token, 'key'):
            token = token.to_string()

        if token:
            logger.info("Saving token in database: %s - %s" % (name, token))
            dbToken = OauthToken(name, token)
            db.session.add(dbToken)
            db.session.commit()

    def get(self, name):
        token = None
        dbTokens = OauthToken.query.filter_by(key=name)
        if dbTokens.count():
            token = dbTokens.first().token
        logger.debug("%s token in database for %s" % ("Found" if token else "Could not find", name))
        if token:
            token = yql.YahooToken.from_string(token)
        return token

    def delete(self, name):
        dbTokens = OauthToken.query.filter_by(key=name)
        if dbTokens.count():
            db.session.delete(dbTokens.first())
            db.session.commit()
            logger.debug("Deleted token in database for %s" % (name))


class Yahoo:
    def __init__(self):
        self.y3 = yql.ThreeLegged(config.yql_consumer_key, config.yql_consumer_secret)
        self.tokenStore = TokenStore()

    def get_yql_token(self, key, verifier=None):
        requestKey = key + '-request'
        requestToken = None
        token = None
        authUri = None

        storedToken = self.tokenStore.get(key)

        if not storedToken:
            # Do the dance
            if verifier:
                requestToken = self.tokenStore.get(requestKey)
            if not requestToken and not verifier:
                requestToken, authUri = self.y3.get_token_and_auth_url(callback_url=url_for("yahoo-form", _external=True, yqlKey=key))
                self.tokenStore.set(requestKey, requestToken)
            else:
                token = self.y3.get_access_token(requestToken, verifier)
                self.tokenStore.delete(requestKey)
                self.tokenStore.set(key, token)
        else:
            # Check access_token is within 1hour-old and if not refresh it
            # and stash it
            token = self.y3.check_token(storedToken)
            if token != storedToken:
                self.tokenStore.set(key, token)

        return (token, authUri)

    def get_leagues(self, key):
        token, authUri = self.get_yql_token(key)

        if token:
            query = "select * from fantasysports.leagues where use_login=1 and game_key in ('nfl')"
            yqlLeagues = self.y3.execute(query, token=token)
            yqlLeagues = yqlLeagues.rows
            leagues = {}
            for league in yqlLeagues:
                if 'name' in league and 'league_key' in league:
                    leagues[league["league_key"]] = league["name"]
            return leagues
        else:
            return {"authUri": authUri}

    def get_league(self, yahooKey, leagueKey):
        token, authUri = self.get_yql_token(yahooKey)
        league = {}

        if token:
            query = "select * from fantasysports.leagues where league_key='%s'" % leagueKey
            yqlLeagues = self.y3.execute(query, token=token)
            yqlLeagues = yqlLeagues.rows
            if yqlLeagues:
                league = yqlLeagues[0]
        return league

    def get_rosters(self, yahooKey, leagueKey):
        token, authUri = yahoo.get_yql_token(yahooKey)

        if token:
            query = "select * from fantasysports.teams.roster where league_key='%s'" % leagueKey
            yqlTeams = self.y3.execute(query, token=token)
            return yqlTeams.rows
        else:
            return []

yahoo = Yahoo()

class YahooLeague(League):
    def __init__(self, yahooKey, leagueKey):
        self.leagueKey = leagueKey
        self.yahooKey = yahooKey
        self.name = "Yahoo League %s" % self.leagueKey
        league = yahoo.get_league(yahooKey, leagueKey)
        if "name" in league: self.name = league["name"]

    def get_rosters(self):
        leagueRosters = {}

        teams = yahoo.get_rosters(self.yahooKey, self.leagueKey)
        for team in teams:
            if  "name" in team and team["name"]:
                leagueRosters[team["name"]] = {"roster": []}
                if "roster" in team and "players" in team["roster"] and "player" in team["roster"]["players"]:
                    roster = team["roster"]["players"]["player"]
                    for rosterPlayer in roster:
                        player = {}
                        player["name"] = rosterPlayer["name"]["full"]

                        player["position"] = rosterPlayer["display_position"]
                        if player["position"] == "DEF":
                            player["position"] = "DST"
                            player["name"] = rosterPlayer["editorial_team_full_name"]

                        player["team"] = rosterPlayer["editorial_team_abbr"].upper()

                        print player
                        leagueRosters[team["name"]]["roster"].append(player)

        return leagueRosters

    @staticmethod
    def is_same_player(player, rankedPlayer):
        if not player or not rankedPlayer:
            log_and_raise_error("Invalid player: %s, %s" % (player, rankedPlayer))

        result = False

        if player["position"].lower() == "DST".lower() and not "team" in rankedPlayer:
            result = player["name"].lower() in rankedPlayer["name"].lower()
        else:
            playerNames = player["name"].split(" ")
            result = True
            for name in playerNames:
                if not name.lower() in rankedPlayer["name"].lower():
                    result = False
                    break

        return result
