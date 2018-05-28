from rankings import Rankings
from bs4 import BeautifulSoup
import re
from config import logger, pp, log_and_raise_error
from util import *

class FantasyPros(Rankings):
    def __init__():
        pass

    @staticmethod
    def _get_rankings_uri(rankingsType="weekly", ppr="ppr", dynasty=False, position="FLEX"):
        rankingsUri = "https://www.fantasypros.com/nfl/rankings/dynasty-overall.php"
        if dynasty:
            if position == "QB":
                rankingsUri = "https://www.fantasypros.com/nfl/rankings/dynasty-qb.php"
            elif position == "RB":
                rankingsUri = "https://www.fantasypros.com/nfl/rankings/dynasty-rb.php"
            elif position == "WR":
                rankingsUri = "https://www.fantasypros.com/nfl/rankings/dynasty-wr.php"
            elif position == "TE":
                rankingsUri = "https://www.fantasypros.com/nfl/rankings/dynasty-te.php"
            elif position == "FLEX":
                rankingsUri = "https://www.fantasypros.com/nfl/rankings/dynasty-overall.php"
            elif position == "IDP":
                rankingsUri = "https://www.fantasypros.com/nfl/rankings/dynasty-idp.php"
            elif position == "DL":
                rankingsUri = "https://www.fantasypros.com/nfl/rankings/dynasty-dl.php"
            elif position == "LB":
                rankingsUri = "https://www.fantasypros.com/nfl/rankings/dynasty-lb.php"
            elif position == "DB":
                rankingsUri = "https://www.fantasypros.com/nfl/rankings/dynasty-db.php"
            elif position == "K":
                rankingsUri = "https://www.fantasypros.com/nfl/rankings/k-cheatsheets.php"
            elif position == "DST":
                rankingsUri = "https://www.fantasypros.com/nfl/rankings/dst-cheatsheets.php"
        else:
            if rankingsType == "season":
                if position == "QB":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/qb-cheatsheets.php"
                elif position == "IDP":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/idp-cheatsheets.php"
                elif position == "DL":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/dl-cheatsheets.php"
                elif position == "LB":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/lb-cheatsheets.php"
                elif position == "DB":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/db-cheatsheets.php"
                if position == "K":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/k-cheatsheets.php"
                elif position == "DST":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/dst-cheatsheets.php"
                elif ppr == "standard":
                    if position == "RB":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/rb-cheatsheets.php"
                    elif position == "WR":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/wr-cheatsheets.php"
                    elif position == "TE":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/te-cheatsheets.php"
                    elif position == "FLEX":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php"
                elif ppr == "half":
                    if position == "RB":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-rb-cheatsheets.php"
                    elif position == "WR":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-wr-cheatsheets.php"
                    elif position == "TE":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-te-cheatsheets.php"
                    elif position == "FLEX":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php"
                else:
                    if position == "RB":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ppr-rb-cheatsheets.php"
                    elif position == "WR":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ppr-wr-cheatsheets.php"
                    elif position == "TE":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ppr-te-cheatsheets.php"
                    elif position == "FLEX":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php"
            elif rankingsType == "restofseason":
                if position == "QB":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-qb.php"
                elif position == "IDP":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/idp-cheatsheets.php"
                elif position == "DL":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/dl-cheatsheets.php"
                elif position == "LB":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/lb-cheatsheets.php"
                elif position == "DB":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/db-cheatsheets.php"
                if position == "K":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-k.php"
                elif position == "DST":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-dst.php"
                elif ppr == "standard":
                    if position == "RB":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-rb.php"
                    elif position == "WR":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-wr.php"
                    elif position == "TE":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-te.php"
                    elif position == "FLEX":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-flex.php"
                elif ppr == "half":
                    if position == "RB":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-half-point-ppr-rb.php"
                    elif position == "WR":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-half-point-ppr-wr.php"
                    elif position == "TE":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-half-point-ppr-te.php"
                    elif position == "FLEX":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-half-point-ppr-flex.php"
                else:
                    if position == "RB":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-ppr-rb.php"
                    elif position == "WR":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-ppr-wr.php"
                    elif position == "TE":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-ppr-te.php"
                    elif position == "FLEX":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ros-ppr-flex.php"
            else: # weekly
                if position == "QB":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/qb.php"
                elif position == "IDP":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/idp.php"
                elif position == "DL":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/dl.php"
                elif position == "LB":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/lb.php"
                elif position == "DB":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/db.php"
                elif position == "K":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/k.php"
                elif position == "DST":
                    rankingsUri = "https://www.fantasypros.com/nfl/rankings/dst.php"
                elif ppr == "standard":
                    if position == "RB":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/rb.php"
                    elif position == "WR":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/wr.php"
                    elif position == "TE":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/te.php"
                    elif position == "FLEX":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/flex.php"
                elif ppr == "half":
                    if position == "RB":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-rb.php"
                    elif position == "WR":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-wr.php"
                    elif position == "TE":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-te.php"
                    elif position == "FLEX":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-flex.php"
                else:
                    if position == "RB":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ppr-rb.php"
                    elif position == "WR":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ppr-wr.php"
                    elif position == "TE":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ppr-te.php"
                    elif position == "FLEX":
                        rankingsUri = "https://www.fantasypros.com/nfl/rankings/ppr-flex.php"

        return rankingsUri

    @staticmethod
    def get_rankings(rankingsType="weekly", ppr="ppr", dynasty=False, position="FLEX"):
        if (not (rankingsType == "weekly" or rankingsType == "season" or rankingsType == "restofseason")):
            log_and_raise_error("Invalid rankings type value: %s" % rankingsType)
        if (not (ppr == "ppr" or ppr == "half" or ppr == "standard")):
            log_and_raise_error("Invalid ppr value: %s" % ppr)
        if (not (position == "FLEX" or position == "QB" or position == "RB" or position == "WR" or position == "TE" or position == "K" or position == "DST" or position == "IDP" or position == "DL" or position == "LB" or position == "DB")):
            log_and_raise_error("Invalid position value: %s" % position)

        logger.debug("Getting rankings for ppr: %s, dynasty: %s, position: %s" % (ppr, dynasty, position))

        rankings = []

        rankingsUri = FantasyPros._get_rankings_uri(rankingsType=rankingsType, ppr=ppr, dynasty=dynasty, position=position)

        page = read_page(rankingsUri)

        if not page:
            logger.error("Could not read page: %s" % rankingsUri)
        else:
            try:
                soup = BeautifulSoup(page, "html.parser")

                tbodys = soup.find_all("tbody")

                playerstbody = tbodys[0]

                playertrs = playerstbody.find_all("tr");

                for playertr in playertrs:
                    if "class" in playertr.attrs and ("table-ad" in playertr["class"] or "tier-row" in playertr["class"] or "static" in playertr["class"]):
                        continue
                    playertds = playertr.find_all("td")
                    player = {}
                    if playertds[0].contents[0] == "No Players found":
                        continue
                    if playertds[0].contents[0] == "Rankings for this time period are not available yet":
                        continue
                    player["rank"] = int(playertds[0].contents[0])
                    playername = playertds[2].find("a")
                    if not playername or len(playername.contents) < 1:
                        continue
                    player["name"] = str(playername.contents[0])

                    if (position == "FLEX" or position == "IDP"):
                        player["position"] = str(re.sub(r'\d', "", playertds[3].contents[0]))
                    else:
                        player["position"] = position

                    if (player["position"] != "DST"):
                        small = playertds[2].find("small")
                        player["team"] = str(small.contents[0])
                        a = small.find("a")
                        if a:
                            player["team"] = str(a.contents[0])

                    rankings.append(player)

            except Exception:
                rankings = []
                import traceback
                logger.error("Generic exception: %s" % traceback.format_exc())

        return rankings
