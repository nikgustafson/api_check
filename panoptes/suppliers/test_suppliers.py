#! tests_me.py


import pytest
import requests
import random
from requests import codes
import logging
import json
import jwt
from datetime import datetime
from pytz import timezone, common_timezones_set
import pytz

from faker import Faker

#from ..orders import fakeOrderBody, lineItemCreate


fake = Faker()


log = logging.getLogger(__name__)


@pytest.mark.skip
@pytest.mark.smoke
def test_supplierOrderCreated(configInfo, connections):

    admin = connections['admin']
    buyer = connections['buyer']

    suppliers = admin.get(configInfo['API'] + 'v1/suppliers')
    assert suppliers.status_code is codes.ok
    #log.info(json.dumps(suppliers.json(), indent=4))

    filters = {
        'AutoForwardSupplierID': '*'
    }
    forwardedProducts = admin.get(
        configInfo['API'] + 'v1/products', params=filters)
    #log.info(json.dumps(forwardedProducts.json(), indent=4))
    assert forwardedProducts.status_code is codes.ok
    assert forwardedProducts.json()['Meta']['TotalCount'] > 0

    forwardedProduct = forwardedProducts.json()['Items'][0]

    filters = {
        'ID': forwardedProduct['ID']
    }
    buyerProducts = buyer.get(
        configInfo['API'] + 'v1/me/products', params=filters)
    log.info(json.dumps(buyerProducts.json(), indent=4))

    # buyer creates order

    body = fakeOrderBody()

    buyerOrder = buyer.post(
        configInfo['API'] + 'v1/orders/outgoing', json=body)

    buyerOrderID = buyerOrder.json()['ID']

    products = []
    products.append(buyerProducts.json()['Items'][0])
    buyerLineItem = lineItemCreate(
        configInfo, buyer, buyerOrderID, products)
    log.info(buyerLineItem)
    #log.info(json.dumps(buyerLineItem.json(), indent=4))

    buyerOrder = buyer.post(
        configInfo['API'] + 'v1/orders/outgoing/' + buyerOrderID + '/submit')
    log.info(json.dumps(buyerOrder.json(), indent=4))

    '''
    # removed from api 1.0.85
    supplierFilters = {
        'AutoForwardedFromOrderID': buyerOrderID
    }

    supplierOrders = admin.get(
        configInfo['API'] + '/v1/me/orders', params=supplierFilters)

    assert supplierOrders.json()['Meta']['TotalCount'] > 0
	'''
