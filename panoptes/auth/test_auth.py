#! tests_auth.py


import pytest
import requests
from requests import codes
import logging
import json


from ..auth import get_Token_UsernamePassword, post_resetPassword
from .. import me



log = logging.getLogger(__name__)



#-----------------------------------------#
#             tests begin                 #
#-----------------------------------------#

log.info('Auth Tests Begun...')
@pytest.mark.smoke
@pytest.mark.description('''Given a buyer user\'s username, password, and client-id,\n
						when the user attempts to get a token via Username/Password Grant,\n
						then the user receives a valid auth token with the expected roles and can use it to make calls''')
def test_usernamePasswordGrant(configInfo):

	client_id = configInfo['BUYER-CLIENTID']
	username = configInfo['BUYER-USERNAME']
	password = configInfo['BUYER-PASSWORD']
	scope = ['Shopper', 'MeAdmin']


	# can successfully get a token
	token = get_Token_UsernamePassword(configInfo, client_id, username, password, scope)

	# can use that token to make calls 

	user = me.get_Me(configInfo, token['access_token'])

@pytest.mark.smoke
@pytest.mark.description('''Given a buyer with anonymous shopping enabled,\n
						When an unregistered user authenticates as an Anonymous Shopper\n
						Then they can register themselves as a new buyer user for the org.''')
def test_anonGrant():
	pass

@pytest.mark.smoke
@pytest.mark.skip(reason='Unimplemented currently.')
@pytest.mark.description('''Given a client id and client secret,\n
						When a user/backend system attempts to get an auth token via Client Credentials Grant,\n
						Then they receive a valid auth token with the expected roles and make calls to the API.''')
def test_clientCredentialsGrant():
	pass



