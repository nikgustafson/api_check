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
from panoptes import host, auth, createCreditCardObj





fake = Faker()

def getMe(token):

    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    r = requests.get(host + '/v1/me', headers=headers)
    assert r.status_code is codes.ok
    assert r.is_redirect is False

    return r.json()


def getMeProducts(token, search='', productID=''):
    if productID != '':
        productID = '/' + productID
       
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    r = requests.get(host+'/v1/me/products' + productID, headers=headers, params=search)
    
    return (r)


def meCardCreate(token):

    logger = logging.getLogger(__name__)

    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}

    user = getMe(token)

    card = createCreditCardObj()
    logger.info('returned card obj: '+str(card))
    


    partialCard = {
        "CardType": card['CardType'],
        "CardholderName": card['CardholderName'],
        "ExpirationDate": card['ExpirationDate'],
        "PartialAccountNumber": card['CardCode'],
        "Token": "",
        "xp": {}
    }

    
    
    logger.debug(partialCard)
    card = requests.post(host+'/v1/me/creditcards', headers=headers, json=partialCard)
    logger.debug(card.url)
    logger.debug(card.request.body)
    logger.debug(json.dumps(card.json(), indent=2))
    assert card.status_code == codes.created

    return (json.dumps(card.json(), indent=2))


