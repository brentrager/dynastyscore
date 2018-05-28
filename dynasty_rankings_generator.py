from collections import OrderedDict
import copy
import sys
from util import *
from external_apis.fleaflicker import Fleaflicker
from external_apis.myfantasyleague import MyFantasyLeague
from external_apis.yahoo import YahooLeague
from external_apis.fantasypros import FantasyPros

UNRANKED_PENALTY = 10
DEPTH_MULTIPLIER = 2
FLEX_POSITIONS = ["RB", "WR", "TE"]
IDP_POSITIONS = ["DL", "LB", "DB", "IDP"]

def reorder_rankings(rankings):
    newRankings = OrderedDict()
    newRankings["Redraft Starter Rankings"] = {} if not "Redraft Starter Rankings" in rankings else rankings["Redraft Starter Rankings"]
    newRankings["Dynasty Starter Rankings"] = {} if not "Dynasty Starter Rankings" in rankings else rankings["Dynasty Starter Rankings"]
    newRankings["Combined Starter Rankings"] ={} if not "Combined Starter Rankings" in rankings else rankings["Combined Starter Rankings"]
    newRankings["Redraft Depth Rankings"] = {} if not "Redraft Depth Rankings" in rankings else rankings["Redraft Depth Rankings"]
    newRankings["Dynasty Depth Rankings"] = {} if not "Dynasty Depth Rankings" in rankings else rankings["Dynasty Depth Rankings"]
    newRankings["Combined Depth Rankings"] = {} if not "Combined Depth Rankings" in rankings else rankings["Combined Depth Rankings"]
    if "Age Rankings" in rankings: newRankings["Age Rankings"] = rankings["Age Rankings"]
    if "League Name" in rankings: newRankings["League Name"] = rankings["League Name"]
    return newRankings

