# configure test app
import requests
from datetime import *
import logging
import configparser
import pytest
import json
from pathlib import *
from faker import Faker
import random
import urllib
# logging setup

#logging.basicConfig(filename='logs/catalogSetUp-'+ str(datetime.timestamp(datetime.utcnow())) +'.log', level=logging.DEBUG, filemode = 'w')
logging.basicConfig(filename='logs/catalogSetUp.log', level=logging.DEBUG, filemode = 'w')
log = logging.getLogger('catalogSetUp')

# read info from config file 

config = configparser.ConfigParser()
config.read('config.ini')
auth = config['LOCUST-AUTH']

apiURLs = config['API-HOST']

authHost = apiURLs['authHost']
host = apiURLs['host']


def getTokenSeller(scope = ''):
	payload = {
	'client_id':auth['sellerClientID'],
	'grant_type': 'password',
	'username' : auth['sellerAdminUsername'],
	'password':auth['sellerAdminPassword'],
	'Scope': scope
	}
	headers = {'Content-Type':'application/json'}
	r = requests.post(authHost + '/oauth/token', data = payload, headers = headers)

	return(r.json()['access_token'])


def generateAddresses(total, headers):
	fake = Faker()
	addresses = []

	success = dict()

	for item in list(range(total)):
		address = {
		  "ID": fake.isbn10(separator="-"),
		  "CompanyName": fake.company(),
		  "FirstName": fake.first_name(),
		  "LastName": fake.last_name(),
		  "Street1": fake.street_address(),
		  "Street2": fake.secondary_address(),
		  "City": fake.city(),
		  "State": fake.state_abbr(),
		  "Zip": fake.postalcode(),
		  "Country": fake.country_code(),
		  "Phone": fake.phone_number(),
		  "AddressName": fake.street_address(),
		  "xp": {}
		}
		addresses.append(address)

	for item in addresses:
		a = requests.post(host + '/addresses', headers = headers, data = json.dumps(item, sort_keys=True, indent=4))
		log.debug(a.request.url)
		log.debug(a.status_code)
		log.debug(a.request.headers)
		log.debug(a.request.body)
		success[a.url]=[(a.status_code, a.text)]
		assert a.status_code == 201

	return(success)


def generatePriceSchedules(total, headers):

	fake = Faker()
	priceSchedules = []

	success = dict()

	for item in list(range(total)):
		minQuant = random.randrange(0,100,1)
		MaxQuant = random.randrange(minQuant,1000,1)

		priceSchedule = {
		  "ID": fake.isbn13(separator="-"),
		  "Name": "withShipping-"+fake.isbn13(separator="-"),
		  "ApplyTax": False,
		  "ApplyShipping": True,
		  "MinQuantity": minQuant,
		  "MaxQuantity": MaxQuant,
		  "UseCumulativeQuantity": False,
		  "RestrictedQuantity": False,
		  "PriceBreaks": [
		    {
		      "Quantity": 0 ,
		      "Price": random.randrange(0,1000,1)
		    }
		  ],
		  "xp": {}
		}

		priceSchedules.append(priceSchedule)

	for item in priceSchedules:
		a = requests.post(host + '/priceschedules', headers = headers, data = json.dumps(item, sort_keys=True, indent=4))
		success[a.url]=[(a.status_code, a.text)]
		assert a.status_code == 201

	return(success)

def generateProducts(total, inventory, priceschedules, addresses, headers):
	fake = Faker()
	
	success = dict()

	blns = Path('blns.json').open()
	blns = json.load(blns)

	inv = False
	quantAvail = 0

	if inventory == True:
		inv = True
		quantAvail = random.randrange(0, 100000, 1)

	products = []

	priceList = []
	addressList = []


	for item in priceschedules:
		#print(item.items())
		priceList.append(item['ID'])


	for item in addresses:
		#print(json.dumps(item, sort_keys=True))
		addressList.append(item['ID'])

	totalPriceSchedules = len(priceList)
	totalAddresses = len(addressList)


	for item in list(range(total)):

		randomPriceSchedule = priceschedules[random.randrange(0, totalPriceSchedules)]['ID']
		randomAddress =  addresses[random.randrange(0, totalAddresses)]['ID']

		fancyName = ''.join(ch for ch in str(random.choice(blns)) if ch.isalnum())
		

		product = {
		  "DefaultPriceScheduleID": randomPriceSchedule,
		  "ID": fake.isbn13(separator="-"),
		  "Name": ('hello '+fancyName)[0:99],
		  "Description": fake.text(max_nb_chars=200, ext_word_list=None),
		  "QuantityMultiplier": 1,
		  "ShipWeight": random.randrange(0, 100, 1),
		  "ShipHeight": random.randrange(0, 100, 1),
		  "ShipWidth": random.randrange(0, 100, 1),
		  "ShipLength": random.randrange(0, 100, 1),
		  "Active": True,
		  "xp": {},
		  "ShipFromAddressID": randomAddress,
		  "Inventory": {
		    "Enabled": inv,
		    "NotificationPoint": 0,
		    "VariantLevelTracking": False,
		    "OrderCanExceed": False,
		    "QuantityAvailable": quantAvail
		  }
		}

		products.append(product)

	for item in products:
		a = requests.post(host + '/products', headers = headers, data = json.dumps(item, sort_keys=True, indent=4))
		success[a.url]=[(a.status_code, a.text)]
		assert a.status_code == 201

	return(success)


