import pytest
import requests
from requests import codes
import logging
import json
from faker import Faker
import random
from random import randint, sample, randrange, choice
import urllib
import time
from datetime import datetime, timedelta
from ..helpers import blns


from ..auth import get_Token_UsernamePassword
from ..products import get_Products, patch_Product
from ..me import get_meProducts


fake = Faker()

log = logging.getLogger(__name__)


def fakeOrderBody(fromUserID=[], isShipped=False, orderID=[]):

    fakeBody = {
        'Comments': fake.company()
    }

    if orderID:
        fakeBody['ID'] = orderID[0]

    if fromUserID:
        fakeBody['FromUserID'] = fromUserID[0]

    log.info(json.dumps(fakeBody, indent=4))

    return fakeBody


def lineItemCreate(configInfo, session, orderID, products=[], addressID=[]):
    log = logging.getLogger(lineItemCreate.__name__)
    log.info('Need a new lineitem!')

    #log.info(not products)
    #log.info(not addressID)
    # log.info(session.headers)

    if not products:
        log.info('need to find some products to buy...')

        # get some products
        meProducts = session.get(
            configInfo['API'] + 'v1/me/products', params={'PageSize': 100})
        log.info(meProducts.json()['Meta'])
        products = sample(meProducts.json()['Items'], 3)
        #    0, meProducts.json()['Meta']['PageSize'] - 1))
        # log.info(products)

    if not addressID:
        log.info('where to ship the goods?')
        meAddresses = session.get(configInfo['API'] + 'v1/me/addresses')

        if meAddresses.json()['Meta']['TotalCount'] > 0:
            # set shipping address
            addressID = choice(meAddresses.json()['Items'])['ID']
            log.info(addressID)

    log.info('let\'s start putting those products into lines...')
    bodyList = []
    for product in products:
        randQuant = randrange(product['PriceSchedule']['MinQuantity'], product[
                              'PriceSchedule']['MaxQuantity'])
        bodyList.append([product['ID'], randQuant, addressID])

    #log.info("list of lineitem bodies: " + str(bodyList))

    # log.info(randQuant)

    newLineItems = []
    for item in bodyList:
        lineBody = {
            "ProductID": item[0],
            "Quantity": item[1],
            "ShippingAddressID": item[2],
            "DateNeeded": str(datetime.utcnow() + timedelta(days=10)),
            "xp": {}
        }

        log.info(lineBody)

        newLineItem = session.post(
            configInfo['API'] + 'v1/orders/outgoing/' + orderID + '/lineitems', json=lineBody)
        log.info(newLineItem.request.body)
        log.info(newLineItem.json())
        assert newLineItem.status_code is codes.created
        newLineItems.append(newLineItem.json())

    return newLineItems


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


def getOrderLineitems(configInfo, connections, orderID):

    #/orders/{direction}/{orderID}/lineitems

    lineitemList = connections['admin'].get(
        configInfo['API'] + 'v1/orders/incoming/' + orderID + '/lineitems')
    log.info(lineitemList.json())
    assert lineitemList.status_code is codes.ok

    return lineitemList.json()


def findOrder(configInfo, session, filters):

    orderList = session.get(configInfo['API'] + 'v1/me/orders', params=filters)

    # log.info(orderList.request.headers)
    # log.info(orderList.url)
    #log.info(json.dumps(orderList.json(), indent=4))
    assert orderList.status_code is codes.ok

    return orderList.json()
