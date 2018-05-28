from league import League
from config import logger, pp, log_and_raise_error
from util import *
from bs4 import BeautifulSoup
import json
import datetime
thisYear = datetime.datetime.now().year

class MyFantasyLeague(League):
    def __init__(self, leagueId=0):
        leagueId = int(leagueId)
        if not isinstance(leagueId, ( int, long )) or leagueId <= 0:
            log_and_raise_error("Invalid league ID: %s" % leagueId)
        self.leagueId = leagueId
        self.name = "MyFantasyLeague League %s" % self.leagueId

    def get_rosters(self):
        logger.debug("Getting myfantasyleague rosters for leagueId: %s" % (self.leagueId))

        leagueRosters = {}

        leagueUrl = "http://www.myfantasyleague.com/%d/export?TYPE=league&L=%s&W=&JSON=1" % (thisYear, self.leagueId)
        page = read_page(leagueUrl)

        if not page:
            logger.error("Could not read page: %s" % leagueUrl)
        else:
            try:
                league = json.loads(page)
                teams = {}
                playerIdList = []
                players = {}

                if "league" in league and "name" in league["league"]:
                    self.name = league["league"]["name"]

                if "league" in league and "franchises" in league["league"] and "franchise" in league["league"]["franchises"]:
                    franchises = league["league"]["franchises"]["franchise"]
                    for franchise in franchises:
                        if "id" in franchise and "name" in franchise:
                            teams[franchise["id"]] = {"name": strip_tags(franchise["name"]), "roster": []}

                if teams:
                    rostersUrl = "http://www.myfantasyleague.com/%d/export?TYPE=rosters&L=%s&W=&JSON=1" % (thisYear, self.leagueId)
                    rostersPage = read_page(rostersUrl)

                    if not rostersPage:
                        logger.error("Could not read page: %s" % rostersUrl)
                    else:
                        rosters = json.loads(rostersPage)

                        if "rosters" in rosters and "franchise" in rosters["rosters"]:
                            franchises = rosters["rosters"]["franchise"]
                            for franchise in franchises:
                                if "id" in franchise and "player" in franchise:
                                    id = franchise["id"]
                                    teams[id]["roster"] = []
                                    playerIds = franchise["player"]
                                    for playerId in playerIds:
                                        if "id" in playerId:
                                            teams[id]["roster"].append({"id": playerId["id"]})
                                            playerIdList.append(playerId["id"])

                if playerIdList:
                    playersUrl = ""
                    if len(playerIdList) > 500:
                        playersUrl = "http://www.myfantasyleague.com/%d/export?TYPE=players&JSON=1&DETAILS=1" % (thisYear)
                    else:
                        playersUrl = "http://www.myfantasyleague.com/%d/export?TYPE=players&JSON=1&DETAILS=1&PLAYERS=%s" % (thisYear, ",".join(playerIdList))
                    playersPage = read_page(playersUrl)

                    if not playersPage:
                        logger.error("Could not read page: %s" % playersUrl)
                    else:
                        playerData = json.loads(playersPage)

                        if "players" in playerData and "player" in playerData["players"]:
                            playerList = playerData["players"]["player"]
                            for player in playerList:
                                if "id" in player and "position" in player and "team" in player and "name" in player:
                                    if player["position"].startswith("TM") or player["position"] == "Coach" or player["position"] == "Off":
                                        # Skip players we can't really rank
                                        continue
                                    if player["position"] == "PK":
                                        player["position"] = "K"
                                    elif player["position"] == "Def" or player["position"] == "ST":
                                        player["position"] = "DST"
                                    elif player["position"] == "CB" or player["position"] == "S":
                                        player["position"] = "DB"
                                    elif player["position"] == "DE" or player["position"] == "DT":
                                        player["position"] = "DL"

                                    players[player["id"]] = {"id": player["id"], "name": player["name"], "team": player["team"], "position": player["position"]}

                                    if "birthdate" in player:
                                        players[player["id"]]["age"] = num_years_since(datetime.datetime.fromtimestamp(int(player["birthdate"])))

                if players:
                    for id,team in teams.iteritems():
                        leagueRosters[team["name"]] = {"roster": []}
                        teamRoster = leagueRosters[team["name"]]["roster"]
                        for rosterPlayer in team["roster"]:
                            if rosterPlayer["id"] in players:
                                teamRoster.append(players[rosterPlayer["id"]])

            except ValueError as e:
                leagueRosters = {}
                import traceback
                logger.error("Error getting myfantasyleague rosters = %s\n%s" % (str(e), traceback.format_exc()))
            except Exception:
                leagueRosters = {}
                import traceback
                logger.error("Generic exception: %s" % traceback.format_exc())

        return leagueRosters

    @staticmethod
    def is_same_player(player={}, rankedPlayer={}):
        if not player or not rankedPlayer:
            log_and_raise_error("Invalid player: %s, %s" % (player, rankedPlayer))

        if player["team"] == "RAM":
            player["team"] = "LAR"

        playerNames = player["name"].split(", ")
        playerNames.reverse()
        result = True
        for name in playerNames:
            if not name.lower() in rankedPlayer["name"].lower():
                result = False
                break

        result = result and ((player["position"].lower() == "DST".lower() and not "team" in rankedPlayer) or player["team"].lower() == rankedPlayer["team"].lower() or player["team"].lower().startswith(rankedPlayer["team"].lower())) and player["position"].lower() == rankedPlayer["position"].lower()

        return result

    @staticmethod
    def get_all_players():
        allPlayers = {}
        playersUrl = "http://www.myfantasyleague.com/%d/export?TYPE=players&JSON=1&DETAILS=1" % thisYear
        playersPage = read_page(playersUrl)
        if not playersPage:
            logger.error("Could not read page: %s" % playersUrl)
        else:
            try:
                allPlayers = json.loads(playersPage)
                allPlayers = allPlayers['players']['player']
            except ValueError as e:
                allPlayers = {}
                import traceback
                logger.error("Error getting all myfantasyleague layers = %s\n%s" % (str(e), traceback.format_exc()))
            except Exception:
                allPlayers = {}
                import traceback
                logger.error("Generic exception: %s" % traceback.format_exc())
        return allPlayers
