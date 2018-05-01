import requests
from . import auth, authhost


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

    return r.json()['access_token']


def getTokenClient():
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
