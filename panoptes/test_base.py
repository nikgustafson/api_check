#! tests_base.py

import pytest
import requests
from requests import codes
import logging
import json


log = logging.getLogger(__name__)


def test_fixtures_for_options(apiEnv):

	log.info('api environment set to: '+str(apiEnv))

def test_configData(configInfo):

	log.info('API: '+ configInfo['API'])
	log.info('AUTH: '+ configInfo['AUTH'])

def test_api_env_vars(configInfo, apiEnv):

	env = requests.get(configInfo['API']+'env')
	assert env.status_code is codes.ok
	log.info('API ENV: '+ json.dumps(env.json(), indent=2))

	authEnv = requests.get(configInfo['AUTH']+'env')
	assert authEnv.status_code is codes.ok
	log.info('AUTH ENV: '+ json.dumps(authEnv.json(), indent=2))

	intEnv = requests.get(configInfo['INTEGRATIONS']+'env')
	assert intEnv.status_code is codes.ok
	log.info('INTEGRATIONS ENV: '+ json.dumps(intEnv.json(), indent=2))

	assert str.lower(env.json()['Environment']) == str.lower(apiEnv)

	assert authEnv.json() == env.json()
	assert authEnv.json() == intEnv.json()