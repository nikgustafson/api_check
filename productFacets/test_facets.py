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
from api_check.productFacets import sessionInit


fake = Faker()

log = logging.getLogger(__name__)

def getRandomProducts(configInfo, buyerSession, pageSize=10):

	
	productList = buyerSession.get(configInfo['API']+'v1/Me/Products', params={'pageSize': pageSize}).json()

	productTotal = productList['Meta']['TotalCount']
	pageTotal = productList['Meta']['TotalPages']

	randomPage = random.choice(range(1, pageTotal-1))

	assert randomPage <= pageTotal

	log.info("Page "+str(randomPage)+" of "+str(pageTotal))

	productIDs = []

	for item in productList['Items']:
		productIDs.append(item['ID'])

	log.info(productIDs)

	return productIDs

def patchXP(configInfo, admiSession, products, newFacets):
	log.info(json.dumps(newFacets, indent=4))

	for facet in newFacets:
		log.info(facet)
		# TODO: build out support for nested xp
		patchBody = {
			'xp' : {
				newFacets[facet]['XpPath'] : fake.word(ext_word_list=None) #TODO: make this parameterized and include wider array of values
			}
		}
		for productID in products:
			log.info(productID)
			try:
				patched = admiSession.patch(configInfo['API']+'v1/products/'+productID, json = patchBody)
				log.info(patched.status_code)
				log.info(patched.request.headers)
				log.info(patched.request.url)
				log.info(patched.request.body)
				log.info(patched.text)
				assert patched.status_code is codes.ok
				log.info(json.dumps(patched.json(), indent=4))

			except requests.exceptions.RequestException as e:  # This is the correct syntax
				log.info(e)
				sys.exit(1)





def test_facetCreation(configInfo):

	sessions = sessionInit(configInfo)
	buyer = sessions[0]
	admin = sessions[1]

	#log.info(json.dumps(buyer.get(configInfo['API']+'v1/me').json(), indent=4))
	#log.info(json.dumps(admin.get(configInfo['API']+'v1/me').json(), indent=4))

	# 1. create a facet as an admin user

	facetList = admin.get(configInfo['API']+'v1/ProductFacets')

	name = fake.sentences(nb=1, ext_word_list=None)[0]
	path = name.replace(' ', '-')

	newFacets = {
		'facet01' : {
			  "ID": 'facet-'+fake.uuid4(),
			  "Name": name,
			  "XpPath": path,
			  "ListOrder": 3,
			  "MinCount": 1
			}
		}

	#log.info((newFacets['facet01']['Name']))
	#log.info((newFacets['facet01']['XpPath']))

	facet = admin.post(configInfo['API']+'v1/ProductFacets', json=newFacets['facet01'])
	assert facet.status_code is codes.created
	log.info(json.dumps(facet.json(), indent=4))


	# 2. create some products with that XP


	products = getRandomProducts(configInfo, buyer)
	#log.info(products)

	patchXP(configInfo, admin, products, newFacets)

