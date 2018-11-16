#! tests_me.py


import pytest
import requests
from requests import codes
import logging
import json
import urllib.parse
from random import choice
from faker import Faker
from time import sleep

fake = Faker()

log = logging.getLogger(__name__)


productParams = {
    'catalogID': '',
    'categoryID': '',
    'supplierID': '',
    'search': '',
    'searchOn': '',
    'page': 1,
    'pageSize': 20,

}


def get_Products(configInfo, token, params):

    if type(token) is dict:
        token = token['access_token']

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    try:
        products = requests.get(
            configInfo['API'] + 'v1/products', headers=headers, params=(params))
        log.info(products.encoding)
        log.info(products.request.url)
        # log.debug(json.dumps(products.json(), indent=2))

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
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    try:
        product = requests.patch(configInfo[
                                 'API'] + 'v1/products/' + productID, headers=headers, params=params, json=body)
        # log.info(product.request.url)
        # log.info(product.status_code)
        # log.debug(json.dumps(product.json(), indent=2))

        assert product.status_code is codes.ok
        log.info('Patched Product ' + str(product.json()['ID']))
        return product.json()
    except requests.exceptions.RequestException as e:
        log.debug(json.dumps(product.json(), indent=2))
        print(e)
        sys.exit(1)


def createProducts(configInfo, session, numberOfProducts=1):

    products = []
    i = 0
    while numberOfProducts > i:
        body = {
            "DefaultPriceScheduleID": "",
            "Name": fake.job(),
            "Description": fake.catch_phrase(),
            "QuantityMultiplier": choice(list(range(1, 10))),
            "ShipWeight": choice(list(range(1, 10))),
            "ShipHeight": choice(list(range(1, 10))),
            "ShipWidth": choice(list(range(1, 10))),
            "ShipLength": choice(list(range(1, 10))),
            "Active": True,
            "xp": {"Faker": True}

        }

        #log.info(json.dumps(body, indent=4))

        try:
            newProduct = session.post(
                configInfo['API'] + 'v1/products', json=body)
            # log.info(newProduct.status_code)
            assert newProduct.status_code is codes.created

        except requests.exceptions.RequestException as e:
            log.info(e)

        products.append(newProduct.json()['ID'])

        i = i + 1

    # log.info(products)
    assert len(products) == numberOfProducts

    return products


def assignProducts(configInfo, session, products, PriceScheduleID=None, BuyerID=None, UserGroupID=None):
    log.info('Let\'s Assign Some Products!')

    if type(products[0]) is dict:
        False

    log.info('assign product to catalog')
    for product in products:
        body = {
            "CatalogID": BuyerID,
            "ProductID": product
        }

        try:
            assignCat = session.post(
                configInfo['API'] + 'v1/catalogs/productassignments', json=body)
           # log.info(assignCat.status_code)
           # log.info(assignCat.request.body)
           # log.info(assignCat.text)
            assert assignCat.status_code in [
                codes.created, codes.no_content, codes.ok, '204']

        except requests.exceptions.RequestException as e:
            log.info(e)

    log.info('assign product to ITEM')
    for product in products:
        log.info(product)

        body = {
            "ProductID": product,
            "BuyerID": BuyerID,
            "UserGroupID": UserGroupID,
            "PriceScheduleID": PriceScheduleID
        }

        try:
            assignment = session.post(
                configInfo['API'] + 'v1/products/assignments', json=body)
            # log.info(assignment.status_code)
            # log.info(assignment.request.body)
            # log.info(assignment.text)
            assert assignment.status_code in [
                codes.created, codes.no_content, codes.ok, '204']

        except requests.exceptions.RequestException as e:
            log.info(e)

    return True
