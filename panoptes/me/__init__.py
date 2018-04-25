import requests
from requests import codes as codes
import pytest
import configparser
import json
import logging
import datetime
import urllib
from random import randint
from faker import Faker
#from . import host, auth

from panoptes import authentication


fake = Faker()

def getMe(token):
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    logger.debug('headers: ')
    logger.debug(headers)
    r = requests.get(host + '/v1/me', headers=headers)
    assert r.status_code is codes.ok

    return r


def getMeProducts(buyerUsername, buyerPassword, search='', productID=''):
    if productID != '':
        productID = '/' + productID

        logger.debug('getMeProducts')
        token = getTokenPasswordGrant(buyerUsername, buyerPassword, 'Shopper')
        logger.debug('token: ' + token)
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
        logger.debug('headers: ')
        logger.debug(headers)
        r = requests.get(host+'/v1/me/products' + productID, headers=headers, params=search)
        return (r)

