import pytest
import requests
from requests import codes
import logging
import json
from faker import Faker
import random
from random import randint
import urllib
import time

from ..auth import get_Token_UsernamePassword
from ..products import get_Products, patch_Product
from ..me import get_meProducts


fake = Faker()

log = logging.getLogger(__name__)



def sessionInit(configInfo):

	client_id = configInfo['ADMIN-CLIENTID']
	username = configInfo['ADMIN-USERNAME']
	password = configInfo['ADMIN-PASSWORD']
	scope = ['FullAccess']

	# can successfully get a token
	adminToken = get_Token_UsernamePassword(configInfo, client_id, username, password, scope)

	client_id = configInfo['BUYER-CLIENTID']
	username = configInfo['BUYER-USERNAME']
	password = configInfo['BUYER-PASSWORD']
	scope = ['Shopper']

	buyerToken = get_Token_UsernamePassword(configInfo, client_id, username, password, scope)


	buyer = requests.Session()

	headers = {
		'Authorization': 'Bearer ' + buyerToken['access_token'],
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	buyer.headers.update(headers)


	admin = requests.Session()

	headers = {
		'Authorization': 'Bearer ' + adminToken['access_token'],
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	admin.headers.update(headers)


	#log.info(json.dumps(buyer.get(configInfo['API']+'v1/me').json(), indent=4))
	#log.info(json.dumps(admin.get(configInfo['API']+'v1/me').json(), indent=4))

	return(buyer, admin)
