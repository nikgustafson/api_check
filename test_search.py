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

from api_check.auth import get_Token_UsernamePassword
from api_check.products import get_Products, patch_Product
from api_check.me import get_meProducts


fake = Faker()

log = logging.getLogger(__name__)


def createProductFacet(configInfo, products, token):

	newXP = {
		"xp": {
			"blue": True
		}
	}

	log.debug(newXP)
	newProducts = []
	for item in products:
		log.debug(item['ID'])
		product = patch_Product(
			configInfo, token, item['ID'], params='', body=newXP)
		log.debug(product)
		newProducts.append(product)

	return newProducts


log.debug('Search Tests Begun...')


@pytest.mark.skip("Test needs improvement")
@pytest.mark.search
@pytest.mark.description("Test verifies that search works over xp and nested xp, and notates the performance")
def test_productSearch(configInfo):

	log.info('API ENV = '+pytest.config.oc_env.lower())

	log.info('GLOBAL ENV TYPE = '+repr(type(pytest.global_env)))

	# auth as an admin user

	client_id = configInfo['ADMIN-CLIENTID']
	username = configInfo['ADMIN-USERNAME']
	password = configInfo['ADMIN-PASSWORD']
	scope = ['FullAccess']

	# can successfully get a token
	adminToken = get_Token_UsernamePassword(
		configInfo, client_id, username, password, scope)

	client_id = configInfo['BUYER-CLIENTID']
	username = configInfo['BUYER-USERNAME']
	password = configInfo['BUYER-PASSWORD']
	scope = ['Shopper']

	buyerToken = get_Token_UsernamePassword(
		configInfo, client_id, username, password, scope)

	# add xp to products

	search = {
		'search': 'blue',
		'searchOn': 'xp.*'

	}

	products = get_meProducts(configInfo, buyerToken, search)  # admin sear h

	log.debug(products['Meta'])

	if products['Meta']['TotalCount'] == 0:
		log.debug("Time to make more XP!")

		params = {
			'pageSize': '5',
			'page': '3'
		}
		products = get_meProducts(configInfo, buyerToken, params)
		patchedProducts = createProductFacet(
			configInfo, products['Items'], adminToken)
		log.debug(patchedProducts)

	products = get_meProducts(configInfo, buyerToken, search)  # admin sear h

	log.debug(products['Meta'])

	# add xp to users

	# nested xp!

	# search and record times


def printAndCompare(term, data):
	# data = ['Items']
	for item in data:
		print(any([]))


@pytest.mark.skip("Test no longer viable")
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
# TODO: make the reporting on this pretty
def test_SearchAndCompare(configInfo, search, searchOn, sortBy):

	# auth as dbrown

	client_id = configInfo['BUYER-CLIENTID']
	username = 'dbrown'
	password = 'fails345!!'
	scope = ['Shopper']

	buyerToken = get_Token_UsernamePassword(
		configInfo, client_id, username, password, scope)

	# list me/products

	search = {
		'search': search,
		'searchOn': searchOn,
		'sortBy': sortBy,
		'PageSize': '100'

	}

	products = get_meProducts(configInfo, buyerToken, search)

	log.debug(json.dumps(products['Meta'], indent=4))
	# log.debug(products['Items'])


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
		'Authorization': 'Bearer ' + token,
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	for ID in productList:
		try:
			xp = requests.post(configInfo['API']+'v1/ProductFacets/',
							   headers=headers, params=params, json=productFacet)
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
		'Authorization': 'Bearer ' + token,
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	try:
		pFacet = requests.get(
			configInfo['API']+'v1/ProductFacets/', headers=headers, params=params)
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
		'Authorization': 'Bearer ' + token,
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}

	try:
		pFacet = requests.post(
			configInfo['API']+'v1/ProductFacets/', headers=headers, json=facet)
		log.debug(pFacet.request.url)
		log.debug(pFacet.status_code)
		log.debug(json.dumps(pFacet.json(), indent=2))

		assert pFacet.status_code is codes.created
		return pFacet.json()
	except requests.exceptions.RequestException as e:
		log.debug(json.dumps(pFacet.json(), indent=2))
		print(e)
		sys.exit(1)


def test_facetMinCount():

	'''
	facet min count controls 
	a) how many results a value needs to show up
	b) if a facet appears in the facet list (if no values, does not show up)
	'''





