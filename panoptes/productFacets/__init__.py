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


from ..auth import get_Token_UsernamePassword
from ..products import get_Products, patch_Product
from ..me import get_meProducts


fake = Faker()

log = logging.getLogger(__name__)


def getRandomProducts(configInfo, buyerSession, pageSize=10):

    productList = buyerSession.get(
        configInfo['API'] + 'v1/Me/Products', params={'pageSize': pageSize}).json()

    productTotal = productList['Meta']['TotalCount']
    pageTotal = productList['Meta']['TotalPages']

    randomPage = random.choice(range(1, pageTotal - 1))

    assert randomPage <= pageTotal

    log.info("Page " + str(randomPage) + " of " + str(pageTotal))

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
            'xp': {
                # TODO: make this parameterized and include wider array of
                # values
                newFacets[facet]['XpPath']: fake.word(ext_word_list=None)
            }
        }
        for productID in products:
            log.info(productID)
            try:
                patched = admiSession.patch(
                    configInfo['API'] + 'v1/products/' + productID, json=patchBody)
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


def createProductFacet(configInfo, productList, productFacet, token=''):

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    for ID in productList:
        try:
            xp = requests.post(configInfo['API'] + 'v1/ProductFacets/',
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
            configInfo['API'] + 'v1/ProductFacets/', headers=headers, params=params)
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
            configInfo['API'] + 'v1/ProductFacets/', headers=headers, json=facet)
        log.debug(pFacet.request.url)
        log.debug(pFacet.status_code)
        log.debug(json.dumps(pFacet.json(), indent=2))

        assert pFacet.status_code is codes.created
        return pFacet.json()
    except requests.exceptions.RequestException as e:
        log.debug(json.dumps(pFacet.json(), indent=2))
        print(e)
        sys.exit(1)
