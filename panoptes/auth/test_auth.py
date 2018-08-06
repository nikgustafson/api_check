#! tests_auth.py


import pytest
import requests
from requests import codes
import logging
import json
from auth import get_Token_UsernamePassword, post_resetPassword

import me



log = logging.getLogger(__name__)



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

	user = me.get_Me(configInfo, token['access_token'])


@pytest.mark.description("Given a buyer with anonymous shopping enabled, a user can authenticate as an anon user and register themselves as a buyer user for the org.")
def test_anonGrant():
	pass


@pytest.mark.description("Given a client id and client secret, can get a client credentials token and make calls to the api.")
def test_clientCredentialsGrant():
	pass