def generateCategories(products, headers, catNum, subCatNum):

	fake = Faker()


	categories = requests.get(host + '/catalogs/'+auth['buyerID']+'/categories?pageSize=10', headers = headers)
	log.debug(categories.request.url)
	log.debug(categories.text)
	assert categories.status_code == 200

	categories = categories.json()

	totalcategories = categories['Meta']['TotalCount']
	pageSize = categories['Meta']['PageSize']
	totalPages = categories['Meta']['TotalPages']

	categories = []

	success = dict()

	for item in list(range(catNum)):

		category = {
		  "ID": fake.isbn13(separator="-"),
		  "Name": fake.uri_path(deep=None),
		  "Description": fake.paragraph(nb_sentences=5, variable_nb_sentences=True, ext_word_list=None),
		  "ListOrder": item+1,
		  "Active": True,
		  "xp": {
		    "catImg": fake.image_url(width=None, height=None)
		  }
		}

		categories.append(category)

		a = requests.post(host + '/catalogs/'+auth['buyerID']+'/categories', headers = headers, data = json.dumps(category, sort_keys=True, indent=4))
		success[a.url]=[(a.status_code, a.text)]
		assert a.status_code == 201

	#print(categories)

	subCategories = []

	for item in list(range(subCatNum)):
		# this needs a try catch -- if page total = 1, this randrange won't work
		categories = requests.get(host + '/catalogs/'+auth['buyerID']+'/categories?pageSize=10&page='+str(random.randrange(1, totalPages)), headers = headers)
		log.debug(categories.request.url)
		log.debug(categories.text)
		assert categories.status_code == 200
		log.debug(categories.url)
		log.debug(categories.status_code)
		#print(a.text)
		totalCategories = pageSize-1
		log.debug("TOTAL CATEGORIES: ")
		log.debug(str(totalCategories))
		categories = categories.json()['Items']
		log.debug(json.dumps(categories, sort_keys=True, indent=4))


		parent = random.randrange(1, totalCategories)
		log.debug("PARENT CATEGORY: "+ str(parent))
		log.debug(json.dumps(categories[parent], sort_keys=True, indent=4))
		parentID = categories[parent]['ID']
		log.debug(parentID)
		#print(parent)

		subcategory = {
		  "ID": fake.isbn13(separator="-"),
		  "Name": fake.uri_path(deep=None),
		  "Description": fake.paragraph(nb_sentences=5, variable_nb_sentences=True, ext_word_list=None),
		  "ListOrder": item+1,
		  "Active": True,
		  "ParentID": parentID,
		  "xp": {
		    "catImg": fake.image_url(width=None, height=None)
		  }
		}

		subCategories.append(subcategory)

		a = requests.post(host + '/catalogs/'+auth['buyerID']+'/categories', headers = headers, data = json.dumps(subcategory, sort_keys=True, indent=4))
		success[a.url]=[(a.status_code, a.text)]
		assert a.status_code == 201


		
	for cat in categories:

		assignment = {
		  "CategoryID": cat['ID'],
		  "BuyerID": auth['buyerID'],
		  "Visible": bool(random.getrandbits(1)),
		  "ViewAllProducts": bool(random.getrandbits(1))
		}

		a = requests.post(host + '/catalogs/'+auth['buyerID']+'/categories/assignments', headers = headers, data = json.dumps(assignment, sort_keys=True, indent=4))
		success[a.url]=[(a.status_code, a.text)]
		assert a.status_code == 204

	for cat in subCategories:

		assignment = {
		  "CategoryID": cat['ID'],
		  "BuyerID": auth['buyerID'],
		  "Visible": bool(random.getrandbits(1)),
		  "ViewAllProducts": bool(random.getrandbits(1))
		}

		a = requests.post(host + '/catalogs/'+auth['buyerID']+'/categories/assignments', headers = headers, data = json.dumps(assignment, sort_keys=True, indent=4))
		success[a.url]=[(a.status_code, a.text)]
		assert a.status_code == 204

	return(success)



