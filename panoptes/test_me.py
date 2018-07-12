#! tests_me.py


import pytest
import requests
from requests import codes
import logging
import json



log = logging.getLogger(__name__)


def get_Me(configInfo, token):

	if type(token) is dict:
		token = token['access_token']

	headers = {
		'Authorization': 'Bearer '+ token,
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	me = requests.get(configInfo['API']+'v1/me', headers = headers)

	#log.debug(me.request.headers)
	#log.debug(me.request.body)
	log.debug(json.dumps(me.json(), indent=2))
	assert me.status_code is codes.ok

	return me.json()


def patch_Me(configInfo, token, newUser):

	headers = {
		'Authorization': 'Bearer '+token['access_token'],
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	payload = newUser

	me = requests.patch(configInfo['API']+'v1/me', json= newUser, headers = headers)

	#log.debug(me.request.headers)
	#log.debug(me.request.body)
	log.debug(json.dumps(me.json(), indent=2))
	assert me.status_code is codes.ok

	return me.json()
