from .. import auth, authhost, authnet, createUserObj, logger
import logging

logger = logging.getLogger('Integration Tests')


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
    


