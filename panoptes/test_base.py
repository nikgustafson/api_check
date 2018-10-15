#! tests_base.py

import pytest
import requests
from requests import codes
import logging
import json
import sys

from . import me
from . import getConfigData

log = logging.getLogger(__name__)


def test_fixtures_for_options(configInfo):

    log.info('api environment set to: ' + str(configInfo))


def test_configData(configInfo):

    log.info(getConfigData(configInfo))


@pytest.mark.smoke
@pytest.mark.description('Verifies that the ENVs reported for API, AUTH, INTEGRATIONS are a) responding and b) consistent.')
def test_api_env_vars(configInfo):

    try:
        env = requests.get(configInfo['API'] + 'env')
        assert env.status_code is codes.ok
        log.info('API ENV: ' + json.dumps(env.json(), indent=2))
    except:
        pytest.main()
        log.info('API Service is not available.')
        raise

    try:
        authEnv = requests.get(configInfo['AUTH'] + 'env')
        assert authEnv.status_code is codes.ok
        log.info('AUTH ENV: ' + json.dumps(authEnv.json(), indent=2))
    except:
        pytest.main()
        log.info('Auth Service is not available')

    try:
        intEnv = requests.get(configInfo['INTEGRATIONS'] + 'env')
        assert intEnv.status_code is codes.ok
        log.info('INTEGRATIONS ENV: ' + json.dumps(intEnv.json(), indent=2))
    except:
        pytest.main()
        log.info("Integrations Service is not available")

    assert str.lower(env.json()['Environment']) == str.lower(
        getConfigData(configInfo))

    assert authEnv.json() == env.json()
    assert authEnv.json() == intEnv.json()
