#! tests_me.py


import pytest
import requests
from requests import codes
import logging
import json
import me
import auth

log = logging.getLogger(__name__)


def test_sessions(configInfo):

	client_id = configInfo['BUYER-CLIENTID']
	username = 'dbrown'
	password = 'fails345!!'
	scope = ['Shopper']

	buyerToken = auth.get_Token_UsernamePassword(configInfo, client_id, username, password, scope)

	buyer = requests.Session()

	headers = {
		'Authorization': 'Bearer '+ buyerToken['access_token'],
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	buyer.headers.update(headers)
	
	log.info(buyer.get(configInfo['API']+'v1/me').json())