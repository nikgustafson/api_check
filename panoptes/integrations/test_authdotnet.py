

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

'''
If you google the Auth.net error code, this seems to be a nagging issue when you create a new profile and then immediately try to use it. Some users have indicated that introducing a delay is an effective work-around.

Kate Reeher or Vince Fenton Here's a scenario it would be great if we could try:

1. Send a createCreditCard transaction with a user where CardDetails.Shared (in the request body) is false AND user.xp.AuthorizeNetProfileID does not exist. You should get the error.

2. Get that user and see if xp.AuthorizeNetProfileID was set in step 1, despite it ultimately failing.

3. If xp.AuthorizeNetProfileID was populated, do another createCreditCard with that user and see if it succeeds the second time.

If this all goes as I think it might, it means forcing a delay should help. I just don't know how to test it.
'''


@pytest.mark.description('Attempting to create a card in auth.net for a newly registered user should work.')
def test_createCardNewUser(configInfo):

    client_id = configInfo['BUYER-CLIENTID']
    scope = ['Shopper']

    # get an anon token
    token = auth.get_anon_user_token(configInfo, client_id)

    # can use that token to make calls

    user = me.get_Me(configInfo, token['access_token'])

    #buyerToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c3IiOiJqb3JkYW5AbWFpbGluYXRvci5jb20iLCJjaWQiOiJhYTM2MTJhZC0wOThkLTQ0ZTEtOGQ1ZC00MWFlMTk5NGVlZmEiLCJpbXAiOiIzNjkyMCIsInVzcnR5cGUiOiJidXllciIsInJvbGUiOiJGdWxsQWNjZXNzIiwiaXNzIjoiaHR0cHM6Ly9hdXRoLm9yZGVyY2xvdWQuaW8iLCJhdWQiOiJodHRwczovL2FwaS5vcmRlcmNsb3VkLmlvIiwiZXhwIjoxNTM4NDk0Mjc2LCJuYmYiOjE1Mzg0OTA2NzZ9.MyR7d_3XaBCRYqXCcONaPxmSlI-7SKO7oYfAWBgF77U'
    #buyerToken = auth.get_Token_UsernamePassword(configInfo, client_id, username, password, scope)

    # register the anon user as a new user
    buyerToken = me.registerMe(configInfo, token)

    user = me.get_Me(configInfo, buyerToken)
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
        'buyerID': "AACBuyer"
    }

    #log.info(json.dumps(requestBody, indent=4))

    newCard = createCreditCard(configInfo, requestBody, buyerToken)

    assert newCard['ResponseHttpStatusCode'] is codes.ok

    user = me.get_Me(configInfo, buyerToken)
    #log.info(json.dumps(user, indent=4))

    assert 'AuthorizeNetProfileID' in user['xp'].keys()


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
        'buyerID': "AACBuyer"
    }

    #log.info(json.dumps(requestBody, indent=4))

    newCard = createCreditCard(configInfo, requestBody, buyerToken)

    assert newCard['ResponseHttpStatusCode'] is codes.ok
    assert newCard['ResponseBody']['messages'][
        'message'][0]['code'] == 'E00039'

    user = me.get_Me(configInfo, buyerToken)
    #log.info(json.dumps(user, indent=4))

    assert 'AuthorizeNetProfileID' in user['xp'].keys()
