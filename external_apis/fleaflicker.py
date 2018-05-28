from league import League
from config import logger, pp, log_and_raise_error
from util import *
from bs4 import BeautifulSoup

class Fleaflicker(League):
    def __init__(self, leagueId=0):
        leagueId = int(leagueId)
        if not isinstance(leagueId, ( int, long )) or leagueId <= 0:
            log_and_raise_error("Invalid league ID: %s" % leagueId)
        self.leagueId = leagueId
        self.name = "Fleaflicker League %s" % self.leagueId

    def get_rosters(self):
        logger.debug("Getting fleaflicker rosters for leagueId: %s" % (self.leagueId))

        leagueRosters = {}
        baseUrl = "http://www.fleaflicker.com"
        leagueRostersPage = "%s/nfl/leagues/%s/teams" % (baseUrl, self.leagueId)

        page = read_page(leagueRostersPage)

        if not page:
            logger.error("Could not read page: %s" % leagueRostersPage)
        else:
            try:
                soup = BeautifulSoup(page, "html.parser")

                self.name = soup.find("ul", {"class" : "breadcrumb"}).find("li", {"class" : "active"}).contents[0]

                tables = soup.find_all("table", {"class" : "table-group"})

                teams = []

                for table in tables:
                    teamtds = table.find_all("td", {"class" : "table-heading"})

                    for teamtd in teamtds:
                        span = teamtd.find("span", {"class" : "league-name"})
                        team = span.contents[0] if len(span.contents) == 1 else span.contents[1]

                        averageAge = 0
                        playersWithNoAge = 0
                        roster = []

                        tr = span.find_parent("tr")

                        while True:
                            tr = tr.find_next_sibling("tr")

                            if not tr:
                                break

                            thead = tr.find_parent("thead")
                            if thead:
                                tr = thead.find_next_sibling("tr")

                            if tr.find("td", {"class" : "vertical-spacer"}):
                                break;

                            player = {}
                            a = tr.find("div", {"class" : "player"}).find("a")
                            player["name"] = str(a.contents[0])
                            player["url"] = str("%s%s" % (baseUrl, a["href"]))
                            player["team"] = str(tr.find("span", {"class" : "player-team"}).contents[0])
                            player["position"] = str(tr.find("span", {"class" : "position"}).contents[0])
                            player["age"] = 0
                            if player["position"] == "D/ST":
                                player["position"] = "DST"

                            if (player["team"] == "ARI" and player["name"] == "J. Brown" and "jaron-brown" in player["url"]):
                                player["name"] = "Ja. Brown"

                            # Keep age code around, but we won't be using it right now. It takes too long.
                            if False:
                                if player["position"] != "DST":
                                    playerPage = read_page(player["url"])

                                    if playerPage:
                                        playerSoup = BeautifulSoup(playerPage, "html.parser")

                                        panel = playerSoup.find("dl", {"class" : "panel-body"})
                                        for panelChild in panel.children:
                                            if panelChild.name == "dt" and panelChild.contents[0] == "Age":
                                                agedd = panelChild.find_next_sibling("dd")
                                                player["age"] = agedd.find("span").contents[0]
                                    else:
                                        logger.error("Could not read page: %s" % player["url"])

                                if player["age"] == 0:
                                    playersWithNoAge += 1

                                averageAge = averageAge + int(player["age"])

                            roster.append(player)

                        #averageAge = float(averageAge) / float(len(roster) - playersWithNoAge)
                        leagueRosters[team] = {"roster": roster} # , "averageAge": averageAge}

            except Exception:
                leagueRosters = {}
                import traceback
                logger.error("Generic exception: %s" % traceback.format_exc())

        return leagueRosters

    @staticmethod
    def is_same_player(player={}, rankedPlayer={}):
        if not player or not rankedPlayer:
            log_and_raise_error("Invalid player: %s, %s" % (player, rankedPlayer))

        if player["team"] == "LA":
            player["team"] = "LAR"

        result = False

        if player["position"].lower() == "DST".lower() and not "team" in rankedPlayer:
            result = player["name"].lower() in rankedPlayer["name"].lower()
        else:
            nameParts = player["name"].split(". ")
            result = rankedPlayer["name"].lower().startswith(nameParts[0].lower()) and nameParts[1].lower() in rankedPlayer["name"].lower() and (player["team"].lower() == rankedPlayer["team"].lower() or player["team"].lower().startswith(rankedPlayer["team"].lower())) and player["position"].lower() == rankedPlayer["position"].lower()

        return result
