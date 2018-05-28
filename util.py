import httplib
import config
from config import logger, pp, log_and_raise_error
if config.mode != "development":
    import urllib3.contrib.pyopenssl
if config.mode != "development":
    urllib3.contrib.pyopenssl.inject_into_urllib3()
import requests
import datetime
from config import logger
import copy

from HTMLParser import HTMLParser
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def years_ago(years, from_date=None):
    if from_date is None:
        from_date = datetime.datetime.now()
    try:
        return from_date.replace(year=from_date.year - years)
    except ValueError:
        # Must be 2/29!
        return from_date.replace(month=2, day=28,
                                 year=from_date.year-years)

def num_years_since(begin, end=None):
    if end is None:
        end = datetime.datetime.now()
    numYears = int((end - begin).days / 365.2425)
    if begin > years_ago(numYears, end):
        return numYears - 1
    else:
        return numYears

def read_page(url):
    page = ""
    try:
        logger.debug("Reading page at: %s" % (url))
        response = requests.get(url)
        page = response.text
    except requests.exceptions.RequestException as e:
        logger.error("RequestException = %s" % str(e))
    except Exception:
        import traceback
        logger.error("Generic exception: %s" % traceback.format_exc())
    return page

def copy_league_rosters(leagueRosters):
    leagueRostersCopy = {}
    for team in leagueRosters:
        leagueRostersCopy[team] = copy.deepcopy(leagueRosters[team])
    return leagueRostersCopy