def generate_all_rankings(leagueHost="fleaflicker", yahooKey=None, leagueId=0, rankingsType="rankingsType", ppr="ppr", startingRosterConfig=OrderedDict()):
    if not (leagueHost == "fleaflicker" or leagueHost == "myfantasyleague" or leagueHost == "yahoo"):
        log_and_raise_error("Invalid league host: %s" % leagueHost)
    if (leagueId <= 0):
        log_and_raise_error("Invalid league ID: %s" % leagueId)
    if (not (ppr == "ppr" or ppr == "half" or ppr == "standard")):
        log_and_raise_error("Invalid ppr value: %s" % ppr)
    if (not startingRosterConfig):
        log_and_raise_error("Must provide starting roster config.")
    if (leagueHost == "yahoo" and not yahooKey):
        log_and_raise_error("Requested yahoo rankings without yahoo key.")

    logger.info("Generating all rankings for leagueHost: %s, leagueId: %s, ppr: %s, startingRosterConfig: %s" % (leagueHost, leagueId, ppr, startingRosterConfig))

    league = None
    if leagueHost == "fleaflicker":
        league = Fleaflicker(leagueId)
    elif leagueHost == "myfantasyleague":
        league = MyFantasyLeague(leagueId)
    elif leagueHost == "yahoo":
        league = YahooLeague(yahooKey, leagueId)

    leagueRosters = league.get_rosters()

    kickerRankings = []
    if "K" in startingRosterConfig and int(startingRosterConfig["K"]) > 0: kickerRankings = FantasyPros.get_rankings(rankingsType=rankingsType, position="K")
    dstRankings = []
    if "DST" in startingRosterConfig and int(startingRosterConfig["DST"]) > 0: dstRankings = FantasyPros.get_rankings(rankingsType=rankingsType, position="DST")

    redraftRankings = {}
    redraftRankings["FLEX"] = FantasyPros.get_rankings(rankingsType=rankingsType, ppr=ppr, dynasty=False, position="FLEX")
    if "QB" in startingRosterConfig and int(startingRosterConfig["QB"]) > 0: redraftRankings["QB"] = FantasyPros.get_rankings(rankingsType=rankingsType, ppr=ppr,dynasty=False, position="QB")
    if "RB" in startingRosterConfig and int(startingRosterConfig["RB"]) > 0: redraftRankings["RB"] = FantasyPros.get_rankings(rankingsType=rankingsType, ppr=ppr,dynasty=False, position="RB")
    if "WR" in startingRosterConfig and int(startingRosterConfig["WR"]) > 0: redraftRankings["WR"] = FantasyPros.get_rankings(rankingsType=rankingsType, ppr=ppr,dynasty=False, position="WR")
    if "TE" in startingRosterConfig and int(startingRosterConfig["TE"]) > 0: redraftRankings["TE"] = FantasyPros.get_rankings(rankingsType=rankingsType, ppr=ppr,dynasty=False, position="TE")
    if any(p in startingRosterConfig and startingRosterConfig[p] > 0 for p in IDP_POSITIONS): redraftRankings["IDP"] = FantasyPros.get_rankings(rankingsType=rankingsType, ppr=ppr,dynasty=False, position="IDP")
    if "DL" in startingRosterConfig and int(startingRosterConfig["DL"]) > 0: redraftRankings["DL"] = FantasyPros.get_rankings(rankingsType=rankingsType, ppr=ppr,dynasty=False, position="DL")
    if "LB" in startingRosterConfig and int(startingRosterConfig["LB"]) > 0: redraftRankings["LB"] = FantasyPros.get_rankings(rankingsType=rankingsType, ppr=ppr,dynasty=False, position="LB")
    if "DB" in startingRosterConfig and int(startingRosterConfig["DB"]) > 0: redraftRankings["DB"] = FantasyPros.get_rankings(rankingsType=rankingsType, ppr=ppr,dynasty=False, position="DB")

    dynastyRankings = {}
    dynastyRankings["FLEX"] = FantasyPros.get_rankings(ppr=ppr, dynasty=True, position="FLEX")
    if "QB" in startingRosterConfig and int(startingRosterConfig["QB"]) > 0: dynastyRankings["QB"] = FantasyPros.get_rankings(ppr=ppr, dynasty=True, position="QB")
    if "RB" in startingRosterConfig and int(startingRosterConfig["RB"]) > 0: dynastyRankings["RB"] = FantasyPros.get_rankings(ppr=ppr, dynasty=True, position="RB")
    if "WR" in startingRosterConfig and int(startingRosterConfig["WR"]) > 0: dynastyRankings["WR"] = FantasyPros.get_rankings(ppr=ppr, dynasty=True, position="WR")
    if "TE" in startingRosterConfig and int(startingRosterConfig["TE"]) > 0: dynastyRankings["TE"] = FantasyPros.get_rankings(ppr=ppr, dynasty=True, position="TE")
    if any(p in startingRosterConfig and startingRosterConfig[p] > 0 for p in IDP_POSITIONS): dynastyRankings["IDP"] = FantasyPros.get_rankings(ppr=ppr, dynasty=True, position="IDP")
    if "DL" in startingRosterConfig and int(startingRosterConfig["DL"]) > 0: dynastyRankings["DL"] = FantasyPros.get_rankings(ppr=ppr, dynasty=True, position="DL")
    if "LB" in startingRosterConfig and int(startingRosterConfig["LB"]) > 0: dynastyRankings["LB"] = FantasyPros.get_rankings(ppr=ppr, dynasty=True, position="LB")
    if "DB" in startingRosterConfig and int(startingRosterConfig["DB"]) > 0: dynastyRankings["DB"] = FantasyPros.get_rankings(ppr=ppr, dynasty=True, position="DB")

    if any(p in startingRosterConfig and startingRosterConfig[p] > 0 for p in IDP_POSITIONS) and not dynastyRankings["IDP"] and redraftRankings["IDP"]: dynastyRankings["IDP"] = redraftRankings["IDP"]
    if "DL" in startingRosterConfig and int(startingRosterConfig["DL"]) > 0 and not dynastyRankings["DL"] and redraftRankings["DL"]: dynastyRankings["DL"] = redraftRankings["DL"]
    if "LB" in startingRosterConfig and int(startingRosterConfig["LB"]) > 0 and not dynastyRankings["LB"] and redraftRankings["LB"]: dynastyRankings["LB"] = redraftRankings["LB"]
    if "DB" in startingRosterConfig and int(startingRosterConfig["DB"]) > 0 and not dynastyRankings["DB"] and redraftRankings["DB"]: dynastyRankings["DB"] = redraftRankings["DB"]

    if (("IDP" in startingRosterConfig and int(startingRosterConfig["IDP"]) > 0) or any((p in startingRosterConfig and int(startingRosterConfig[p]) > 0) for p in IDP_POSITIONS)):
        if not redraftRankings["IDP"]:
            log_and_raise_error("Must provide IDP redraft rankings.")
        if not dynastyRankings["IDP"]:
            log_and_raise_error("Must provide IDP dynasty rankings.")

    combinedRankings = {}
    if dynastyRankings["FLEX"]: combinedRankings["FLEX"] = generate_combined_rankings(redraftRankings["FLEX"], dynastyRankings["FLEX"])
    if dynastyRankings["FLEX"] and ("QB" in startingRosterConfig and int(startingRosterConfig["QB"]) > 0): combinedRankings["QB"] = generate_combined_rankings(redraftRankings["QB"], dynastyRankings["QB"] if dynastyRankings["QB"] else dynastyRankings["FLEX"])
    if dynastyRankings["FLEX"] and ("RB" in startingRosterConfig and int(startingRosterConfig["RB"]) > 0): combinedRankings["RB"] = generate_combined_rankings(redraftRankings["RB"], dynastyRankings["RB"] if dynastyRankings["RB"] else dynastyRankings["FLEX"])
    if dynastyRankings["FLEX"] and ("WR" in startingRosterConfig and int(startingRosterConfig["WR"]) > 0): combinedRankings["WR"] = generate_combined_rankings(redraftRankings["WR"], dynastyRankings["WR"] if dynastyRankings["WR"] else dynastyRankings["FLEX"])
    if dynastyRankings["FLEX"] and ("TE" in startingRosterConfig and int(startingRosterConfig["TE"]) > 0): combinedRankings["TE"] = generate_combined_rankings(redraftRankings["TE"], dynastyRankings["TE"] if dynastyRankings["TE"] else dynastyRankings["FLEX"])
    if "IDP" in dynastyRankings and dynastyRankings["IDP"]: combinedRankings["IDP"] = generate_combined_rankings(redraftRankings["IDP"], dynastyRankings["IDP"])
    if "IDP" in dynastyRankings and dynastyRankings["IDP"] and ("DL" in startingRosterConfig and int(startingRosterConfig["DL"]) > 0): combinedRankings["DL"] = generate_combined_rankings(redraftRankings["DL"], dynastyRankings["DL"] if dynastyRankings["DL"] else dynastyRankings["IDP"])
    if "IDP" in dynastyRankings and dynastyRankings["IDP"] and ("LB" in startingRosterConfig and int(startingRosterConfig["LB"]) > 0): combinedRankings["LB"] = generate_combined_rankings(redraftRankings["LB"], dynastyRankings["LB"] if dynastyRankings["LB"] else dynastyRankings["IDP"])
    if "IDP" in dynastyRankings and dynastyRankings["IDP"] and ("DB" in startingRosterConfig and int(startingRosterConfig["DB"]) > 0): combinedRankings["DB"] = generate_combined_rankings(redraftRankings["DB"], dynastyRankings["DB"] if dynastyRankings["DB"] else dynastyRankings["IDP"])

    allRankings = OrderedDict()
    allRankings["Redraft Starter Rankings"] = generate_league_rankings(league=league, leagueRosters=leagueRosters, rankings=redraftRankings, kickerRankings=kickerRankings,
        dstRankings=dstRankings, startingRosterConfig=startingRosterConfig, depth=False)
    if dynastyRankings["FLEX"]: allRankings["Dynasty Starter Rankings"] = generate_league_rankings(league=league, leagueRosters=leagueRosters, rankings=dynastyRankings, kickerRankings=kickerRankings,
        dstRankings=dstRankings, startingRosterConfig=startingRosterConfig, depth=False)
    if dynastyRankings["FLEX"]: allRankings["Combined Starter Rankings"] = generate_league_rankings(league=league, leagueRosters=leagueRosters, rankings=combinedRankings, kickerRankings=kickerRankings,
        dstRankings=dstRankings, startingRosterConfig=startingRosterConfig, depth=False)
    allRankings["Redraft Depth Rankings"] = generate_league_rankings(league=league, leagueRosters=leagueRosters, rankings=redraftRankings, kickerRankings=kickerRankings,
        dstRankings=dstRankings, startingRosterConfig=startingRosterConfig, depth=True)
    if dynastyRankings["FLEX"]: allRankings["Dynasty Depth Rankings"] = generate_league_rankings(league=league, leagueRosters=leagueRosters, rankings=dynastyRankings, kickerRankings=kickerRankings,
        dstRankings=dstRankings, startingRosterConfig=startingRosterConfig, depth=True)
    if dynastyRankings["FLEX"]: allRankings["Combined Depth Rankings"] = generate_league_rankings(league=league, leagueRosters=leagueRosters, rankings=combinedRankings, kickerRankings=kickerRankings,
        dstRankings=dstRankings, startingRosterConfig=startingRosterConfig, depth=True)

    ageRankings = generate_age_rankings(leagueHost=leagueHost, leagueRosters=leagueRosters)
    if ageRankings:
        allRankings["Age Rankings"] = ageRankings

    allRankings["League Name"] = league.name

    return allRankings

