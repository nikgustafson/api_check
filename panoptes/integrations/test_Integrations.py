# test platform integrations: auth.net, shipping rates
import requests
import pytest
from requests import codes
import sys
import json
import logging
import logging.handlers
import os
from datetime import *
import urllib
from .. import host
from . import createAuthCard
from ..me import getMe, meCardCreate
from ..authentication import registerUser
import configparser
sys.path.append("C:/api-check/panoptes/pytest")
from faker import Faker
fake = Faker()


handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", "/api-check/logs/"+__name__+'.log'))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "DEBUG"))
root.addHandler(handler)


log = logging.getLogger(__name__)

# create file handler which logs even debug messages
#fh = logging.FileHandler('../logs/'+__name__+'.log')

def test_AuthorizeNet_CreateCard():
    """ 1. creates an anon user
        2. test gets user's credit cards at start of test
        2. test creates random card data, creates card in auth.net createCreditCard trans type
        3. test checks users credit cards again to verify new card in api 

    """
    log.info('Authorize.Net: Create Card')

    # register a new anon user
    user = registerUser()
    log.debug('new anon user: '+ json.dumps(user, indent=2))

    me = getMe(user['access_token'])
    log.debug('getMe returns: \n'+json.dumps(me, indent=2))

    # brand new user, should have no cards
    headers = {'Content-Type':'application/json', 'Authorization':'Bearer '+ user['access_token']} #TODO: Move to me tests
    meCC = requests.get(host+'/v1/me/creditcards', headers = headers)
    #log.debug(json.dumps(meCC.json(), indent=2))

    assert meCC.status_code is codes.ok
    totalCount = meCC.json()['Meta']['TotalCount']
    assert totalCount == 0

    # auth.net: create card
    card = createAuthCard(me['Buyer']['ID'], me['Username'], user['user']['Password'])
    log.debug(json.dumps(card, indent=2))

    # verify card was created in ordercloud api too
    meCC2 = requests.get(host+'/v1/me/creditcards', headers = headers)
    assert meCC2.status_code is codes.ok
    totalCount = meCC2.json()['Meta']['TotalCount']
    assert totalCount == 1


def test_AuthorizeNet_AuthOnly():
    """
        two variants: with previously created, with new card
        requires: userID, buyerID, orderID & direciton, ammount
    """
    log.info('Authorize.Net: Auth Only')
    pass