def assignProductsCatalog(headers):

	##TODO: add an optional products parameter to be able to pass a product subset

	products = requests.get(host + '/products?pageSize=100', headers = headers).json()

	totalProducts = products['Meta']['TotalCount']
	pageSize = products['Meta']['PageSize']
	page = products['Meta']['Page']
	totalPages = products['Meta']['TotalPages']

	success = dict()

	# assign to catalog

	for page in list(range(totalPages)):
		products = requests.get(host + '/products?pageSize=100&page='+str(page+1), headers = headers)
		products = products.json()['Items']

		for product in products:
			assignment ={
			  "CatalogID": auth['buyerID'],
			  "ProductID": product['ID']
			}

			a = requests.post(host + '/catalogs/productassignments', headers = headers, data = json.dumps(assignment, sort_keys=True, indent=4))
			
			success[a.url]=[(a.status_code, a.text)]

	return(success)

def assignProductsCategories(headers):

	categories = requests.get(host + '/catalogs/'+auth['buyerID']+'/categories?depth=all', headers = headers)
	log.debug(categories.url)
	log.debug(categories.status_code)
	#log.debug(categories.text)
	assert categories.status_code == 200

	categories = categories.json()
	#log.debug(json.dumps(categories, sort_keys=True, indent=4))
	pageCatSize = categories['Meta']['PageSize']
	totalCatPages = categories['Meta']['TotalPages']
	totalCategories = categories['Meta']['TotalCount']

	log.debug('TOTAL CATEGORIES'+ str(totalCategories))
	categories = categories['Items']
	log.debug(json.dumps(categories, sort_keys=True, indent=4))


	success = dict()

	products = requests.get(host + '/products?pageSize=100', headers = headers).json()

	totalProducts = products['Meta']['TotalCount']
	pageSize = products['Meta']['PageSize']
	page = products['Meta']['Page']
	totalPages = products['Meta']['TotalPages']

	for page in list(range(totalPages)): # TOTAL PAGES OF PRODUCTS
		products = requests.get(host + '/products?pageSize=100&page='+str(page+1), headers = headers)
		assert products.status_code == 200

		for product in products.json()['Items']:

			randPage = random.randrange(1, totalCatPages)

			categories = requests.get(host + '/catalogs/'+auth['buyerID']+'/categories?depth=all&pageSize='+str(pageCatSize)+'&page='+str(randPage), headers = headers)

			randomCat = random.randrange(0,(pageCatSize-1))

			if randomCat != 1 and randomCat < pageCatSize:
				catID = categories.json()['Items'][randomCat]['ID']
			else:
				catID = categories.json()['Items'][1]['ID']

			log.debug(catID)

			assignment = {
			  "CategoryID": catID,
			  "ProductID": product['ID'],
			  "ListOrder": random.randrange(1,5)
			}


			a = requests.post(host + '/catalogs/'+auth['buyerID']+'/categories/productassignments', headers = headers, data = json.dumps(assignment, sort_keys=True, indent=4))
			
			success[a.url]=[(a.status_code, a.text)]

	return(success)


def assignCategoriesBuyer(visible, viewAllProducts, headers):

	success = dict()

	categories = requests.get(host + '/catalogs/'+auth['buyerID']+'/categories', headers = headers).json()['Items']

	for category in categories:

		assignment = {
		  "CategoryID": category['ID'],
		  "BuyerID": auth['buyerID'],
		  "Visible": visible,
		  "ViewAllProducts": viewAllProducts
		}

		a = requests.post(host + '/catalogs/'+auth['buyerID']+'/categories/assignments', headers = headers, data = json.dumps(assignment, sort_keys=True, indent=4))
		
		success[a.url]=[(a.status_code, a.text)]

	return(success)