def generate_league_rankings(league=None, leagueRosters={}, rankings=[], kickerRankings=[], dstRankings=[], startingRosterConfig=OrderedDict(), depth=False):
    if not league:
        log_and_raise_error("League not provided")
    if (not leagueRosters):
        log_and_raise_error("Must provide league rosters.")
    if (not rankings):
        log_and_raise_error("Must provide rankings.")
    if (not "FLEX" in rankings  or not rankings["FLEX"]):
        log_and_raise_error("Must provide FLEX rankings.")
    if (not startingRosterConfig):
        log_and_raise_error("Must provide starting roster config.")
    if ("K" in startingRosterConfig and int(startingRosterConfig["K"]) > 0 and not kickerRankings):
        log_and_raise_error("Must provide kicker rankings.")
    if ("DST" in startingRosterConfig and int(startingRosterConfig["DST"]) > 0 and not dstRankings):
        log_and_raise_error("Must provide dst rankings.")

    logger.debug("Generating league rankings for league: %s, startingRosterConfig: %s, depth: %s" % (league, startingRosterConfig, depth))

    leagueRostersCopy = copy_league_rosters(leagueRosters)

    maxDstRankings = len(dstRankings) + UNRANKED_PENALTY
    maxKickerRankings = len(kickerRankings) + UNRANKED_PENALTY
    maxPositionRankings = {}
    maxPositionRankings["FLEX"] = len(rankings["FLEX"]) + UNRANKED_PENALTY
    if "IDP" in rankings: maxPositionRankings["IDP"] = len(rankings["IDP"]) + UNRANKED_PENALTY
    for position, num in startingRosterConfig.iteritems():
        if int(num) > 0 and position != "K" and position != "DST" and position != "FLEX" and position != "IDP":
            if rankings[position]:
                maxPositionRankings[position] = len(rankings[position]) + UNRANKED_PENALTY
            else:
                if position in FLEX_POSITIONS or position == "QB":
                    maxPositionRankings[position] = maxPositionRankings["FLEX"]
                else:
                    maxPositionRankings[position] = maxPositionRankings["IDP"]

    for team in leagueRostersCopy:
        for player in leagueRostersCopy[team]["roster"]:
            player["rank"] = sys.maxint if not player["position"] in maxPositionRankings else maxPositionRankings[player["position"]]
            player["flexRank"] = sys.maxint if not "FLEX" in maxPositionRankings else maxPositionRankings["FLEX"]
            player["idpRank"] = sys.maxint if not "IDP" in maxPositionRankings else maxPositionRankings["IDP"]
            if player["position"] == "DST" and "DST" in startingRosterConfig and int(startingRosterConfig["DST"]) > 0:
                try:
                    rankedTeam = next(x for x in dstRankings if league.is_same_player(player=player, rankedPlayer=x))
                    player["rank"] = int(rankedTeam["rank"])
                    if "team" in rankedTeam: player["team"] = rankedTeam["team"]
                except:
                    player["rank"] = maxDstRankings
            elif player["position"] == "K" and "K" in startingRosterConfig and int(startingRosterConfig["K"]) > 0:
                try:
                    rankedPlayer = next(x for x in kickerRankings if league.is_same_player(player=player, rankedPlayer=x))
                    player["rank"] = int(rankedPlayer["rank"])
                    player["name"] = rankedPlayer["name"]
                    if "team" in rankedPlayer: player["team"] = rankedPlayer["team"]
                except:
                    player["rank"] = maxKickerRankings
            else:
                playerPosition = player["position"]
                if not playerPosition in rankings:
                    if playerPosition in FLEX_POSITIONS:
                        playerPosition = "FLEX"
                    elif playerPosition in IDP_POSITIONS:
                        playerPosition = "IDP"
                if playerPosition in rankings:
                    try:
                        positionRankings = rankings[playerPosition]
                        if not positionRankings:
                            if playerPosition in FLEX_POSITIONS or playerPosition == "QB":
                                positionRankings = rankings["FLEX"]
                            else:
                                positionRankings = rankings["IDP"]
                        rankedPlayer = next(x for x in positionRankings if league.is_same_player(player=player, rankedPlayer=x))
                        player["rank"] = int(rankedPlayer["rank"])
                        if playerPosition == "FLEX":
                            player["flexRank"] = player["rank"]
                        elif playerPosition == "IDP":
                            player["idpRank"] = player["rank"]
                        if playerPosition in FLEX_POSITIONS and "FLEX" in rankings:
                            try:
                                rankedFlexPlayer = next(x for x in rankings["FLEX"] if league.is_same_player(player=player, rankedPlayer=x))
                                player["flexRank"] = int(rankedFlexPlayer["rank"])
                            except:
                                pass
                        elif playerPosition in IDP_POSITIONS and "IDP" in rankings:
                            try:
                                rankedIdpPlayer = next(x for x in rankings["IDP"] if league.is_same_player(player=player, rankedPlayer=x))
                                player["idpRank"] = int(rankedIdpPlayer["rank"])
                            except:
                                pass
                        player["name"] = rankedPlayer["name"]
                        if "team" in rankedPlayer: player["team"] = rankedPlayer["team"]
                    except:
                        player["rank"] = maxPositionRankings[playerPosition]

    rankings = []
    for team in leagueRostersCopy:
        roster = leagueRostersCopy[team]["roster"]

        qbs = sorted([x for x in roster if x["position"] == "QB"], key=lambda (v): v["rank"])
        wrs = sorted([x for x in roster if x["position"] == "WR"], key=lambda (v): v["rank"])
        rbs = sorted([x for x in roster if x["position"] == "RB"], key=lambda (v): v["rank"])
        tes = sorted([x for x in roster if x["position"] == "TE"], key=lambda (v): v["rank"])
        ks = sorted([x for x in roster if x["position"] == "K"], key=lambda (v): v["rank"])
        dsts = sorted([x for x in roster if x["position"] == "DST"], key=lambda (v): v["rank"])
        flexes = sorted([x for x in roster if x["position"] == "WR" or x["position"] == "RB" or x["position"] == "TE"], key=lambda (v): v["flexRank"])
        idps = sorted([x for x in roster if x["position"] == "DL" or x["position"] == "LB" or x["position"] == "DB"], key=lambda (v): v["idpRank"])
        dls = sorted([x for x in roster if x["position"] == "DL"], key=lambda (v): v["rank"])
        lbs = sorted([x for x in roster if x["position"] == "LB"], key=lambda (v): v["rank"])
        dbs = sorted([x for x in roster if x["position"] == "DB"], key=lambda (v): v["rank"])

        bestRosterScore = 0
        bestRoster = []

        for i in range(0, DEPTH_MULTIPLIER):
            if not depth and i > 0:
                break

            for position in startingRosterConfig:
                # If this is depth, skip the non depth positions
                if depth and i > 0 and (position == "K" or position == "DST"):
                    continue

                pos = []
                cleanFlex = True
                cleanFlexPositions = False
                cleanIdp = False
                cleanIdpPositions = False
                if position == "QB":
                    pos = qbs
                elif position == "RB":
                    pos = rbs
                elif position == "WR":
                    pos = wrs
                elif position == "TE":
                    pos = tes
                elif position == "FLEX":
                    pos = flexes
                    cleanFlex = False
                    cleanFlexPositions = True
                elif position == "K":
                    pos = ks
                    cleanFlex = False
                elif position == "DST":
                    pos = dsts
                    cleanFlex = False
                elif position == "IDP":
                    pos = idps
                    cleanFlex = False
                    cleanIdp = False
                    cleanIdpPositions = True
                elif position == "DL":
                    pos = dls
                    cleanFlex = False
                    cleanIdp = True
                elif position == "LB":
                    pos = lbs
                    cleanFlex = False
                    cleanIdp = True
                elif position == "DB":
                    pos = dbs
                    cleanFlex = False
                    cleanIdp = True

                numberOfSpots = startingRosterConfig[position]

                for j in range(0, numberOfSpots):
                    if pos:
                        originalPlayer = pos.pop(0)
                        player = copy.deepcopy(originalPlayer)
                        bestRoster.append(player)

                        if position == "FLEX" and "flexRank" in player:
                            player["rank"] = player["flexRank"]
                            player["position"] = "FLEX"
                        elif position == "IDP" and "idpRank" in player:
                            player["rank"] = player["idpRank"]
                            player["position"] = "IDP"

                        bestRosterScore += player["rank"]

                        if cleanFlex:
                            if originalPlayer in flexes: flexes.remove(originalPlayer)
                        if cleanFlexPositions:
                            if originalPlayer in rbs: rbs.remove(originalPlayer)
                            if originalPlayer in wrs: wrs.remove(originalPlayer)
                            if originalPlayer in tes: tes.remove(originalPlayer)
                        if cleanIdp:
                            if originalPlayer in idps: idps.remove(originalPlayer)
                        if cleanIdpPositions:
                            if originalPlayer in dls: dls.remove(originalPlayer)
                            if originalPlayer in lbs: lbs.remove(originalPlayer)
                            if originalPlayer in dbs: dbs.remove(originalPlayer)
                    else:
                        depthPenalty = 0
                        if position == "K":
                            depthPenalty = maxKickerRankings
                        elif position == "DST":
                            depthPenalty = maxDstRankings
                        else:
                            depthPenalty = maxPositionRankings[position]
                        bestRoster.append({"name": "Depth Penalty", "position": position, "rank": depthPenalty, "team": "NA"})
                        bestRosterScore += depthPenalty

        rankings.append({"team": team, "roster": bestRoster, "score": bestRosterScore})

    rankings = sorted(rankings, key=lambda (v): v["score"])
    return rankings

