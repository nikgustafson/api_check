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
sys.path.append("C:/api-check/panoptes/pytest")
from test_Me import meCardCreate, getMe, getMeToken, getTokenBuyer
from faker import Faker
fake = Faker()

config = configparser.ConfigParser()
config.read('../config.ini')
auth = config['LOCUST-AUTH']


env = ''
host = 'https://'+env+'api.ordercloud.io'
authhost = 'https://'+env+'auth.ordercloud.io'

#log = logging.getLogger('Authorize.Net')
# auth.net

authnet = host+'/v1/integrationproxy/authorizenet'

def createAuthCard(BuyerID, username, password):
    log = logging.getLogger('Create Authorize.Net Card')

    card = meCardCreate(username, password) # creates card in ordercloud api
    card['BuyerID'] = BuyerID

    token = getTokenBuyer(username, password, 'MeCreditCardAdmin')

    headers = {'Content-Type':'application/json; charset=UTF-8', 'Authorization':'Bearer '+ token}
    
    authCard = requests.post(authnet, headers = headers, json = card)
    log.debug('auth.net url: '+authCard.url)
    log.debug('new card request body: \n'+json.dumps(json.loads(authCard.request.body), indent=2))
    log.debug('auth.net response: \n'+ json.dumps(authCard.json(), indent=2))
    assert authCard.status_code is codes.created
    assert authCard.json()['ResponseHttpStatusCode'] is codes.created
    

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

    newUserID = fake.ean8()

    jsonObj = {
      'ID' : newUserID,
      'Username' : fake.user_name(),
      'FirstName' : fake.first_name(),
      'LastName' : fake.last_name(),
      'Password': fake.password(),
      'Email' : newUserID+'@ordercloud-qa.mailinator.com',
      'Phone' : fake.phone_number(),
      'TermsAccepted':datetime.utcnow().strftime('%Y/%m/%d'),
      'Active' : 'True',
      'xp' : {}
    }

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



def test_AuthorizeNet():
    #print(sys.path)
    log = logging.getLogger('Authorize.Net')

    user = registerUser()
    print(user)

    me = getMeToken(user['access_token'])
    log.debug(me.json())

    headers = {'Content-Type':'application/json', 'Authorization':'Bearer '+ user['access_token']} #TODO: Move to me tests
    meCC = requests.get(host+'/v1/me/creditcards', headers = headers)
    log.debug(json.dumps(meCC.json(), indent=2))
    assert meCC.status_code is codes.ok
    totalCount = meCC.json()['Meta']['TotalCount']

    card = createAuthCard(me.json()['Buyer']['ID'], user['user']['Username'], user['user']['Password'])


test_AuthorizeNet()



