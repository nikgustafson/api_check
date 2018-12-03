#! tests_me.py


import pytest
import requests
from requests import codes
import logging
import json
import urllib.parse
from faker import Faker
from . import product_setup

from time import sleep

from ..auth import get_Token_UsernamePassword

fake = Faker()

from . import createProducts, assignProducts

from ..me import getMeProducts, get_Me


log = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.Description("Admin List Products endpoint, with performance info.")
def test_ListProducts(configInfo, connections, product_setup):

    admin = connections['admin']

    filters = {
        'pageSize': 100
    }
    productList = admin.get(configInfo['API'] + 'v1/products', params=filters)
    log.debug(productList.status_code)
    log.info(repr(productList.elapsed.total_seconds()) +
             ' total seconds elapsed.')
    assert productList.status_code is codes.ok
    log.debug(json.dumps(productList.json()))


@pytest.mark.skip
@pytest.mark.Description("Bug EX-1761 -- currently caching is holding up product assignment via usergroup.")
def test_productAssignmentCaching(configInfo, connections):

    admin = connections['admin']

    # create a product

    products = createProducts(configInfo, admin, 20)

    # don't create a price schedule

    for product in products:
        meProducts = getMeProducts(configInfo,
                                   connections['buyer'], {'ID': product})
        assert meProducts['Meta']['TotalCount'] == 0

    # assign the product to a user group

    groupBody = {
        "ID": "UserGroup-" + fake.color_name(),
        "Name": fake.color_name(),
        "Description": fake.catch_phrase(),
        "xp": {'Faker': True}
    }

    try:
        userGroup = admin.put(configInfo['API'] + 'v1/buyers/' + configInfo[
                              'BUYER'] + '/usergroups/' + groupBody['ID'], json=groupBody)
        assert userGroup.status_code in [codes.ok, codes.created]
    except requests.exceptions.RequestException as e:
        log.info(e)

    assignment = assignProducts(
        configInfo, admin, products, PriceScheduleID=None, BuyerID=configInfo['BUYER'], UserGroupID=userGroup.json()['ID'])

    log.info(assignment)
    # assign the user to the group

    assignUserBody = {
        "UserGroupID": userGroup.json()['ID'],
        "UserID": configInfo['BUYER-ID']
    }

    assignUser = admin.post(configInfo['API'] + 'v1/buyers/' + configInfo['BUYER'] +
                            '/usergroups/assignments', json=assignUserBody)
    assert assignUser.status_code == 204

    log.info('is it in me/products??')

    foundProducts = []
    for product in products:
        meProducts = getMeProducts(configInfo,
                                   connections['buyer'], {'ID': product})
        if meProducts['Meta']['TotalCount'] != 0:
            foundProducts.append(product)

    log.info('we found these:')
    log.info(foundProducts)

    sleep(120)

    log.info('now is it in me/products??')

    client_id = configInfo['BUYER-CLIENTID']
    username = configInfo['BUYER-USERNAME']
    password = configInfo['BUYER-PASSWORD']
    scope = ['Shopper']

    buyerToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)
    log.debug('buyer session token ' + json.dumps(buyerToken, indent=2))
    buyer = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + buyerToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    buyer.headers.update(headers)

    foundProducts = []
    for product in products:
        meProducts = getMeProducts(configInfo,
                                   buyer, {'ID': product})
        if meProducts['Meta']['TotalCount'] != 0:
            foundProducts.append(product)

    log.info('we found these:')
    log.info(foundProducts)
    if len(foundProducts) == len(product):
        log.info('all products found')