def assignProductsUser(userID, headers):

	success = dict()

	priceSchedules = requests.get(host + '/priceschedules?pageSize=100', headers = headers).json()

	totalPriceSchedules = priceSchedules['Meta']['TotalCount']
	pageSize = priceSchedules['Meta']['PageSize']
	totalPSPages = priceSchedules['Meta']['TotalPages']

	priceSchedules = requests.get(host + '/priceschedules?pageSize='+str(pageSize)+'&page=1', headers = headers)
	log.debug(priceSchedules.url)
	log.debug(priceSchedules.status_code)
	#log.debug(priceSchedules.text)
	assert priceSchedules.status_code == 200

	priceSchedules = priceSchedules.json()['Items']

	
	products = requests.get(host + '/products?pageSize=100', headers = headers).json()

	totalProducts = products['Meta']['TotalCount']
	pageSize = products['Meta']['PageSize']
	page = products['Meta']['Page']
	totalPages = products['Meta']['TotalPages']

	success = dict()

	for page in list(range(1,totalPages)):
		products = requests.get(host + '/products?pageSize=100&page='+str(page), headers = headers)
		log.debug(products.url)
		log.debug(products.status_code)
		#log.debug(products.text)
		assert products.status_code == 200

		products = products.json()['Items']

		for product in products:

			randPage = random.randrange(1, pageSize-1)

			if randPage > 1 and randPage < totalPSPages:
				randomPriceSchedule = priceSchedules[randPage]['ID']
			else:
				randomPriceSchedule = priceSchedules[1]['ID']

		
			assignment = {
			  "ProductID": product['ID'],
			  "BuyerID": auth['buyerID'],
			  "PriceScheduleID": randomPriceSchedule
			}


			a = requests.post(host + 'products/assignments', headers = headers, data = json.dumps(assignment, sort_keys=True, indent=4))
			
			success[a.url]=[(a.status_code, a.text)]



	return(success)




def main():
# 1 -- log in as back end user
	token = getTokenSeller('FullAccess')
	headers = {'Content-Type':'application/json', 'Authorization':'Bearer '+ token}
	r = requests.get(host + '/me', headers = headers)
	log.debug(r.url)
	log.debug(r.headers)
	assert r.status_code == 200
	assert r.json()['Username'] == auth['sellerAdminUsername']
	assert r.json()['Active'] == True

# Create Admin Addresses (for shipping address)

	print("Creating Admin Addresses!")

	addresses = generateAddresses(0, headers)
	log.debug(addresses)


	getAddresses = requests.get(host + '/addresses', headers = headers)

	totalAddresses = getAddresses.json()['Meta']['TotalCount']
	print(str(len(addresses))+" Admin Addresses Created!")
	print("New Total Admin Addresses: "+ str(totalAddresses))

# Create Price Schedule

	print("Creating Price Schedules!")
	priceSchedules = generatePriceSchedules(0, headers)
	log.debug(priceSchedules)

	getSchedules = requests.get(host + '/priceschedules', headers = headers)
	totalPriceSchedules = getSchedules.json()['Meta']['TotalCount']

	print(str(len(priceSchedules))+" Price Schedules Created!")
	print("New Total Price Schedules: "+ str(totalPriceSchedules))


# 2 -- create product catalog 

	print("Creating Products!")
	productList = requests.get(host + '/products', headers = headers)
	log.debug(productList.url)
	log.debug(productList.json())


	if productList.status_code != 200:
		fail("Seller User does not have correct Security Profile.")
	assert productList.status_code == 200
	
	#if productList.json()['Meta']['TotalCount'] != 0:
	#	fail("Product Catalog is already populated.")	

	productSchedules = getSchedules.json()['Items']
	productAddresses = getAddresses.json()['Items']

	products = generateProducts(0, True, productSchedules, productAddresses, headers)

	log.debug(json.dumps(products, sort_keys=True, indent=4))

	print(str(len(products))+" New Products Created!")


	getProducts = requests.get(host + '/products', headers = headers)
	totalProducts = getProducts.json()['Meta']['TotalCount']
	print("New Total Products:"+str(totalProducts))

	assert totalProducts > 0



# Create Categories

	print("Creating Categories!")
	#categories = generateCategories(products, headers, 1, 1)
	#log.debug(categories)
	#print(str(len(categories))+ " New Categories Created!")

	#r = requests.get(host + '/catalogs/'+auth['buyerID']+'/categories?depth=all', headers = headers)
	#print("New Total Categories: "+ str(r.json()['Meta']['TotalCount']))



# Assign Products to Catalogs

	print("Assigning Products to "+auth['buyerID']+" Catalog!")
	#assignments = assignProductsCatalog(headers)
	#log.debug(assignments)


# assign products to categories
	print("Assigning Products to Categories!")
	#assignments = assignProductsCategories(headers)
	#log.debug(assignments)


# assign categories to buyer 

	print("Assigning Categories to "+auth['buyerID']+" Buyer!")	
	#assignments = assignCategoriesBuyer(True, True, headers)
	#log.debug(assignments)

# assign products to anon-template user

	print("Assigning Products to "+auth['anonID']+" User!")
	assignments = assignProductsUser(auth['anonID'], headers)
	log.debug(assignments)

# log in as template user and assert users, categories



main()