#@pytest.mark.skipif(pytest.config.oc_env.lower() == 'prod',
#					reason="feature not in Prod yet")
@pytest.mark.search
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

	buyerToken = get_Token_UsernamePassword(
		configInfo, client_id, username, password, scope)

	# get auth tokens

	client_id = configInfo['ADMIN-CLIENTID']
	username = configInfo['ADMIN-USERNAME']
	password = configInfo['ADMIN-PASSWORD']
	scope = ['FullAccess']

	adminToken = get_Token_UsernamePassword(
		configInfo, client_id, username, password, scope)['access_token']

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
			"MinCount": 1,  # defaults to 1, 0 includes 0 results
			"xp": {}
		}

		facet = adminProductFacet(configInfo, adminToken, newFacet)
	else:
		log.debug(facetName + ' Facets Exist!')

	# me/products list for buyer user & save list of product ids

	log.debug('buyer product list!')

	buyerProducts = get_meProducts(configInfo, buyerToken, {'PageSize': 20})
	log.info(buyerProducts['Meta']['Facets'])

	assert buyerProducts['Meta']['Facets']

	buyerProductIDs = []

	for item in buyerProducts['Items']:
		buyerProductIDs.append(item['ID'])

	log.debug(buyerProductIDs)

	# admin looks for any products with the facet XP

	filters = []

	filters.append({'xp.'+facetPath: facetValue})

	log.debug('XP filters are: '+str(filters))

	numXP = len(filters)  # number of filters we're looking for

	for fil in filters:
		adminProductList = get_Products(configInfo, adminToken, fil)
		log.debug('Admin List of Products with Facet XP: ' +
				  str(adminProductList['Meta']['TotalCount']))

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

		# log.debug(facet.keys())
		#log.debug('creating '+str(len(buyerProductIDs)) + ' Products with XP '+facet['ID']+'!')

		if facetPath == facetID:
			newXP = {
				'xp': {
					facetPath: facetValue
				}
			}
		elif facetPath != facetID:
			log.info('Nested XP!')
			facetList = facetPath.split('.')
			log.info(len(facetList))
			log.info(list(facetList))
			#(len(facetList))

			if len(facetList) == 2:
				newXP = {
				'xp': {
					facetList[0] : {
						facetList[1] : facetValue
					}
				}
			}


		
		log.info(newXP)


		for item in buyerProductIDs:
			patch_Product(configInfo, adminToken, item, '', newXP)

	# check buyer me/product list for expected facet

	time.sleep(30)
	log.info('okay, the index should be rebuilt now!')
	time.sleep(30)

	newBuyerProducts = get_meProducts(configInfo, buyerToken, {'PageSize': 20})

	log.debug(newBuyerProducts['Meta']['Facets'])
	assert newBuyerProducts['Meta']['Facets']

	foundFacets = []
	for item in newBuyerProducts['Meta']['Facets']:
		foundFacets.append(item['XpPath'])

	log.info('Looking for '+facetPath+'...   \nFound Facets '+ str(', '.join(foundFacets)))
	try:
		assert facetPath in foundFacets
		log.info('Found it!')
	except:
		log.info('Could not find!')

	# check that facetValue is collected in facet meta

	index = foundFacets.index(item['XpPath'])
	log.debug('index: '+str(index))

	log.debug(newBuyerProducts['Meta']['Facets'])
	#log.debug(newBuyerProducts['Meta']['Facets'])

	for item in newBuyerProducts['Meta']['Facets']:
		log.debug(newBuyerProducts['Meta']['Facets'][item]['Values'])
		for value in newBuyerProducts['Meta']['Facets'][item]['Values']:
			log.debug(newBuyerProducts['Meta']['Facets'][item]['Values'][value]['Value'])




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


@pytest.mark.skip
def test_EX1663(configInfo):

