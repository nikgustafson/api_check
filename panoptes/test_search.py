import pytest
import requests
from requests import codes
import logging
import json

from test_auth import get_Token_UsernamePassword
from test_products import get_Products, patch_Product
from test_me import get_meProducts
from faker import Faker
import urllib

import time

fake=Faker()

log = logging.getLogger(__name__)


def createProductFacet(configInfo, products, token):

	newXP = {
		"xp": {
			"blue" : True
		}
	}

	log.debug(newXP)
	newProducts = []
	for item in products:
		log.debug(item['ID'])
		product = patch_Product(configInfo, token, item['ID'], params = '', body= newXP)
		log.debug(product)
		newProducts.append(product)

	return newProducts


log.debug('Search Tests Begun...')

@pytest.mark.description("Test verifies that search works over xp and nested xp, and notates the performance")

def test_productSearch(configInfo):

	# auth as an admin user

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

	# add xp to products

	search = {
		'search': 'blue',
		'searchOn': 'xp.*'

	}


	products = get_meProducts(configInfo, buyerToken, search) # admin sear h

	log.debug(products['Meta'])

	if products['Meta']['TotalCount'] == 0:
		log.debug("Time to make more XP!")

		params = { 
			'pageSize': '5',
			'page': '3'
		}
		products = get_meProducts(configInfo, buyerToken, params)
		patchedProducts = createProductFacet(configInfo, products['Items'], adminToken)
		log.debug(patchedProducts)

	products = get_meProducts(configInfo, buyerToken, search) # admin sear h

	log.debug(products['Meta'])



	# add xp to users




	# nested xp!

	# search and record times




def printAndCompare(term, data):
	#data = ['Items']
	for item in data:
		print(any([]))





@pytest.mark.parametrize("search", [
    (fake.job()),
    (fake.word(ext_word_list=None)),
    (fake.paragraph(nb_sentences=3, variable_nb_sentences=True, ext_word_list=None)),
    (fake.words(nb=3, ext_word_list=None)),
    (fake.boolean(chance_of_getting_true=50)),
    (fake.safe_color_name()),
    (str(fake.boolean(chance_of_getting_true=50)).lower()),
    (int(fake.msisdn()))
])
@pytest.mark.parametrize("searchOn", [
	(None),
	('ID'),
	('Name'),
	('Description')
])
@pytest.mark.parametrize("sortBy", [
	(None),
	('ID'),
	('Name')
])
#TODO: make the reporting on this pretty
def test_SearchAndCompare(configInfo, apiEnv, search, searchOn, sortBy):

	# auth as dbrown

	client_id = configInfo['BUYER-CLIENTID']
	username = 'dbrown'
	password = 'fails345!!'
	scope = ['Shopper']

	buyerToken = get_Token_UsernamePassword(configInfo, client_id, username, password, scope)

	# list me/products

	search = {
		'search': search,
		'searchOn': searchOn,
		'sortBy': sortBy,
		'PageSize': '100'

	}


	products = get_meProducts(configInfo, buyerToken, search) 

	log.debug(json.dumps(products['Meta'], indent=4))
	#log.debug(products['Items'])

'''
	# write product id, name, description to file

	with open('logs/'+__name__+'_'+str(apiEnv)+'.txt', 'a') as f:
		f.write('Me/Product Search Results for '+str(apiEnv)+'\n')
		f.write('Search Data: \n'+json.dumps(search, indent=4)+'\n')
		json.dump(products['Meta'], f,  indent=4)
		f.write('\n')
		for item in products['Items']:
			f.write('\n'+'ID: '+item['ID']+'\n')
			f.write('Name: '+item['Name']+'\n')
			f.write('Description: '+item['Description']+'\n')
			f.write('\n')
'''

def createProductFacet(configInfo, productList, productFacet, token=''):

	headers = {
		'Authorization': 'Bearer '+ token,
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}


	for ID in productList:
		try:
			xp = requests.post(configInfo['API']+'v1/ProductFacets/', headers = headers, params=params, json=productFacet)
			log.debug(xp.request.url)
			log.debug(xp.status_code)
			log.debug(json.dumps(xp.json(), indent=2))

			assert xp.status_code is codes.ok
			return xp.json()
		except requests.exceptions.RequestException as e: 
			log.debug(json.dumps(xp.json(), indent=2))
			print(e)
			sys.exit(1)


