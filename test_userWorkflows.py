# user workflow tests
import requests
import pytest
import configparser
import json


config = configparser.ConfigParser()
config.read('config.ini')
auth = config['AUTH']

environments = {'api':['api', 'qaapi'], 'auth':['auth', 'qaauth']}

# Auth Tests

def getTokenBuyer(buyerUsername, buyerPassword):
    payload = {
    'client_id':auth['buyerClientID'],
    'grant_type': 'password',
    'username' : auth['buyerUsername'],
    'password':auth['buyerPassword'],
    'Scope':'Buyer'
    }
    headers = {'Content-Type':'application/json'}
    r = requests.post('https://auth.ordercloud.io/oauth/token', data = payload, headers = headers)

    return(r.json()['access_token'])

def getUser(buyerUsername, buyerPassword):
    token = getTokenBuyer(buyerUsername, buyerPassword)
    headers = {'Content-Type':'application/json', 'Authorization':'Bearer '+ token}
    r = requests.get('https://api.ordercloud.io/v1/me', headers = headers)
    print(r.content)



def main():
    getUser(auth['buyerUsername'], auth['buyerPassword'])


main()
