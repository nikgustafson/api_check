

import pytest
import requests
from requests import codes
import logging
import json
import time
from faker import Faker
from random import randint
import jwt


from .. import me
from .. import auth
from ..me import get_Me

from ..integrations import listServers, listEmails, findEmail, awaitEmail, getEmail, deleteEmail, createCreditCard


fake = Faker()
log = logging.getLogger(__name__)


#@pytest.mark.skip('Bugged in 1.0.85: EX-1705')
@pytest.mark.smoke
@pytest.mark.description('Attempting to create a card in auth.net for a newly registered user or established user should work.')
@pytest.mark.parametrize("sessions", [
    "anon",
    "buyer",
    "registered"
])
def test_createCardNewUser(configInfo, connections, sessions, registerAnonUser):

    # log.info(connections[sessions].headers)
    session = connections[sessions]

    decoded = jwt.decode(connections[sessions].headers[
                         'Authorization'][7:], verify=False)
    log.debug(decoded)

    client_id = decoded['cid']

    scope = ['Shopper']

    user = get_Me(configInfo, session)
    log.debug(json.dumps(user, indent=4))

    if user['xp'] is not None:
        log.debug(user['xp'])
        assert 'AuthorizeNetProfileID' not in user['xp'].keys()
        # if 'AuthorizeNetProfileID' in user['xp'].keys():
        #	me.patch_Me(configInfo, buyerToken, {'xp.AuthorizeNetProfileID':None})

    # create a new card through auth.net

    requestBody = {
        'CardDetails': {
            'CardCode': fake.credit_card_security_code(card_type='visa13'),
            'CardNumber': fake.credit_card_number(card_type="visa13"),
            'CardType': "Visa",
            'CardholderName': user['FirstName'] + ' ' + user['LastName'],
            'ExpirationDate': fake.credit_card_expire(start="now", end="+10y", date_format="%m%y"),
            'Shared': False
        },
        'TransactionType': "createCreditCard",
        'buyerID': configInfo['BUYER']
    }

    log.debug(json.dumps(requestBody, indent=4))

    newCard = createCreditCard(configInfo, requestBody, session)

    assert newCard['ResponseHttpStatusCode'] is codes.ok

    user = me.get_Me(configInfo, session)
    log.debug(json.dumps(user, indent=4))

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
