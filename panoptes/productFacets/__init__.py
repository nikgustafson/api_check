import pytest
import requests
from requests import codes
import logging
import json
from faker import Faker
import random
from random import randint
import urllib
import time
from ..helpers import blns


from ..auth import get_Token_UsernamePassword
from ..products import get_Products, patch_Product
from ..me import get_meProducts


fake = Faker()

log = logging.getLogger(__name__)


def getRandomProducts(configInfo, buyerSession, pageSize=10):

    productList = buyerSession.get(
        configInfo['API'] + 'v1/Me/Products', params={'pageSize': pageSize}).json()

    productTotal = productList['Meta']['TotalCount']
    pageTotal = productList['Meta']['TotalPages']

    randomPage = random.choice(range(1, pageTotal - 1))

    assert randomPage <= pageTotal

    log.info("Page " + str(randomPage) + " of " + str(pageTotal))

    productIDs = []

    for item in productList['Items']:
        productIDs.append(item['ID'])

    log.info(productIDs)

    return productIDs


def patchXP(configInfo, admiSession, products, newFacets):
    log.info(json.dumps(newFacets, indent=4))

    for facet in newFacets:
        log.info(facet)
        # TODO: build out support for nested xp
        patchBody = {
            'xp': {
                # TODO: make this parameterized and include wider array of
                # values
                newFacets[facet]['XpPath']: fake.word(ext_word_list=None)
            }
        }
        for productID in products:
            log.info(productID)
            try:
                patched = admiSession.patch(
                    configInfo['API'] + 'v1/products/' + productID, json=patchBody)
                log.info(patched.status_code)
                log.info(patched.request.headers)
                log.info(patched.request.url)
                log.info(patched.request.body)
                log.info(patched.text)
                assert patched.status_code is codes.ok
                log.info(json.dumps(patched.json(), indent=4))

            except requests.exceptions.RequestException as e:  # This is the correct syntax
                log.info(e)
                sys.exit(1)


def createProductFacet(configInfo, productFacet, session):

    try:
        facet = session.post(configInfo['API'] +
                             'v1/ProductFacets', json=productFacet)
        # log.info(facet.request.url)
        # log.info(facet.request.body)
        # log.info(facet.text)
        assert facet.status_code is codes.created
        # log.info(json.dumps(facet.json(), indent=4))
        return facet
    except:
        raise


def assignProductFacet(configInfo, session, productID, facetPath, value):
    '''
        create a value for a facet by building up an xp dict (levels of facet, facet value), then patching the product with that xp dict
    '''

    xpBody = {
        'xp': ''
    }
    xp = {}
    if '.' in facetPath:
        levels = facetPath.split(sep='.')
        xpBody['xp'] = xp

        l = len(levels)
        i = 0
        v = value
        body = {}
        while i < l:
            body = {levels[l - 1]: v}
            log.info(body)
            l -= 1
            v = body
        xpBody['xp'] = body
        log.info(xpBody)

    else:
        xpBody['xp'] = {facetPath: value}
        log.info(xpBody)

    patchedProduct = session.patch(configInfo['API'] + 'v1/products/' +
                                   productID, json=xpBody)
    log.info(json.dumps(patchedProduct.json(), indent=2))
    log.info(patchedProduct.status_code)


def makeAFacet(configInfo, admin, nested, mincount):

    # now, make a facet!
    name = fake.words(nb=random.randrange(2, 6))

    facetBody = {}

    if nested == True:
        facetBody = {
            "ID": 'facet-' + fake.uuid4(),
            "Name": str('.'.join(name)),
            "XpPath": str('.'.join(name)),
            "ListOrder": 0,
            "MinCount": mincount
        }

    else:
        facetBody = {
            "ID": 'facet-' + fake.uuid4(),
            "Name": str(' '.join(name)),
            "XpPath": str('-'.join(name)),
            "ListOrder": 0,
            "MinCount": mincount
        }

    newFacet = createProductFacet(configInfo, facetBody, admin)

    return newFacet.json()


def makeFacetAndAssignValues(configInfo, buyer, admin, nested, minCount, numValues):

    # get the products to assign facet values to...

    if numValues > 20:
        pageSize = numValues
    else:
        pageSize = 20

    # get some products to assign values to
    buyerProducts = buyer.get(
        configInfo['API'] + 'v1/me/products', params={'PageSize': pageSize})
    assert buyerProducts.status_code is codes.ok

    randomPick = random.randrange(0, pageSize - 1)
    randomProducts = random.choices(buyerProducts.json()['Items'], k=numValues)
    # log.info(randomProducts)

    # make that facet
    newFacet = makeAFacet(configInfo, admin, nested, minCount)

    # check to see if the facet shows up in the meta facet
    facetList = buyer.get(configInfo['API'] + 'v1/me/products')

    # values should only show up if minCount = 0 here, because no values yet
    facetNames = []
    for each in facetList.json()['Meta']['Facets']:
        facetNames.append(each['Name'])
    log.info(facetNames)
    #log.info('wait for the product index...')
    # time.sleep(60)
    if minCount > 0:
        assert newFacet['Name'] not in facetNames
    elif minCount == 0:
        assert newFacet['Name'] not in facetNames

    # let's assign some values

    valueOptions = [True, False, fake.catch_phrase(), random.choice(blns.list)]
    # add a value
    for each in randomProducts:
        facetValue = assignProductFacet(
            configInfo, admin, productID=each['ID'], facetPath=newFacet['XpPath'], value=random.choice(valueOptions))

    log.info('wait for the product index...')
    time.sleep(100)

    facetNames = []
    for each in facetList.json()['Meta']['Facets']:
        facetNames.append(each['Name'])

    log.info(facetNames)
    if minCount >= 0:
        assert newFacet['Name'] in facetNames
    else:
        assert newFacet['Name'] not in facetNames

    return True


def getProductFacets(configInfo, token, params):

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    try:
        pFacet = requests.get(
            configInfo['API'] + 'v1/ProductFacets/', headers=headers, params=params)
        log.debug(pFacet.request.url)
        log.debug(pFacet.status_code)
        log.debug(json.dumps(pFacet.json(), indent=2))

        assert pFacet.status_code is codes.ok
        return pFacet.json()
    except requests.exceptions.RequestException as e:
        log.debug(json.dumps(pFacet.json(), indent=2))
        print(e)
        sys.exit(1)


def adminProductFacet(configInfo, token, facet):

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    try:
        pFacet = requests.post(
            configInfo['API'] + 'v1/ProductFacets/', headers=headers, json=facet)
        log.debug(pFacet.request.url)
        log.debug(pFacet.status_code)
        log.debug(json.dumps(pFacet.json(), indent=2))

        assert pFacet.status_code is codes.created
        return pFacet.json()
    except requests.exceptions.RequestException as e:
        log.debug(json.dumps(pFacet.json(), indent=2))
        print(e)
        sys.exit(1)
