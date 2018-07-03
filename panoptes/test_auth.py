#! tests_auth.py


import pytest
import requests
from requests import codes
import logging
import json

import test_me



log = logging.getLogger(__name__)


def get_Token_UsernamePassword(configInfo, client_id, username, password, scope = []):
	"""
	

	"""

	scopes = ' '.join(scope)


	payload = {
	    'client_id': client_id,
	    'grant_type': 'password',
	    'username': username,
	    'password': password,
	    'Scope': scopes
	}
	log.debug(payload)

	headers = {'Content-Type': 'text/html'}



	token = requests.post(configInfo['AUTH']+'oauth/token', data = payload, headers = headers)
	#log.debug(token.request.headers)
	#log.debug(token.request.body)
	log.debug(json.dumps(token.json(), indent=2))
	assert token.status_code is codes.ok

	return token.json()





#-----------------------------------------#
#             tests begin                 #
#-----------------------------------------#

log.info('Auth Tests Begun...')

def test_usernamePasswordGrant(configInfo):

	client_id = configInfo['BUYER-CLIENTID']
	username = configInfo['BUYER-USERNAME']
	password = configInfo['BUYER-PASSWORD']
	scope = ['Shopper', 'MeAdmin']


	# can successfully get a token
	token = get_Token_UsernamePassword(configInfo, client_id, username, password, scope)

	# can use that token to make calls 

	me = test_me.get_Me(configInfo, token['access_token'])





