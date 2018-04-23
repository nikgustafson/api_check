# test platform integrations: auth.net, shipping rates
import requests
import pytest
from requests import codes
import sys
import json
import logging
from datetime import *
import urllib
import configparser
sys.path.append("C:/api-check/pytest")
from test_Me import meCardCreate, getMe
from faker import Faker
fake = Faker()

config = configparser.ConfigParser()
config.read('../config.ini')
auth = config['LOCUST-AUTH']

logging.basicConfig(filename='testRun.log', level=logging.DEBUG, filemode = 'w')
env = ''
host = 'https://'+env+'api.ordercloud.io'
authhost = 'https://'+env+'auth.ordercloud.io'

#log = logging.getLogger('Authorize.Net')
# auth.net

authnet = host+'/v1/integrationproxy/Authorize.Net'

def createAuthCard(BuyerID):

    card = meCardCreate() # creates card in ordercloud api
    card['BuyerID'] = BuyerID

    log.debug(card)
    user = getMe(auth['buyerUsername'], auth['buyerPassword'], 'Shopper')
    log.debug(json.dumps(user.json(), indent=2))
    assert user.status_code == codes.ok
    
    authCard = requests.post(authnet, headers = user.headers, json = card)
    log.debug(authCard.request)
    log.debug(authCard.url)
    log.debug(authCard.text)
    assert authCard.status_code is codes.created

    #c = requests.post(authnet, )


def registerUser():
    log = logging.getLogger('Register Anon User')


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


    newUserID = fake.ean8()

    jsonObj = {
      'ID' : newUserID,
      'Username' : fake.user_name(),
      'FirstName' : fake.first_name(),
      'LastName' : fake.last_name(),
      'Email' : newUserID+'@ordercloud-qa.mailinator.com',
      'Phone' : fake.phone_number(),
      'TermsAccepted':'2018-04-23T14:35:10.8939165-05:00',#datetime.utcnow().strftime('%Y'),
      'Active' : 'True',
      'xp' : {}
    }

    url = host+'/v1/me/register'
    querystring = {"anonUserToken": anonToken.json()['access_token']}

    payload = json.dumps(jsonObj, indent=2)

    headers = {
    'Accept': "application/json",
    'Content-Type': "application/json",
    'Authorization': "Bearer "+anonToken.json()['access_token']
    }

    user = requests.request("PUT", url, data=payload, headers=headers, params=querystring)

   
    log.debug(user.request.url)
    log.debug(user.request.headers)
    log.debug(user.request.body)
    log.debug(user.json())


    assert user.status_code is codes.ok



def test_AuthorizeNet():
    #print(sys.path)
    log = logging.getLogger('Authorize.Net')

    user = registerUser()
    log.debug(user)

    me = getMe(auth['buyerUsername'], auth['buyerPassword'], 'Shopper')
    log.debug(me.json())

    buyer = me.json()['Buyer']['ID']

    card = createAuthCard(buyer)


test_AuthorizeNet()



