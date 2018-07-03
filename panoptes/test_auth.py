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



def post_resetPassword(configInfo, token, resetUrl):
	"""
	Sends a temporary verification code via email, which must subsequently be passed in a Reset Password call.
	"""

	user = test_me.get_Me(configInfo, token)
	#log.debug(user)

	payload = {
	    'ClientID': configInfo['BUYER-CLIENTID'],
	    'Email': user['Email'],
	    'username': user['Username'],
	    'URL': resetUrl 
	}
	log.debug(json.dumps(payload, indent=2))

	headers = {
	'Content-Type': 'application/json',
	'Autentication': 'Bearer '+ token['access_token']}

	log.debug(headers)



	reset = requests.post(configInfo['API']+'v1/password/reset', json = payload, headers = headers)
	log.debug(reset)
	assert reset.status_code is codes.no_content




#-----------------------------------------#
#             tests begin                 #
#-----------------------------------------#

log.info('Auth Tests Begun...')

@pytest.mark.description("Given a buyer user's username, password, and client-id, the buyer user can get a token and use it to make calls")
def test_usernamePasswordGrant(configInfo):

	client_id = configInfo['BUYER-CLIENTID']
	username = configInfo['BUYER-USERNAME']
	password = configInfo['BUYER-PASSWORD']
	scope = ['Shopper', 'MeAdmin']


	# can successfully get a token
	token = get_Token_UsernamePassword(configInfo, client_id, username, password, scope)

	# can use that token to make calls 

	me = test_me.get_Me(configInfo, token['access_token'])


@pytest.mark.description("Given a buyer with anonymous shopping enabled, a user can authenticate as an anon user and register themselves as a buyer user for the org.")
def test_anonGrant():
	pass


@pytest.mark.description("Given a client id and client secret, can get a client credentials token and make calls to the api.")
def test_clientCredentialsGrant():
	pass



