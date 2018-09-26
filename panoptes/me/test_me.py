#! tests_me.py


import pytest
import requests
import random
from requests import codes
import logging
import json

from faker import Faker


from .. import auth
from ..auth import get_Token_UsernamePassword

fake=Faker()

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

	#log.info(buyer.headers)

	
	test = buyer.get(configInfo['API']+'v1/me')
	assert test.status_code is codes.ok
	#log.info(test.url)
	#log.info(test.headers)
	#log.info(test.text)

def deleteMeAddress(configInfo, session, productID):

	delete = session.delete(configInfo['API']+'v1/me/addresses/'+productID)
	log.info(delete.status_code)
	#log.info(delete.json())

	assert delete.status_code is codes.no_content
	


def createMeAddress(configInfo, session):

	newAddress = {
		"Shipping": True,
		"Billing": bool(random.getrandbits(1)),
		"CompanyName": fake.company(),
		"FirstName": fake.first_name(),
		"LastName": fake.last_name(),
		"Street1": fake.street_address(),
		"Street2": fake.secondary_address(),
		"City": fake.city(),
		"State": fake.state_abbr(),
		"Zip": fake.zipcode_plus4(),
		"Country": fake.country_code(),
		"Phone": fake.phone_number(),
		"AddressName": fake.catch_phrase(),
		"xp": {
			'fake':True
		}
	}

	create = session.post(configInfo['API']+'v1/me/addresses', json=newAddress)
	log.info(create.json())
	assert create.status_code is codes.created

@pytest.mark.smoke
@pytest.mark.description(''' Verifies that a buyer user can create a new private address.\n
						In the Smoke Tests, this verifies that the API can write to the database.''')
def test_meAddressesCreate(configInfo):

	client_id = configInfo['BUYER-CLIENTID']
	username = configInfo['BUYER-USERNAME']
	password = configInfo['BUYER-PASSWORD']
	scope = ['Shopper', 'MeAdmin', 'MeAddressAdmin']

	token = get_Token_UsernamePassword(configInfo, client_id, username, password, scope)

	buyer = requests.Session()

	headers = {
		'Authorization': 'Bearer '+ token['access_token'],
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	buyer.headers.update(headers)

	meGet = buyer.get(configInfo['API']+'v1/me')
	assert meGet.status_code is codes.ok
	log.info(json.dumps(meGet.json(), indent=4))

	addList = buyer.get(configInfo['API']+'v1/me/addresses')
	assert addList.status_code is codes.ok

	log.info(json.dumps(addList.json()))

	totalAdd = addList.json()['Meta']['TotalCount']

	# okay, we've got the initial total of addresses

	newAdd = createMeAddress(configInfo, buyer)

	# now we've created a new address

	addList2 = buyer.get(configInfo['API']+'v1/me/addresses')
	assert addList2.status_code is codes.ok

	assert addList2.json()['Meta']['TotalCount'] == totalAdd+1

@pytest.mark.smoke
@pytest.mark.description(''' Verifies that a buyer user can delete a private address.\n
						In the Smoke Tests, this verifies that the API can write deletes to the database.''')
def test_meAddressesDelete(configInfo):

	client_id = configInfo['BUYER-CLIENTID']
	username = configInfo['BUYER-USERNAME']
	password = configInfo['BUYER-PASSWORD']
	scope = ['Shopper', 'MeAdmin', 'MeAddressAdmin']

	token = get_Token_UsernamePassword(configInfo, client_id, username, password, scope)

	buyer = requests.Session()

	headers = {
		'Authorization': 'Bearer '+ token['access_token'],
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	buyer.headers.update(headers)

	meGet = buyer.get(configInfo['API']+'v1/me')
	assert meGet.status_code is codes.ok
	log.info(json.dumps(meGet.json(), indent=4))

	addList = buyer.get(configInfo['API']+'v1/me/addresses')
	assert addList.status_code is codes.ok

	log.info(json.dumps(addList.json()))

	totalAdd = addList.json()['Meta']['TotalCount']

	if totalAdd == 0:
		newAdd = createMeAddress(configInfo, buyer)
		totalAdd = totalAdd+1

	deletedAdd = addList.json()['Items'][0]['ID']
	log.info('Deleted Address ID: '+deletedAdd)

	deleteMeAddress(configInfo, buyer, deletedAdd)

	addList2 = buyer.get(configInfo['API']+'v1/me/addresses')
	assert addList2.status_code is codes.ok

	assert addList2.json()['Meta']['TotalCount'] == totalAdd-1



