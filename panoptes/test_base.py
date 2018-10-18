#! tests_base.py

import pytest
import requests
from requests import codes
import logging
import json
import sys
import tempfile
from pathlib import Path
import random

from . import me
from . import getConfigData
from .helpers import blns

log = logging.getLogger(__name__)

blns_list = blns.list
log.info(type(blns_list))


def test_fixtures_for_options(configInfo):

    log.info('api environment set to: ' + str(configInfo))


def test_configData(configInfo):

    log.info(getConfigData(configInfo))


@pytest.mark.skip
@pytest.mark.smoke
@pytest.mark.description('Verifies that the ENVs reported for API, AUTH, INTEGRATIONS are a) responding and b) consistent.')
def test_api_env_vars(configInfo):

    try:
        env = requests.get(configInfo['API'] + 'env')
        assert env.status_code is codes.ok
        log.info('API ENV: ' + json.dumps(env.json(), indent=2))
    except:

        log.info('API Service is not available.')
        pytest.exit(pytest.main())
        raise

    try:
        authEnv = requests.get(configInfo['AUTH'] + 'env')
        assert authEnv.status_code is codes.ok
        log.info('AUTH ENV: ' + json.dumps(authEnv.json(), indent=2))
    except:
        log.info('Auth Service is not available')
        pytest.exit(pytest.main())
        raise

    try:
        intEnv = requests.get(configInfo['INTEGRATIONS'] + 'env')
        assert intEnv.status_code is codes.ok
        log.info('INTEGRATIONS ENV: ' + json.dumps(intEnv.json(), indent=2))
    except:
        log.info("Integrations Service is not available")
        pytest.exit(pytest.main())
        raise

    assert str.lower(env.json()['Environment']) == str.lower(
        getConfigData(configInfo))

    assert authEnv.json() == env.json()
    assert authEnv.json() == intEnv.json()


def test_sessionfixture(configInfo, connections):

    log.info(json.dumps(
        connections['buyer'].get(configInfo['API'] + 'v1/me').json(), indent=4))
    log.info(json.dumps(
        connections['admin'].get(configInfo['API'] + 'v1/me').json(), indent=4))


@pytest.mark.parametrize("sessions", ['buyer', 'anon'])
@pytest.mark.parametrize("a_blns", random.sample(blns_list, 7))
#@pytest.mark.parametrize("a_blns", blns_list)
def test_blns(configInfo, connections, sessions, a_blns):

    session = connections[sessions]

    try:
        naughtyString = session.get(configInfo['API'] + 'v1/' + a_blns + '/')

        '''
        if naughtyString.status_code != codes.not_found:
            log.debug(str(naughtyString.url))
            log.debug(str(naughtyString.status_code))
            log.debug(naughtyString.text)
        '''
        #assert naughtyString.status_code == codes.not_found

    except:
        raise


@pytest.mark.parametrize("endpoint", [
    "",
    "products",
    "costcenters",
    "usergroups",
    "addresses",
    "creditcards",
    "categories",
    "orders",
    "promotions",
    "spendingAccounts",
    "shipments",
    "catalogs"

])
#@pytest.mark.parametrize("sessions", ['buyer', 'anon'])
@pytest.mark.parametrize("a_blns", random.sample(blns_list, 3))
#@pytest.mark.parametrize("a_blns", blns_list)
@pytest.mark.skip()
def test_blns_endpoints(configInfo, connections, a_blns, endpoint):

    reportLoc = Path('C:/Users/kreeher/AppData/Local/Temp/panoptes/logs/')
    reportLoc.mkdir(mode=0o777, parents=True, exist_ok=True)
    reportFile = Path(reportLoc, 'blns_endpoints.csv')
    log.info('tempdoc: ' + repr(reportLoc))

    reportList = []

    #session = connections[sessions]
    session = connections['buyer']
    try:
        naughtyString = session.get(
            configInfo['API'] + 'v1/' + endpoint + '/' + a_blns + '/')

        if naughtyString.status_code != '404':
            log.info(naughtyString.status_code)
            report = {
                "Naughty String": a_blns,
                "Request URL": naughtyString.url,
                "Status Code": naughtyString.status_code
                #,
                #"Response Text": naughtyString.text
            }
            # log.info(report.values())
            reportList.append(report)
        #assert naughtyString.status_code == codes.not_found

    except:
        raise

    csv = reportFile.open("a")
    #"w" indicates that you're writing strings to the file

    # columnTitleRow = "naughtyString, requestURL, statusCode, responseText\n"
    # csv.write(columnTitleRow)

    # log.info(len(reportList))

    for item in reportList:
        row = ''
        for data in item.values():
            escaped = str(data).translate(str.maketrans({".":  r"\.",
                                                         ",":  r"\,"}))
            row += (repr(escaped) + ',')
        row += '\n'
        csv.write(row)
