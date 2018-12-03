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

from ..me import getMeProducts, get_Me

fake = Faker()

log = logging.getLogger(__name__)


def get_Products(configInfo, session, params):

    try:
        products = session.get(
            configInfo['API'] + 'v1/products', params=(params))
       # log.info(products.encoding)
       # log.info(products.request.url)
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


def createProducts(configInfo, session, DefaultPriceScheduleID='', numberOfProducts=1):

    products = []
    i = 0
    while numberOfProducts > i:
        body = {
            "DefaultPriceScheduleID": DefaultPriceScheduleID,
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

        log.debug(json.dumps(body, indent=4))

        try:
            newProduct = session.post(
                configInfo['API'] + 'v1/products', json=body)
            log.debug(newProduct.text)
            log.debug(newProduct.status_code)
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
                codes.created, codes.no_content, codes.ok]

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


productParams = {
    'catalogID': '',
    'categoryID': '',
    'supplierID': '',
    'search': '',
    'searchOn': '',
    'page': 1,
    'pageSize': 20,

}


@pytest.fixture(scope='module', autouse=True)
def product_setup(configInfo, connections):
    log.info('---------------------------')
    log.info('| Building up products... |')
    log.info('---------------------------')

    admin = connections['admin']
    buyer = connections['buyer']

    meBuyer = get_Me(configInfo, buyer)
    # log.info(meBuyer)

    buyerID = meBuyer['Buyer']['ID']
    catalogID = meBuyer['Buyer']['DefaultCatalogID']

    meAdmin = get_Me(configInfo, admin)
    # log.info(meAdmin)

    #catalog = meAdmin['']

# products create & to catalog
    filters = {
        'name': 'defaultPriceSchedule'
    }
    priceSchedule = admin.get(
        configInfo['API'] + 'v1/priceschedules/', params=filters)
    # log.info(priceSchedule.json())
    log.debug(priceSchedule.status_code)
    assert priceSchedule.status_code is codes.ok

    defaultPS = priceSchedule.json()['Items'][0]['ID']

    newProducts = createProducts(
        configInfo, admin, DefaultPriceScheduleID=defaultPS, numberOfProducts=100)
   # log.debug(newProducts)

    for item in newProducts:
        assignProductsBody = {
            "CatalogID": catalogID,
            "ProductID": item
        }
        productCatalogAssign = admin.post(
            configInfo['API'] + 'v1/catalogs/productassignments/', json=assignProductsBody)
        # log.debug(productCatalogAssign.text)
        # log.debug(productCatalogAssign.status_code)
        assert productCatalogAssign.status_code is codes.no_content
    log.info('Created and Assigned 100 products to ' + buyerID)

    def product_teardown():
        log.info('--------------------------------------')
        log.info('| tearing down the extra products... |')
        log.info('--------------------------------------')

        for item in newProducts:
            deleteProduct = admin.delete(
                configInfo['API'] + 'v1/products/' + item['ID'])
            # log.debug(deleteProduct.status_code)
            assert deleteProduct.status_code is codes.no_content
