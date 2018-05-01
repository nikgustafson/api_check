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
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)


log = logging.getLogger(__name__)

# create file handler which logs even debug messages
#fh = logging.FileHandler('../logs/'+__name__+'.log')

def test_AuthorizeNet():
    #print(sys.path)
    log.info('Authorize.Net')

    user = registerUser()
    log.debug(user)

    me = getMe(user['access_token'])
    log.debug('getMe returns: '+ str(type(me)) + '\n'+str(me))

    headers = {'Content-Type':'application/json', 'Authorization':'Bearer '+ user['access_token']} #TODO: Move to me tests
    meCC = requests.get(host+'/v1/me/creditcards', headers = headers)
    
    log.debug(meCC.request.url)
    log.debug(meCC.url)
    log.debug(meCC.status_code)

    log.debug(json.dumps(meCC.json(), indent=2))

    assert meCC.status_code is codes.ok
    totalCount = meCC.json()['Meta']['TotalCount']

    card = createAuthCard(me['Buyer']['ID'], user['user']['Username'], user['user']['Password'])


test_AuthorizeNet()



