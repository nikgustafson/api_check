#! shipments __init__.py


import pytest
import requests
from requests import codes
import logging
import json
import time
from datetime import datetime, date, time
from faker import Faker
from random import randint, choice, randrange


from ..orders import orderCreate

from ..me import registerMe, get_Me


log = logging.getLogger(__name__)


def createAShipment(configInfo, connections, shipmentBody):
        #log = logging.getLogger(createAShipment.__name__)

    if 'ID' in shipmentBody.keys():
        newShipment = connections['admin'].post(
            configInfo['API'] + 'v1/shipments/' + shipmentBody['ID'], json=shipmentBody)

    else:
        newShipment = connections['admin'].post(
            configInfo['API'] + 'v1/shipments/', json=shipmentBody)

    log.info(newShipment.json())
    assert newShipment.status_code is codes.created

    return newShipment.json()


def addItemsToShipment(configInfo, connections, shipmentID, orderID, lineitems=[]):

    admin = connections['admin']

    if len(lineitems) == 0:
        log.info('you don\'t have any line items,  you fool.')
        raise

    for item in lineitems:
        log.info(item)

        itemBody = {
            "OrderID": orderID,
            "LineItemID": item['ID'],
            "QuantityShipped": item['Quantity']
        }

        newItem = admin.post(
            configInfo['API'] + 'v1/shipments/' + shipmentID + '/items', json=itemBody)
        log.info(newItem.request.url)
        log.info(newItem.request.body)
        log.info(newItem.status_code)
        log.info(newItem.json())
        assert newItem.status_code is codes.created

    allItems = admin.get(configInfo['API'] +
                         'v1/shipments/' + shipmentID + '/items')
    assert allItems.status_code is codes.ok

    return allItems.json()


def patchShipment(configInfo, connections, shipmentID, patchBody):

        #"DateShipped": str(datetime.utcnow())

    newShipment = connections['admin'].patch(
        configInfo['API'] + 'v1/shipments/' + shipmentID, json=patchBody)
    log.info(newShipment.url)
    log.info(newShipment.status_code)
    log.info(newShipment.json())
    assert newShipment.status_code is codes.ok
