import pytest
import requests
from requests import codes
import logging
import json
from faker import Faker
import random
from random import randint, choice, randrange
import urllib
import time
from ..helpers import blns
from datetime import datetime, timedelta


from ..auth import get_Token_UsernamePassword
from ..products import get_Products, patch_Product
from ..me import get_meProducts


fake = Faker()

log = logging.getLogger(__name__)


def orderCreate(configInfo, session, direction, orderBody):

    if direction == None:
        direction = 'Outbound'

    if type(orderBody) == None:
        orderBody = {"Comments": ""}

    log.info(orderBody)

    if type(orderBody) is dict and 'ID' in orderBody.keys():
        newOrder = session.post(
            configInfo['API'] + 'v1/orders/' + direction + '/' + orderBody['ID'], json=orderBody)

    else:
        newOrder = session.post(
            configInfo['API'] + 'v1/orders/' + direction + '/', json=orderBody)

    log.info(newOrder.json())
    assert newOrder.status_code is codes.created

    return newOrder.json()


def createLineItem(configInfo, session, orderID, productList, numberWanted):

    user = session

    params = {
        'ID': orderID
    }

    order = user.get(configInfo['API'] + 'v1/me/orders/', params=params)
    log.info(order.status_code)
    log.info(order.text)
    #log.info(json.dumps(order.json(), indent=4))

    products = user.get(configInfo['API'] + 'v1/me/products')
    assert products.status_code is codes.ok
    assert products.json()['Meta']['TotalCount'] > 0

    productList = []

    for num in range(numberWanted):
        randomProduct = choice(products.json()['Items'])
        productList.append(randomProduct)

    log.info(productList)

    lineitems = []

    for product in productList:
        log.info(json.dumps(product, indent=4))

        lineitemBody = {
            "ProductID": product['ID'],
            "Quantity": randrange(product['PriceSchedule']['MinQuantity'], product['PriceSchedule']['MaxQuantity']),
            "DateNeeded": (datetime.today() + timedelta(days=5)).strftime("%m/%d/%y"),
            "xp": {
                'Bug': 'Created To Test Bug'
            }
        }

        log.info(lineitemBody)

        lineitem = user.post(
            configInfo['API'] + 'v1/orders/outgoing/' + orderID + '/lineitems', json=lineitemBody)
        log.info(lineitem.status_code)
        log.info(lineitem.request.url)
        log.info(lineitem.request.body)
        log.info(lineitem.text)
        assert lineitem.status_code is codes.created

        lineitems.append(lineitem.json())

    # for item in lineitems:
        #log.info(json.dumps(item, indent=4))

    confirmOrder = user.get(configInfo['API'] + 'v1/me/orders/', params=params)
   # log.debug(confirmOrder.status_code)
   # log.debug(confirmOrder.request.url)
    #log.info(json.dumps(confirmOrder.json(), indent=4))
    # log.info(confirmOrder.json()['LineItemCount'])
    assert confirmOrder.status_code is codes.ok

    assert confirmOrder.json()['Items'][0]['LineItemCount'] == len(lineitems)

    return lineitems