# 1. create a product facet such as "colors.spring"
# 2. add the xp "colors.spring": true to various products that are assigned to a user
# 3. impersonate said user, and list me/products
# 4. see the new Facets subobject on Meta, but there are no values populated


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


	log.info(json.dumps(buyer.get(configInfo['API']+'v1/me').json(), indent=4))
	log.info(json.dumps(admin.get(configInfo['API']+'v1/me').json(), indent=4))


	facetList = admin.get(configInfo['API']+'v1/ProductFacets')

	assert facetList.status_code is codes.ok
	log.info('Total Initial Facets: '+ str(facetList.json()['Meta']['TotalCount']))

	newFacets = {
		'facet01' : {
			  "ID": 'ex-1663-'+fake.uuid4(),
			  "Name": "Sizes",
			  "XpPath": "sizes",
			  "ListOrder": 3,
			  "MinCount": 0
			},

		'facet02' : {
			  "ID": 'ex-1663-'+fake.uuid4(),
			  "Name": "ExtendedSizes",
			  "XpPath": "sizes.extended",
			  "ListOrder": 1,
			  "MinCount": 0
			},

		'facet03' : {
			  "ID": 'ex-1663-'+fake.uuid4(),
			  "Name": "PetiteSizes",
			  "XpPath": "sizes.petite",
			  "ListOrder": 2,
			  "MinCount": 0
			}
		}

	if facetList.json()['Meta']['TotalCount'] == 0:
		for item in newFacets:
			try:
				log.info(item)
				facet = admin.post(configInfo['API']+'v1/ProductFacets', json = newFacets[item])
				assert facet.status_code is codes.created
				log.info('Created '+ str(facet.json()['ID']))
			except requests.exceptions.RequestException as e:  # This is the correct syntax
				log.info(e)
				sys.exit(1)

		facetList = admin.get(configInfo['API']+'v1/ProductFacets')

		assert facetList.status_code is codes.ok
		log.info('Total Facets After Creation: '+ str(facetList.json()['Meta']['TotalCount']))



	# update ten random products to have these facets

	pageSize = '10'
	productList = admin.get(configInfo['API']+'v1/Products', params={'pageSize': pageSize}).json()

	productTotal = productList['Meta']['TotalCount']
	pageTotal = productList['Meta']['TotalPages']

	randomPage = random.choice(range(1, pageTotal-1))


	selectedProducts = admin.get(configInfo['API']+'v1/Products', params={'page': randomPage, 'pageSize':pageSize})
	log.info(selectedProducts.url)
	log.info(json.dumps(selectedProducts.json()['Meta'], indent=4))
	selectedProducts = selectedProducts.json()['Items']
	#log.info(json.dumps(selectedProducts, indent=4))

	productIDs = []


	for item in selectedProducts:
		#log.info(item)
		productIDs.append(item['ID'])

	
	log.info(productIDs, len(productIDs))
	patchBody = {'xp':{}}
	sizeList = ['xs/0-4', 's/5-8', 'm/9-12', 'l/13-16', 'xl/17-22', 'xxl/23-28']
	log.info(random.choice(sizeList))

	for facet in newFacets:
		log.info(newFacets[facet]['XpPath'])
		if newFacets[facet]['XpPath'] == 'sizes':
			print(newFacets[facet]['XpPath'])
			patchBody['xp'][newFacets[facet]['XpPath']] = random.choice(sizeList)
			
		else:
			patchBody['xp'][newFacets[facet]['XpPath']] = bool(random.getrandbits(1))	

	log.info(json.dumps(patchBody, indent=4))		

	assert len(productIDs) > 0

	for productID in productIDs:
		try:
			patched = admin.patch(configInfo['API']+'v1/products/'+productID, json = patchBody)
			log.info(patched.status_code)
			log.info(patched.request.headers)
			log.info(patched.request.url)
			log.info(patched.request.body)
			log.info(patched.text)
			assert patched.status_code is codes.ok
			log.info(patched.json())

		except requests.exceptions.RequestException as e:  # This is the correct syntax
			log.info(e)
			sys.exit(1)


@pytest.mark.parametrize("buyer_endpoint", [
	('costcenters'),
	('usergroups'),
	('Addresses'),
	('creditcards'),
	('categories'),
	('orders'),
	('promotions'),
	('spendingaccounts'),
	('shipments'),
	('catalogs')
])
def test_NoFacetsReturnedForNonFacetLists(configInfo, buyer_endpoint):

	'''
		facets should only be returned in the meta for faceted lists, not all lists
		current facet lists:
		- me/products
	'''

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


	log.info(json.dumps(buyer.get(configInfo['API']+'v1/me').json(), indent=4))
	log.info(json.dumps(admin.get(configInfo['API']+'v1/me').json(), indent=4))


	facetList = admin.get(configInfo['API']+'v1/ProductFacets')

	assert facetList.status_code is codes.ok

	should_not_have_facet_meta = buyer.get(configInfo['API']+'v1/Me/'+buyer_endpoint)
	log.info(should_not_have_facet_meta.json()['Meta']) 
	
	assert should_not_have_facet_meta.status_code is codes.ok
	assert 'Facets' not in should_not_have_facet_meta.json()['Meta'] 


