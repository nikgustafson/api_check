# filter user workflow tests
import requests
from requests import codes as codes
import pytest
import configparser
import json
import logging
import datetime
import urllib
from random import randint
from faker import Faker


from panoptes import host, auth

from . import fake

from panoptes import authentication



logger = logging.getLogger(__name__)


# @pytest.mark(usefixture('setEnv('')'))
#class TestAuth():


# Me List Endpoints

def getMe(token):
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
    logger.debug('headers: ')
    logger.debug(headers)
    r = requests.get(host + '/v1/me', headers=headers)
    assert r.status_code is codes.ok

    return r


def getMeProducts(buyerUsername, buyerPassword, search='', productID=''):
    if productID != '':
        productID = '/' + productID

        logger.debug('getMeProducts')
        token = getTokenPasswordGrant(buyerUsername, buyerPassword, 'Shopper')
        logger.debug('token: ' + token)
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
        logger.debug('headers: ')
        logger.debug(headers)
        r = requests.get(host+'/v1/me/products' + productID, headers=headers, params=search)
        return (r)


# 1
def test_MeGet():
    # get me succeeds, and user is active

    token = getTokenPasswordGrant(auth['buyerUsername'], auth['buyerPassword'], 'Shopper')
    user = getMe(token)
    logger.debug('user: ')
    logger.debug(json.dumps(user.json(), indent= 2))
    assert user.status_code == 200
    assert user.is_redirect is False
    assert user.json()['Username'] == auth['buyerUsername']
    assert user.json()['Active'] == True
    logger.info(user)


# 2
def test_MeProduct():

    logger.debug('test_MeProduct: Product List')
    productList = getMeProducts(auth['buyerUsername'], auth['buyerPassword'])
    logger.debug(productList.url)
    assert productList.status_code == 200
    assert productList.is_redirect is False

    assert productList.json()['Meta']['TotalCount'] > 5
    randProduct = productList.json()['Items'][randint(0, productList.json()['Meta']['PageSize'] - 1)]
    logger.info("Random Product: " + str(randProduct))

    logger.debug('test_MeProduct: Product GET')
    productList = getMeProducts(auth['buyerUsername'], auth['buyerPassword'], productID=randProduct['ID'])
    logger.debug(productList.url)
    logger.debug(str(randProduct['ID']))

    assert productList.status_code == 200
    assert productList.is_redirect is False


# logger.info("Product List: "+str(productList))


searchParams = (["catalogID", "smokebuyer01"], ["search", "*w*"], ["sortBy", "name"], ["page", 5], ["pageSize", 100])
# filterParams =

ids = []

for item in searchParams:
    ids.append(item[0] + '-' + str(item[1]))


@pytest.mark.parametrize("searchParams", searchParams, ids=ids, )
# 3
def test_MeProductFilter(searchParams):
    allProducts = getMeProducts(auth['buyerUsername'], auth['buyerPassword'])
    logger.debug(allProducts.url)
    assert allProducts.status_code == 200
    totalProducts = allProducts.json()['Meta']['TotalCount']
    totalPages = allProducts.json()['Meta']['TotalPages']
    logger.debug(totalProducts)
    logger.debug(totalPages)

    # filters

    logger.debug('test_MeProductFilter ' + str(searchParams[0]) + ' expects ' + str(searchParams[1]))

    filters = {searchParams[0]: str(searchParams[1])}
    print(filters)

    filterProducts = getMeProducts(auth['buyerUsername'], auth['buyerPassword'], filters)
    logger.debug(filterProducts.url)
    assert allProducts.status_code == 200
    assert filterProducts.url == (
                host+'/v1/me/products?' + str(searchParams[0]) + '=' + urllib.parse.quote_plus(
            str(searchParams[1])))
    filterProducts = allProducts.json()['Meta']['TotalCount']
    filterPages = allProducts.json()['Meta']['TotalPages']
    logger.debug(filterProducts)
    logger.debug(filterPages)


# what we want: 'catalogID','search',"sortBy","page","pageSize" x filters


def meCardCreate(username, password):
    logger.debug('ME: Create Credit Card ')

    user = getMe(username, password, 'MeCreditCardAdmin')
    # TODO: refactor scope to be array of strings
    assert user.status_code == codes.ok

    headers = user.request.headers
    # assert headers.json()['Authorization'] TODO: to be able to assert user has current priv, add jwt decode
    logger.debug(headers)
    logger.debug(json.dumps(user.json(), indent=2))

    cardNumber = fake.credit_card_number(card_type=None)

    fullCard = {
        "BuyerID": '',
        "TransactionType": "createCreditCard",
        "CardDetails": {
            "CardholderName": user.json()['FirstName'] + ' ' + user.json()['LastName'],
            "CardType": fake.credit_card_provider(card_type=None),
            "CardNumber": cardNumber,
            "ExpirationDate": fake.credit_card_expire(start="now", end="+10y", date_format="%Y/%m/%d"),
            "CardCode": cardNumber[-4:],
            "Shared": False
        }
    }

    partialCard = {
        "CardType": fullCard["CardDetails"]['CardType'],
        "CardholderName": fullCard["CardDetails"]['CardholderName'],
        "ExpirationDate": fullCard["CardDetails"]['ExpirationDate'],
        "PartialAccountNumber": fullCard["CardDetails"]['CardCode'],
        "Token": "",
        "xp": {}
    }

    # logger.debug(partialCard)
    logger.debug(fullCard)

    card = requests.post(host+'/v1/me/creditcards', headers=headers, json=partialCard)
    logger.debug(card.url)
    logger.debug(card.request.body)
    logger.debug(json.dumps(card.json(), indent=2))
    assert card.status_code == codes.created

    return (fullCard)

