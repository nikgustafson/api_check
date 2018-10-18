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

from ..auth import get_Token_UsernamePassword
from ..products import get_Products, patch_Product
from ..me import get_meProducts
from ..productFacets import sessionInit


fake = Faker()

log = logging.getLogger(__name__)


def test_facetCreation(configInfo):

    sessions = sessionInit(configInfo)
    buyer = sessions[0]
    admin = sessions[1]

    #log.info(json.dumps(buyer.get(configInfo['API']+'v1/me').json(), indent=4))
    #log.info(json.dumps(admin.get(configInfo['API']+'v1/me').json(), indent=4))

    # 1. create a facet as an admin user

    facetList = admin.get(configInfo['API'] + 'v1/ProductFacets')

    name = fake.sentences(nb=1, ext_word_list=None)[0]
    path = name.replace(' ', '-')

    newFacets = {
        'facet01': {
            "ID": 'facet-' + fake.uuid4(),
            "Name": name,
            "XpPath": path,
            "ListOrder": 3,
            "MinCount": 1
        }
    }

    # log.info((newFacets['facet01']['Name']))
    # log.info((newFacets['facet01']['XpPath']))

    facet = admin.post(configInfo['API'] +
                       'v1/ProductFacets', json=newFacets['facet01'])
    assert facet.status_code is codes.created
    log.info(json.dumps(facet.json(), indent=4))

    # 2. create some products with that XP

    products = getRandomProducts(configInfo, buyer)
    # log.info(products)

    patchXP(configInfo, admin, products, newFacets)
