#! tests_auth.py


import pytest
import requests
from requests import codes
import logging
import json
from faker import Faker


from ..auth import get_Token_UsernamePassword, get_Token_ClientID, post_resetPassword, get_anon_user_token
from .. import me

fake = Faker()

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
def test_anonGrant(configInfo):
		
	client_id = configInfo['BUYER-CLIENTID']
	scope = ['Shopper']


	# can successfully get a token
	token = get_anon_user_token(configInfo, client_id)

	# can use that token to make calls 

	user = me.get_Me(configInfo, token['access_token'])

	assert user['ID'] == 'anon-template'

@pytest.mark.smoke
@pytest.mark.description('''Given a client id and client secret,\n
						When a user/backend system attempts to get an auth token via Client Credentials Grant,\n
						Then they receive a valid auth token with the expected roles and make calls to the API.''')
def test_clientCredentialsGrant(configInfo):
	
	client_id = configInfo['BUYER-CLIENTID']
	scope = ['Shopper']


	# can successfully get a token
	token = get_Token_ClientID(configInfo, client_id, scope)

	# can use that token to make calls 

	user = me.get_Me(configInfo, token['access_token'])

@pytest.mark.skip
def test_updatePriceSchedules(configInfo):
	client_id = configInfo['ADMIN-CLIENTID']
	username = configInfo['ADMIN-USERNAME']
	password = configInfo['ADMIN-PASSWORD']
	scope = ['FullAccess']


	# can successfully get a token
	token = get_Token_UsernamePassword(configInfo, client_id, username, password, scope)

	# can use that token to make calls 
	session = requests.Session()

	headers = {
		'Authorization': 'Bearer '+ token['access_token'],
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	session.headers.update(headers)

	#log.info(buyer.headers)

	
	test = session.get(configInfo['API']+'v1/me')
	assert test.status_code is codes.ok
	


	priceSchedules = session.get(configInfo['API']+'v1/priceSchedules', params = { 'PageSize':'100'})
	assert priceSchedules.status_code is codes.ok

	totalCount = priceSchedules.json()['Meta']['TotalCount']
	log.info(totalCount)

	newBody = {
		"MinQuantity": '1',
		"MaxQuantity": '100',
		"UseCumulativeQuantity": False,
		"RestrictedQuantity": False,
		"PriceBreaks": [
		  {
		    "Quantity": '1',
		    "Price": '200'
		  }
		]
	}

	if totalCount <= 100:
		for item in priceSchedules.json()['Items']:
			log.info(item['ID'])
			old = session.get(configInfo['API']+'v1/priceSchedules/'+item['ID'])
			new = session.patch(configInfo['API']+'v1/priceSchedules/'+item['ID'], json = newBody)
			assert new.status_code is codes.ok


#@pytest.mark.dev
@pytest.mark.smoke
@pytest.mark.description('this test verifies that EX-1691 has been fixed')
def test_anonOrderNotFound(configInfo):


	client_id = configInfo['BUYER-CLIENTID']
	
	token = get_anon_user_token(configInfo, client_id)

	user = me.get_Me(configInfo, token['access_token'])

	anon = requests.Session()

	headers = {
		'Authorization': 'Bearer '+ token['access_token'],
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	anon.headers.update(headers)

	#log.info(buyer.headers)

	
	test = anon.get(configInfo['API']+'v1/me')
	#log.info(test.text)
	assert test.status_code is codes.ok


	products = me.get_meProducts(configInfo, token, params = None)

	#log.info(json.dumps(products, indent = 4))
	

	assert products['Meta']['TotalCount'] > 0

	productID = products['Items'][0]
	#log.info(json.dumps(productID, indent=4))
	productID = productID['ID']

	newOrder = {
		'Comments': 'boo.'
	}

	order = anon.post(configInfo['API']+'v1/orders/outgoing', json = newOrder)

	#log.info(json.dumps(order.json(), indent=4))
	assert order.status_code is codes.created

	orderID = order.json()['ID']

	newLine = {
	  "ProductID": productID,
	  "Quantity": 3,
	  "xp": {}
	}

	lineitem = anon.post(configInfo['API']+'v1/orders/outgoing/'+orderID+'/lineitems', json = newLine)
	log.debug(lineitem.status_code)
	#log.info(json.dumps(lineitem.json(), indent=4))
	assert lineitem.status_code is codes.created

	#orders = me.getMeOrders(configInfo, anon)

	#log.info(json.dumps(orders.json(), indent=4))


'''
POST @ v1/orders/outgoing
POST @ v1/orders/outgoing/STEP_1_RESPONSE_ID/lineitems
IF SUCCESSFUL
DELETE @ v1/orders/outgoing/STEP_1_RESPONSE_ID
Start again at Step 1
IF ERROR
STOP
Congratulations you've recreated the bug!
'''