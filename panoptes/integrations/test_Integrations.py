# test platform integrations: auth.net, shipping rates
import requests
import pytest
from requests import codes
import sys
import json
import logging
from datetime import *
import urllib
from .. import host
from . import createAuthCard, logger
from ..me import getMe, meCardCreate
from ..authentication import registerUser
import configparser
sys.path.append("C:/api-check/panoptes/pytest")
from faker import Faker
fake = Faker()



def test_AuthorizeNet():
    #print(sys.path)
    log = logging.getLogger('Authorize.Net')

    user = registerUser()
    print(user)

    me = getMe(user['access_token'])
    log.debug(me.json())

    headers = {'Content-Type':'application/json', 'Authorization':'Bearer '+ user['access_token']} #TODO: Move to me tests
    meCC = requests.get(host+'/v1/me/creditcards', headers = headers)
    
    log.debug(meCC.request.url)
    log.debug(meCC.url)
    log.debug(meCC.status_code)

    log.debug(json.dumps(meCC.json(), indent=2))

    assert meCC.status_code is codes.ok
    totalCount = meCC.json()['Meta']['TotalCount']

    card = createAuthCard(me.json()['Buyer']['ID'], user['user']['Username'], user['user']['Password'])


test_AuthorizeNet()



