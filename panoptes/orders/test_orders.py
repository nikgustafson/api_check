import requests
from requests import codes
import random
from random import choice
import logging
import json
import time
import pytest

from . import orderCreate, createLineItem


log = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.description("Verifies that an order submitted twice is unmodified if the Order Status is Open or Awaiting Approval.")
def test_OrderDoubleSumit(configInfo, connections):

    # Set Up

    user = connections['buyer']

    # Create An Order

    orderBody = {
        'Comments': 'Order Double Submit Testing'
    }

    params = {
        'Billing': True,
        'Shipping': True
    }
    addresses = user.get(configInfo['API'] + 'v1/me/addresses', params=params)
    log.debug(addresses.request.url)
    log.debug(addresses.status_code)
    log.debug(addresses.text)
    assert addresses.status_code is codes.ok
    log.debug(json.dumps(addresses.json(), indent=4))

    if addresses.json()['Meta']['TotalCount'] > 0:
        random = choice(addresses.json()['Items'])
        log.debug(json.dumps(random, indent=4))

        orderBody['BillingAddressID'] = random['ID']
        orderBody['ShippingAddressID'] = random['ID']

    #log.info('Order Body:')
    #log.info(json.dumps(orderBody, indent=4))

    order = orderCreate(configInfo, user, 'outgoing', orderBody)
    log.info('New Order')
    #log.info(json.dumps(order, indent=4))

    # Add Some Line Items

    products = user.get(configInfo['API'] + 'v1/me/products')
    assert products.status_code is codes.ok
    assert products.json()['Meta']['TotalCount'] > 0

    productList = choice(products.json()['Items'])

    lineitems = createLineItem(configInfo, user, order['ID'], productList, 2)

    # log.info(lineitems)

    # Double Submit

    submission01 = user.post(
        configInfo['API'] + 'v1/orders/outgoing/' + order['ID'] + '/submit')
    log.info(submission01.status_code)
    log.info(json.dumps(submission01.json(), indent=4))

    time.sleep(30)

    submission02 = user.post(
        configInfo['API'] + 'v1/orders/outgoing/' + order['ID'] + '/submit')
    log.info(submission02.status_code)
    log.info(json.dumps(submission02.json(), indent=4))

    assert submission01.json() == submission02.json()
