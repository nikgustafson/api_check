#! tests_me.py


import pytest
import requests
from requests import codes
import logging
import json
import urllib.parse



log = logging.getLogger(__name__)



productParams = {
	'catalogID':'',
	'categoryID':'',
	'supplierID':'',
	'search': '',
	'searchOn': '',
	'page':1,
	'pageSize': 20,

}

def get_Products(configInfo, token, params):



	if type(token) is dict:
		token = token['access_token']

	headers = {
		'Authorization': 'Bearer '+ token,
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}



	try:
		products = requests.get(configInfo['API']+'v1/products', headers = headers, params=(params))
		log.info(products.encoding)
		log.info(products.request.url)
		#log.debug(json.dumps(products.json(), indent=2))

		assert products.status_code is codes.ok
		return products.json()
	except requests.exceptions.RequestException as e: 
		log.debug(json.dumps(products.json(), indent=2))
		print(e)
		sys.exit(1)

	

def patch_Product(configInfo, token, productID, params, body):

	

	if type(token) is dict:
		token = token['access_token']

	headers = {
		'Authorization': 'Bearer '+ token,
		'Content-Type': 'application/json',
		'charset': 'UTF-8'
	}


	try:
		product = requests.patch(configInfo['API']+'v1/products/'+productID, headers = headers, params=params, json=body)
		#log.info(product.request.url)
		#log.info(product.status_code)
		#log.debug(json.dumps(product.json(), indent=2))

		assert product.status_code is codes.ok
		log.info('Patched Product '+str(product.json()['ID']))
		return product.json()
	except requests.exceptions.RequestException as e: 
		log.debug(json.dumps(product.json(), indent=2))
		print(e)
		sys.exit(1)
