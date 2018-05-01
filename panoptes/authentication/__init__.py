import requests
from requests import codes
import logging
import json
from .. import auth, authhost, host, logger, createUserObj


def getTokenPasswordGrant(buyerUsername, buyerPassword, scope=''):
    payload = {
        'client_id': auth['buyerClientID'],
        'grant_type': 'password',
        'username': buyerUsername,
        'password': buyerPassword,
        'Scope': scope
    }
    headers = {'Content-Type': 'application/json'}

    r = requests.post(authhost + '/oauth/token', data=payload, headers=headers)

    assert r.status_code is codes.ok
    print(r.json())

    return r.json()['access_token']


def getTokenClientGrand():
    payload = {
        'client_id': auth['buyerClientID'],
        'grant_type': 'clientgrant',
        'username': buyerUsername,
        'password': buyerPassword,
        'Scope': scope
    }
    headers = {'Content-Type': 'application/json'}
    r = requests.post(authhost + '/oauth/token', data=payload, headers=headers)

    return r.json()['access_token']


def getAnonToken():
    log = logging.getLogger('Get Anon Token')

    data = {
        'client_id': auth['buyerClientID'],
        'scope': 'Shopper MeAdmin',
        'grant_type':'client_credentials'
    }

    headers = {'Content-Type':'Application/Json'}

    anonToken = requests.post(authhost+'/oauth/token', data = data, headers=headers)
    log.debug(anonToken.url)
    log.debug(anonToken.request.headers)
    log.debug(anonToken.request.body)
    log.debug(anonToken.json())
    assert anonToken.status_code is codes.ok

    return(anonToken.json())

def registerUser():
    log = logging.getLogger('Register Anon User')

    anonToken = getAnonToken()
    log.debug(anonToken)

    jsonObj = createUserObj()

    url = host+'/v1/me/register'
    querystring = {"anonUserToken": anonToken['access_token']}
    payload = json.dumps(jsonObj, indent=2)
    headers = {
    'Accept': "application/json",
    'Content-Type': "application/json",
    'Authorization': "Bearer "+anonToken['access_token']
    }

    user = requests.request("PUT", url, data=payload, headers=headers, params=querystring)

   
    log.info(user.request.url)
    log.info(user.request.headers)
    log.info(user.request.body)
    log.debug(user.json())


    assert user.status_code is codes.ok

    returnedUser = dict()
    returnedUser['access_token']= user.json()['access_token']
    returnedUser['user'] = json.loads(user.request.body)

    return(returnedUser)
