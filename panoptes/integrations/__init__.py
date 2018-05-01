from .. import auth, authhost, authnet, createUserObj
from ..me import meCardCreate
from ..authentication import getTokenPasswordGrant
import json
import requests
import collections


def createAuthCard(BuyerID, username, password):
    token = getTokenPasswordGrant(username, password, 'MeCreditCardAdmin')

    newCard = meCardCreate(token) # creates card in ordercloud api
    
    card = json.loads(newCard)


    card['BuyerID'] = BuyerID


    headers = {'Content-Type':'application/json; charset=UTF-8', 'Authorization':'Bearer '+ token}
    
    authCard = requests.post(authnet, headers = headers, json = card)

    request = collections.namedtuple('url', authCard.request.url, 'headers', authCard.request.headers, 'body', authCard.request)

    print(request)
    assert authCard.status_code is codes.created
    assert authCard.json()['ResponseHttpStatusCode'] is codes.created


    return(authCard)
    


