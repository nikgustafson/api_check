

import pytest
import requests
from requests import codes
import logging
import json
import time
from faker import Faker
from random import randint

from .. import me
from .. import auth

from ..integrations import listServers, listEmails, findEmail, awaitEmail, getEmail, deleteEmail, createCreditCard


fake = Faker()
log = logging.getLogger(__name__)


@pytest.mark.skip('Bugged in 1.0.85: EX-1705')
@pytest.mark.smoke
@pytest.mark.description('Attempting to create a card in auth.net for a newly registered user should work.')
def test_createCardNewUser(configInfo, connections):

    client_id = configInfo['BUYER-CLIENTID']
    scope = ['Shopper']

    # get an anon session
    session = connections['anon']
    # log.info(session.headers)
    #token = auth.get_anon_user_token(configInfo, client_id)

    # register the anon user as a new user
    newUserToken = me.registerMe(configInfo, session)
    #log.info(json.dumps(newUserToken, indent=4))

    user = me.get_Me(configInfo, newUserToken)
    #log.info(json.dumps(user, indent=4))

    assert 'AuthorizeNetProfileID' not in user['xp'].keys()
    # if 'AuthorizeNetProfileID' in user['xp'].keys():
    #	me.patch_Me(configInfo, buyerToken, {'xp.AuthorizeNetProfileID':None})

    # create a new card through auth.net

    requestBody = {
        'CardDetails': {
            'CardCode': "123",
            'CardNumber': "4111111111111111",
            'CardType': "visa",
            'CardholderName': user['FirstName'] + ' ' + user['LastName'],
            'ExpirationDate': "0321",
            'Shared': False
        },
        'TransactionType': "createCreditCard",
        'buyerID': configInfo['BUYER']
    }

    #log.info(json.dumps(requestBody, indent=4))

    newCard = createCreditCard(configInfo, requestBody, newUserToken)

    assert newCard['ResponseHttpStatusCode'] is codes.ok

    user = me.get_Me(configInfo, newUserToken)
    log.info(json.dumps(user, indent=4))

    assert 'AuthorizeNetProfileID' in user['xp'].keys()


@pytest.mark.skip('Bugged in 1.0.85: EX-1705')
@pytest.mark.smoke
@pytest.mark.description('Attempting to create a card that already exists should return an Auth.Net duplicate payment profile error')
def test_createCardExistingUser(configInfo):

    client_id = configInfo['BUYER-CLIENTID']
    username = configInfo['BUYER-USERNAME']
    password = configInfo['BUYER-PASSWORD']
    scope = ['Shopper', 'MeAdmin']

    buyerToken = auth.get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    user = me.get_Me(configInfo, buyerToken)
    #log.info(json.dumps(user, indent=4))

    assert 'AuthorizeNetProfileID' in user['xp'].keys()

    # create a new card through auth.net

    requestBody = {
        'CardDetails': {
            'CardCode': "123",
            'CardNumber': "4111111111111111",
            'CardType': "visa",
            'CardholderName': user['FirstName'] + ' ' + user['LastName'],
            'ExpirationDate': "0321",
            'Shared': False
        },
        'TransactionType': "createCreditCard",
        'buyerID': configInfo['BUYER']
    }

    #log.info(json.dumps(requestBody, indent=4))

    newCard = createCreditCard(configInfo, requestBody, buyerToken)

    assert newCard['ResponseHttpStatusCode'] is codes.ok
    assert newCard['ResponseBody']['messages'][
        'message'][0]['code'] == 'E00039'

    user = me.get_Me(configInfo, buyerToken)
    #log.info(json.dumps(user, indent=4))

    assert 'AuthorizeNetProfileID' in user['xp'].keys()
