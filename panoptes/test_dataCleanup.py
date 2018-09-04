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

from .auth import get_Token_UsernamePassword
from .products import get_Products, patch_Product
from .me import get_meProducts


fake = Faker()

log = logging.getLogger(__name__)


def test_CleanUpData(configInfo):

	client_id = configInfo['ADMIN-CLIENTID']
	username = configInfo['ADMIN-USERNAME']
	password = configInfo['ADMIN-PASSWORD']
	scope = ['FullAccess']

	adminToken = get_Token_UsernamePassword(configInfo, client_id, username, password, scope)


	admin = requests.Session()

	headers = {
		'Authorization': 'Bearer ' + adminToken['access_token'],
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	admin.headers.update(headers)

	productList = admin.get(configInfo['API']+'v1/Products', params={'xp.sizes': '*'})

	assert productList.status_code is codes.ok

	#log.info(json.dumps(productList.json(), indent=4))

	products = productList.json()['Items']

	for item in products:
		log.info(json.dumps(item['xp'], indent=4))

		removeXP = admin.patch(configInfo['API']+'v1/Products/'+item['ID']+'/', json= {'xp': None})
		assert removeXP.status_code is codes.ok
		log.info(json.dumps(removeXP.json(), indent=4))