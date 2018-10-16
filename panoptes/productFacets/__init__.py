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


def sessionInit(configInfo):

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

    #log.info(json.dumps(buyer.get(configInfo['API']+'v1/me').json(), indent=4))
    #log.info(json.dumps(admin.get(configInfo['API']+'v1/me').json(), indent=4))

    return(buyer, admin)


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