@pytest.mark.parametrize("buyer_endpoint", [
	('products')
])
def test_FacetsReturnedForFacetLists(configInfo, buyer_endpoint):

	'''
		facets should only be returned in the meta for faceted lists, not all lists
		current facet lists:
		- me/products
	'''

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


	log.info(json.dumps(buyer.get(configInfo['API']+'v1/me').json(), indent=4))
	log.info(json.dumps(admin.get(configInfo['API']+'v1/me').json(), indent=4))

	should_have_facet_meta = buyer.get(configInfo['API']+'v1/Me/'+buyer_endpoint)
	log.info(should_have_facet_meta.json()['Meta']) 

	assert should_have_facet_meta.status_code is codes.ok
	assert 'Facets' in should_have_facet_meta.json()['Meta'] 


@pytest.mark.search
def test_NoAccessForNonFacetOrgs(configInfo, buyer_endpoint):

	'''
		if a user attempts to access facets (such as facets endpoint, or find facets in list meta) from an org without Premium Search turned on, there should be a friendly error. Not an empty list.

		#TODO: expand to use a non facet org 
	'''

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


	log.info(json.dumps(buyer.get(configInfo['API']+'v1/me').json(), indent=4))
	log.info(json.dumps(admin.get(configInfo['API']+'v1/me').json(), indent=4))


	facetList = admin.get(configInfo['API']+'v1/ProductFacets')

	assert facetList.status_code is codes.ok


@pytest.mark.search
@pytest.mark.skip("needs adjusted to handle misspellings better")
@pytest.mark.parametrize("search_query", [
	('data'),
	('datas'),
	('particular'),
	('partikular'),
	('sentences'),
	('sentances')
])
def test_FuzzySearch(configInfo, search_query):

	#/me/products?search=data&searchOn=Description

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

	params = {
		'searchOn': 'Description',
		'search': search_query,
		'pageSize': 100
	}

	searchQuery = params['search']
	log.info(searchQuery)

	fuzzy = buyer.get(configInfo['API']+'v1/me/products', params= params)
	assert fuzzy.status_code is codes.ok
	#log.info(json.dumps(fuzzy.json(), indent=4))


	log.info('Fuzzy Search: '+params['search'])
	log.info(str(fuzzy.json()['Meta']['TotalCount'])+ ' Results:')



	results= fuzzy.json()['Items']
	#log.info(json.dumps(fuzzy.json()['Items'], indent=4))

	count = 0
	for item in results:
		if searchQuery.lower() in item['Description'].lower():
			log.info('MATCH')
			count += 1
			#log.info(item['Description'])
		else:
			log.info('No Match :(')
			log.info(item['Description'].lower())
	
	#assert count == fuzzy.json()['Meta']['TotalCount']



def test_FuzzySearch2(configInfo, search_query):

	#/me/products?search=data&searchOn=Description

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

	params = {
		'searchOn': 'Description',
		'search': search_query,
		'pageSize': 100
	}

	searchQuery = params['search']
	log.info(searchQuery)

	fuzzy = buyer.get(configInfo['API']+'v1/me/products', params= params)
	assert fuzzy.status_code is codes.ok
	#log.info(json.dumps(fuzzy.json(), indent=4))


	log.info('Fuzzy Search: '+params['search'])
	log.info(str(fuzzy.json()['Meta']['TotalCount'])+ ' Results:')



	results= fuzzy.json()['Items']
	#log.info(json.dumps(fuzzy.json()['Items'], indent=4))

	count = 0
	for item in results:
		if searchQuery.lower() in item['Description'].lower():
			log.info('MATCH')
			count += 1
			#log.info(item['Description'])
		else:
			log.info('No Match :(')
			log.info(item['Description'].lower())
	
	assert count == fuzzy.json()['Meta']['TotalCount']






def test_XPAlias(configInfo):

	#/me/products?search=data&searchOn=Description

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


	noalias = buyer.get(configInfo['API']+'v1/me/products', params= {'searchOn': 'xp=*', 'search': '', 'pageSize': 100})
	assert noalias.status_code is codes.ok

	alias = buyer.get(configInfo['API']+'v1/me/products', params= {'searchOn': 'xp', 'search': '', 'pageSize': 100})
	assert alias.status_code is codes.ok
	#log.info(json.dumps(fuzzy.json(), indent=4))

	assert alias.json()['Meta']['TotalCount'] == noalias.json()['Meta']['TotalCount']
	
	
	totalCount = alias.json()['Meta']['PageSize']
	log.info(totalCount)

	for i in range(0, totalCount):
		log.info(i)
		#log.info(noalias.json()['Items'][i])
		#log.info(alias.json()['Items'][i])
		assert noalias.json()['Items'][i] == alias.json()['Items'][i]
