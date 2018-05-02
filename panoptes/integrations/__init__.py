from .. import auth, authhost, authnet, createUserObj, createCreditCardObj
from ..me import meCardCreate
from ..authentication import getTokenPasswordGrant
import json
import requests
from requests import codes
import logging



def createAuthCard(BuyerID, username, password):
    """
    creates a credit card in the ordercloud api AND in the auth.net integration
    auth.net should not have to create a card in ordercloud
    """

    logger = logging.getLogger('integrations/createAuthCard')


    token = getTokenPasswordGrant(username, password, 'MeCreditCardAdmin')

    #newCard = meCardCreate(token) # creates card in ordercloud api
    
    newCard = createCreditCardObj()
    logger.info('returned card obj: '+json.dumps(newCard, indent=2))

    CardDetails = {
        "CardholderName": newCard['CardholderName'],
        "CardType": newCard['CardType'],
        "CardNumber": newCard['CardNumber'],
        "ExpirationDate": newCard['ExpirationDate'],
        "CardCode": newCard['CardCode'],
        "Shared": newCard['Shared'] 
    }

    authCard = {
    "BuyerID": BuyerID,
    "TransactionType": "createCreditCard",
    }

    authCard['CardDetails'] = CardDetails

    logger.debug(json.dumps(authCard, indent=2))

    head = {'Content-Type':'application/json; charset=UTF-8', 'Authorization':'Bearer '+ token}
    
    authCard = requests.post(authnet, headers = head, json = authCard)

    logger.debug('response: '+json.dumps(authCard.json(), indent=2))
    assert authCard.status_code is codes.created
    assert authCard.json()['ResponseHttpStatusCode'] is codes.created


    return(authCard.json())
    


