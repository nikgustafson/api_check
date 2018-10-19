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
from . import createProductFacet, assignProductFacet


fake = Faker()

log = logging.getLogger(__name__)

# https://four51.atlassian.net/browse/EX-1678

#@pytest.mark.parametrize("sessions", ['buyer', 'anon'])


@pytest.mark.parametrize('nested', [True, False])
@pytest.mark.description('A Facet\'s Min Count controls how many **VALUES** must exist for that facet before the facet will show up in the Facet Meta. Min Count = 1')
def test_verifyMinCount1(configInfo, connections, nested):

    admin = connections['admin']
    buyer = connections['buyer']

    #----------------------------#
    # buyer product list
    buyerProducts = buyer.get(configInfo['API'] + 'v1/me/products')
    assert buyerProducts.status_code is codes.ok
    pageSize = buyerProducts.json()['Meta']['PageSize']
    randomPick = random.randrange(0, pageSize - 1)
    randomProductID = buyerProducts.json()['Items'][randomPick]['ID']

    # now, make some facets!
    name = fake.words(nb=random.randrange(2, 6))

    facetBody = {}

    if nested == True:

        facetBody = {
            "ID": 'facet-' + fake.uuid4(),
            "Name": str('.'.join(name)),
            "XpPath": str('.'.join(name)),
            "ListOrder": 0,
            "MinCount": 1
        }

    else:
        facetBody = {
            "ID": 'facet-' + fake.uuid4(),
            "Name": str(' '.join(name)),
            "XpPath": str('-'.join(name)),
            "ListOrder": 0,
            "MinCount": 1
        }

    facetName = createProductFacet(configInfo, facetBody, admin)['Name']

    # shouldn't show up in facet list
    facetList = buyer.get(configInfo['API'] + 'v1/me/products')

    # log.info(facetList.json()['Meta']['Facets'])

    facetNames = []

    for each in facetList.json()['Meta']['Facets']:
        facetNames.append(each['Name'])

    # value mincount = 1, thus facet should not appear yet in facet meta list
    assert facetName not in facetNames

    valueOptions = [True, False, fake.catch_phrase(), random.choice(blns.list)]
    # add a value
    facetValue = assignProductFacet(
        configInfo, admin, productID=randomProductID, facetPath=facetBody['XpPath'], value=random.choice(valueOptions))

    time.sleep(300)  # wait for the index....

    # assert that the facet shows up now in facet meta list
    facetList = buyer.get(configInfo['API'] + 'v1/me/products')

    # log.info(facetList.json()['Meta']['Facets'])

    facetNames = []

    for each in facetList.json()['Meta']['Facets']:
        facetNames.append(each['Name'])
    log.info(facetNames)

    # value created, thus facet should now appear yet in facet meta list
    assert facetName in facetNames


def test_verifyMinCount0(configInfo, connections):

    admin = connections['admin']

    name = fake.words(nb=3)

    facetBody = {
        "ID": 'facet-' + fake.uuid4(),
        "Name": str(' '.join(name)),
        "XpPath": str('-'.join(name)),
        "ListOrder": 3,
        "MinCount": 0
    }

    facetName = createProductFacet(configInfo, facetBody, admin)['Name']

    buyer = connections['buyer']

    facetList = buyer.get(configInfo['API'] + 'v1/me/products')

    # log.info(facetList.json()['Meta']['Facets'])

    facetNames = []

    for each in facetList.json()['Meta']['Facets']:
        facetNames.append(each['Name'])

    log.info(facetNames)

    assert facetName in facetNames


def test_deletion(configInfo, connections):
    pass


def test_normal(configInfo, connections):
    pass


def test_facetCreation(configInfo, connections):

    buyer = connections['buyer']
    admin = connections['admin']

    # 1. create a facet as an admin user