def getProductFacets(configInfo, token, params):

	headers = {
		'Authorization': 'Bearer '+ token,
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	try:
		pFacet = requests.get(configInfo['API']+'v1/ProductFacets/', headers = headers, params=params)
		log.debug(pFacet.request.url)
		log.debug(pFacet.status_code)
		log.debug(json.dumps(pFacet.json(), indent=2))

		assert pFacet.status_code is codes.ok
		return pFacet.json()
	except requests.exceptions.RequestException as e: 
		log.debug(json.dumps(pFacet.json(), indent=2))
		print(e)
		sys.exit(1)


def adminProductFacet(configInfo, token, facet):

	headers = {
		'Authorization': 'Bearer '+ token,
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	try:
		pFacet = requests.post(configInfo['API']+'v1/ProductFacets/', headers = headers, json=facet)
		log.debug(pFacet.request.url)
		log.debug(pFacet.status_code)
		log.debug(json.dumps(pFacet.json(), indent=2))

		assert pFacet.status_code is codes.created
		return pFacet.json()
	except requests.exceptions.RequestException as e: 
		log.debug(json.dumps(pFacet.json(), indent=2))
		print(e)
		sys.exit(1)



@pytest.mark.parametrize("facetName,facetID,facetPath", [
    ('colors.spring', 'colors-spring', 'colors.spring'),
    ('job', 'job', 'job')
])
@pytest.mark.parametrize("facetValue", [
    (fake.boolean(chance_of_getting_true=50)),
    (fake.safe_color_name()),
    (str(fake.boolean(chance_of_getting_true=50)).lower()),
    (int(fake.msisdn()))
])
def test_FacetSearch(configInfo, facetName, facetID, facetPath, facetValue):


	client_id = configInfo['BUYER-CLIENTID']
	username = 'dbrown'
	password = 'fails345!!'
	scope = ['Shopper']

	buyerToken = get_Token_UsernamePassword(configInfo, client_id, username, password, scope)


	#get auth tokens

	client_id = configInfo['ADMIN-CLIENTID']
	username = configInfo['ADMIN-USERNAME']
	password = configInfo['ADMIN-PASSWORD']
	scope = ['FullAccess']

	adminToken = get_Token_UsernamePassword(configInfo, client_id, username, password, scope)['access_token']



	# admin checks if facet exists

	params = {
		'ID': facetID
	}

	productFacet = getProductFacets(configInfo, adminToken, params)
	log.debug(json.dumps(productFacet['Items'], indent=4))



	if productFacet['Meta']['TotalCount'] == 0:
		log.debug('create new facet '+facetName+'!')
		newFacet = {
			"ID": facetID,
			"Name": facetName,
			"XpPath": facetPath,
			"ListOrder": 1,
			"MinCount": 1, # defaults to 1, 0 includes 0 results
			"xp": {}
			}

		facet = adminProductFacet(configInfo, adminToken, newFacet)
	else:
		log.debug(facetName + ' Facets Exist!')


	# me/products list for buyer user & save list of product ids

	log.debug('buyer product list!')
	
	buyerProducts = get_meProducts(configInfo, buyerToken, {'PageSize':20})

	assert buyerProducts['Meta']['Facets']

	buyerProductIDs = []
	
	for item in buyerProducts['Items']:
		buyerProductIDs.append(item['ID'])

	log.debug(buyerProductIDs)


	# admin looks for any products with the facet XP

	filters = []

	filters.append({'xp.'+facetPath : facetValue})

	log.debug('XP filters are: '+str(filters))

	numXP = len(filters) #number of filters we're looking for

	for fil in filters:
		adminProductList = get_Products(configInfo, adminToken, fil )
		log.debug('Admin List of Products with Facet XP: '+str(adminProductList['Meta']['TotalCount']))
	


	facets = []
	for facet in buyerProducts['Meta']['Facets']:
		log.debug(facet)
		facets.append(facet['Name'])

	for item in filters:
		for key in item.keys():
			assert key[3:] in facets

	log.debug(buyerProducts['Meta'])


	if adminProductList['Meta']['TotalCount'] == 0:
		log.debug('No Products With XP for Product Facets!')

		#log.debug(facet.keys())
		log.debug('creating '+str(len(buyerProductIDs))+' Products with XP '+facet['ID']+'!')
		newXP = {
			'xp': {
				facetPath : facetValue
			}
		}
		
		for item in buyerProductIDs:
			patch_Product(configInfo, adminToken, item, '', newXP)


		
	# check buyer me/product list for expected facet 
	
	time.sleep(60)
	log.info('okay, the index should be rebuilt now!')
	time.sleep(30)

	newBuyerProducts = get_meProducts(configInfo, buyerToken, {'PageSize':20})

	log.debug(newBuyerProducts['Meta']['Facets'])
	assert newBuyerProducts['Meta']['Facets']

	foundFacets = []
	for item in newBuyerProducts['Meta']['Facets']:
		foundFacets.append(item['ID'])


	assert facetID in foundFacets

	# check that facetValue is collected in facet meta

	index = foundFacets.index(item['ID'])
	log.debug('index: '+str(index))

	log.debug(newBuyerProducts['Meta']['Facets'][index]['Values'])

	foundValues = []
	for item in newBuyerProducts['Meta']['Facets'][index]['Values']:
		log.debug(item.keys())
		foundValues.append(item['ID'])

	log.info('facet value: '+str(facetValue))
	if type(facetValue) == bool:
		facetValue = str(facetValue).lower()
		log.info('facet value: '+str(facetValue))
	log.info('found values: '+str(foundValues))
	assert facetValue in foundValues


	

'''
	for item in newBuyerProducts['Items']:
		if item['ID'] in buyerProductIDs:
			log.debug("Updated Product Present!")
			for facet in newBuyerProducts['Meta']['Facets']:
				if facet['ID'] == facetID:
					for value in facet['Values']:
						if value['ID'] == facetValue:
							log.debug('SUCCESSFULLY FOUND VALUE '+value['Count'])

		else:
			log.debug(item['ID']+' Not Found!')

'''

print('end!')






