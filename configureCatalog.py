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


def getTokenSeller(scope = ''):
	payload = {
	'client_id':auth['sellerClientID'],
	'grant_type': 'password',
	'username' : auth['sellerAdminUsername'],
	'password':auth['sellerAdminPassword'],
	'Scope': scope
	}
	headers = {'Content-Type':'application/json'}
	r = requests.post('https://auth.ordercloud.io/oauth/token', data = payload, headers = headers)

	return(r.json()['access_token'])


def generateAddresses(total):
	fake = Faker()
	addresses = []

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

	return(addresses)


def generatePriceSchedules(total):

	fake = Faker()
	priceSchedules = []

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

	return(priceSchedules)

def generateProducts(total, inventory, priceschedules, addresses):
	fake = Faker()
	
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

	return(products)

def main():
# 1 -- log in as back end user
	token = getTokenSeller('FullAccess')
	headers = {'Content-Type':'application/json', 'Authorization':'Bearer '+ token}
	r = requests.get('https://api.ordercloud.io/v1/me', headers = headers)
	log.debug(r.url)
	log.debug(r.headers)
	assert r.status_code == 200
	assert r.json()['Username'] == auth['sellerAdminUsername']
	assert r.json()['Active'] == True

# Create Admin Addresses (for shipping address)

	addresses = generateAddresses(0)

	for item in addresses:
		a = requests.post('https://api.ordercloud.io/v1/addresses', headers = headers, data = json.dumps(item, sort_keys=True, indent=4))
		log.debug(a.request.url)
		log.debug(a.status_code)
		log.debug(a.request.headers)
		log.debug(a.request.body)
		assert a.status_code == 201

	getAddresses = requests.get('https://api.ordercloud.io/v1/addresses', headers = headers)

	totalAddresses = getAddresses.json()['Meta']['TotalCount']
	print("total addresses:"+str(totalAddresses))

# Create Price Schedule

	priceSchedules = generatePriceSchedules(0)

	for item in priceSchedules:
		a = requests.post('https://api.ordercloud.io/v1/priceschedules', headers = headers, data = json.dumps(item, sort_keys=True, indent=4))
		log.debug(a.request.url)
		log.debug(a.status_code)
		log.debug(a.request.headers)
		log.debug(a.request.body)
		assert a.status_code == 201

	getSchedules = requests.get('https://api.ordercloud.io/v1/priceschedules', headers = headers)
	totalPriceSchedules = getSchedules.json()['Meta']['TotalCount']
	print("total priceschedules: "+str(totalPriceSchedules))


# 2 -- create product catalog 

	productList = requests.get('https://api.ordercloud.io/v1/products', headers = headers)
	log.debug(productList.url)
	log.debug(productList.json())
	
	if productList.status_code != 200:
		fail("Seller User does not have correct Security Profile.")
	assert productList.status_code == 200
	
	#if productList.json()['Meta']['TotalCount'] != 0:
	#	fail("Product Catalog is already populated.")	

	productSchedules = getSchedules.json()['Items']
	productAddresses = getAddresses.json()['Items']

	products = generateProducts(100, True, productSchedules, productAddresses)

	#print(products)

	for item in products:
		a = requests.post('https://api.ordercloud.io/v1/products', headers = headers, data = json.dumps(item, sort_keys=True, indent=4))
		log.debug(a.request.url)
		log.debug(a.status_code)
		log.debug(a.request.headers)
		log.debug(a.request.body)
		log.debug(a.text)
		#print(a.text)
		assert a.status_code == 201


	
	# needs: price schedule, address
	#for item in blns:
		#product = dict( id=urllib.parse.urlencode(item), name=item )

	
# 2 -- create product categories

# 2 -- create promos

# 2 -- create a couple admin addresses

# 3 -- assign product catalog to template user

# 4 -- assign promos to template user

# 5 -- assign admin addresses to template user

main()