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
from ..helpers import blns


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


def getOrderLineitems(configInfo, connections, orderID):

    #/orders/{direction}/{orderID}/lineitems

    lineitemList = connections['admin'].get(
        configInfo['API'] + 'v1/orders/incoming/' + orderID + '/lineitems')
    log.info(lineitemList.json())
    assert lineitemList.status_code is codes.ok

    return lineitemList.json()
