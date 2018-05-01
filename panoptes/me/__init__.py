#! panoptes/me __init__
import requests
from requests import codes
import pytest
import configparser
import json
import logging
import datetime
import urllib
from random import randint
from faker import Faker
from panoptes import host, auth




fake = Faker()
logger = logging.getLogger(__name__)

def getMe(token):

    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    logger.debug('headers: ')
    logger.debug(headers)
    r = requests.get(host + '/v1/me', headers=headers)
    assert r.status_code is codes.ok
    assert r.is_redirect is False

    return r.json()


def getMeProducts(token, search='', productID=''):
    if productID != '':
        productID = '/' + productID

    logger.debug('getMeProducts')
        
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    logger.debug('headers: ')
    logger.debug(headers)
    r = requests.get(host+'/v1/me/products' + productID, headers=headers, params=search)
    
    return (r)


def meCardCreate(token):
    logger.debug('ME: Create Credit Card ')

    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    
    logger.debug(headers)
    user = getMe(token)

    logger.debug(json.dumps(user.json(), indent=2))

    card = createCreditCardObj()

    fullCard = {
        "BuyerID": '',
        "TransactionType": "createCreditCard",
        "CardDetails": {
            "CardholderName": user.json()['FirstName'] + ' ' + user.json()['LastName'],
            "CardType": fake.credit_card_provider(card_type=None),
            "CardNumber": cardNumber,
            "ExpirationDate": fake.credit_card_expire(start="now", end="+10y", date_format="%Y/%m/%d"),
            "CardCode": cardNumber[-4:],
            "Shared": False
        }
    }

    partialCard = {
        "CardType": fullCard["CardDetails"]['CardType'],
        "CardholderName": fullCard["CardDetails"]['CardholderName'],
        "ExpirationDate": fullCard["CardDetails"]['ExpirationDate'],
        "PartialAccountNumber": fullCard["CardDetails"]['CardCode'],
        "Token": "",
        "xp": {}
    }

    # logger.debug(partialCard)
    logger.debug(fullCard)

    card = requests.post(host+'/v1/me/creditcards', headers=headers, json=partialCard)
    logger.debug(card.url)
    logger.debug(card.request.body)
    logger.debug(json.dumps(card.json(), indent=2))
    assert card.status_code == codes.created

    return (fullCard)