def generate_combined_rankings(redraftRankings=[], dynastyRankings=[]):
    if (not redraftRankings):
        log_and_raise_error("Must provide redraft rankings.")
    if (not dynastyRankings):
        log_and_raise_error("Must provide dynasty rankings.")

    biggerRankings = redraftRankings
    smallerRankings = dynastyRankings

    if len(dynastyRankings) > len(redraftRankings):
        biggerRankings = dynastyRankings
        smallerRankings = redraftRankings

    maxBiggerRankings = len(biggerRankings) + UNRANKED_PENALTY
    maxSmallerRankings = len(smallerRankings) + UNRANKED_PENALTY

    combinedRankings = copy.deepcopy(biggerRankings)

    for player in combinedRankings:
        found = False
        for player2 in smallerRankings:
            if player["name"].lower() == player2["name"].lower() and (("team" in player and player["team"] == player2["team"]) or ("team" not in player)) and player["position"] == player2["position"]:
                player["rank"] += player2["rank"]
                found = True
                break
        if not found:
            player["rank"] += maxSmallerRankings

    combinedRankings = sorted(combinedRankings, key=lambda (v): v["rank"])

    return combinedRankings

def generate_age_rankings(leagueHost="fleaflicker", leagueRosters={}):
    if not (leagueHost == "fleaflicker" or leagueHost == "myfantasyleague" or leagueHost == "yahoo"):
        log_and_raise_error("Invalid league host: %s" % leagueHost)
    if (not leagueRosters):
        log_and_raise_error("Must provide league rosters.")
    ageRankings = []

    logger.debug("Generating age rankings for leagueHost: %s" % (leagueHost))

    leagueRostersCopy = copy_league_rosters(leagueRosters)

    for team in leagueRostersCopy:
        agePlayers = []
        totalAge = 0
        roster = leagueRostersCopy[team]["roster"]
        for player in roster:
            if "age" in player and player["age"] != 0:
                totalAge += player["age"]
                agePlayers.append(player)
                player["rank"] = player["age"]

        ageCount = len(agePlayers)
        if totalAge > 0 and ageCount > 0:
            averageAge = float(totalAge) / float(ageCount)
            agePlayers = sorted(agePlayers, key=lambda (v): v["age"])
            ageRankings.append({"team": team, "roster": agePlayers, "score": "%0.3f" % averageAge})

    if ageRankings:
        ageRankings = sorted(ageRankings, key=lambda (v): v["score"])

    return ageRankings
