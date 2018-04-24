#filter user workflow tests
import requests
from requests import codes as codes
import pytest
import configparser
import json
import logging
import datetime
import urllib
from random import randint
from faker import Faker
fake = Faker()

logging.basicConfig(filename='testRun.log', level=logging.DEBUG, filemode = 'w')
log = logging.getLogger('userWorkflow')

config = configparser.ConfigParser()
config.read('../config.ini')
auth = config['LOCUST-AUTH']

environments = {'api':['api', 'qaapi'], 'auth':['auth', 'qaauth']}

# Authentication

def getTokenBuyer(buyerUsername, buyerPassword, scope = ''):
	log = logging.getLogger('getTokenBuyer')
	payload = {
	'client_id':auth['buyerClientID'],
	'grant_type': 'password',
	'username' : buyerUsername,
	'password':buyerPassword,
	'Scope': scope
	}
	headers = {'Content-Type':'application/json'}
	r = requests.post('https://auth.ordercloud.io/oauth/token', data = payload, headers = headers)

	return(r.json()['access_token'])

# Me List Endpoints

def getMeToken(token):
	log.debug('getMe')
	token = token
	log.debug('token: '+ token)
	headers = {'Content-Type':'application/json', 'Authorization':'Bearer '+ token}
	log.debug('headers: ')
	log.debug(headers)
	r = requests.get('https://api.ordercloud.io/v1/me', headers = headers)
	return(r)

def getMe(buyerUsername= '', buyerPassword = '', scope = ''):
	log.debug('getMe')
	token = getTokenBuyer(buyerUsername, buyerPassword, scope)
	log.debug('token: '+ token)

	r = getMeToken(token)
	
	return(r)

def getMeProducts(buyerUsername, buyerPassword, search='', productID = ''):

	if productID != '':
		productID = '/'+productID

	log.debug('getMeProducts')
	token = getTokenBuyer(buyerUsername, buyerPassword, 'Shopper')
	log.debug('token: '+ token)
	headers = {'Content-Type':'application/json', 'Authorization':'Bearer '+ token}
	log.debug('headers: ')
	log.debug(headers)
	r = requests.get('https://api.ordercloud.io/v1/me/products'+productID, headers = headers, params = search)
	return(r)

#1
def test_MeGet():
	# get me succeeds, and user is active
	log.debug('test_userMe')
	user = getMe(auth['buyerUsername'], auth['buyerPassword'], 'Shopper')
	log.debug('user: ')
	log.debug(user.json())
	assert user.status_code == 200
	assert user.is_redirect is False
	assert user.json()['Username'] == auth['buyerUsername']
	assert user.json()['Active'] == True
	log.info(user)
#2
def test_MeProduct():
	log.debug('test_MeProduct')

	log.debug('test_MeProduct: Product List')
	productList = getMeProducts(auth['buyerUsername'], auth['buyerPassword'])
	log.debug(productList.url)
	assert productList.status_code == 200
	assert productList.is_redirect is False

	assert productList.json()['Meta']['TotalCount'] > 5
	randProduct = productList.json()['Items'][randint(0, productList.json()['Meta']['PageSize']-1)]
	log.info("Random Product: "+ str(randProduct))

	log.debug('test_MeProduct: Product GET')
	productList = getMeProducts(auth['buyerUsername'], auth['buyerPassword'], productID = randProduct['ID'])
	log.debug(productList.url)
	log.debug(str(randProduct['ID']))

	assert productList.status_code == 200
	assert productList.is_redirect is False
	#log.info("Product List: "+str(productList))


searchParams =	(["catalogID", "smokebuyer01"],["search", "*w*"],["sortBy", "name"],["page", 5],["pageSize", 100])
#filterParams =

ids = []

for item in searchParams:
	ids.append(item[0]+'-'+str(item[1]))


@pytest.mark.parametrize("searchParams", searchParams, ids= ids,)

#3
def test_MeProductFilter(searchParams):

	allProducts = getMeProducts(auth['buyerUsername'], auth['buyerPassword'])
	log.debug(allProducts.url)
	assert allProducts.status_code == 200
	totalProducts = allProducts.json()['Meta']['TotalCount']
	totalPages = allProducts.json()['Meta']['TotalPages']
	log.debug(totalProducts)
	log.debug(totalPages)

	# filters

	log.debug('test_MeProductFilter '+str(searchParams[0])+' expects '+str(searchParams[1]))

	filters = {searchParams[0]:str(searchParams[1])}
	print(filters)

	filterProducts = getMeProducts(auth['buyerUsername'], auth['buyerPassword'], filters)
	log.debug(filterProducts.url)
	assert allProducts.status_code == 200
	assert filterProducts.url == ('https://api.ordercloud.io/v1/me/products?'+str(searchParams[0])+'='+urllib.parse.quote_plus(str(searchParams[1])))
	filterProducts = allProducts.json()['Meta']['TotalCount']
	filterPages = allProducts.json()['Meta']['TotalPages']
	log.debug(filterProducts)
	log.debug(filterPages)


# what we want: 'catalogID','search',"sortBy","page","pageSize" x filters


def meCardCreate(username, password):
	log.debug('ME: Create Credit Card ')

	user = getMe(username, password, 'MeCreditCardAdmin')
	# TODO: refactor scope to be array of strings
	assert user.status_code == codes.ok

	headers = user.request.headers
	#assert headers.json()['Authorization'] TODO: to be able to assert user has current priv, add jwt decode
	log.debug(headers)
	log.debug(json.dumps(user.json(), indent=2))

	cardNumber = fake.credit_card_number(card_type=None)

	fullCard = {
	"BuyerID": '',
	"TransactionType": "createCreditCard",
	"CardDetails": {
	"CardholderName":  user.json()['FirstName']+' '+user.json()['LastName'],
	"CardType": fake.credit_card_provider(card_type=None),
	"CardNumber": cardNumber,
	"ExpirationDate": fake.credit_card_expire(start="now", end="+10y", date_format="%Y/%m/%d"),
	"CardCode": cardNumber[-4:],
	"Shared": False
	}   
	}

	partialCard = {
	    "CardType": fullCard["CardDetails"]['CardType'],
	    "CardholderName": fullCard["CardDetails"]['CardholderName'],
	    "ExpirationDate": fullCard["CardDetails"]['ExpirationDate'],
	    "PartialAccountNumber": fullCard["CardDetails"]['CardCode'],
	    "Token": "",
	    "xp": {}
	}

	#log.debug(partialCard)
	log.debug(fullCard)

	card = requests.post('https://api.ordercloud.io/v1/me/creditcards', headers = headers, json = partialCard)
	log.debug(card.url)
	log.debug(card.request.body)
	log.debug(json.dumps(card.json(), indent=2))
	assert card.status_code == codes.created

	
	return(fullCard)
	
