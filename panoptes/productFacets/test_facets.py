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
from . import createProductFacet, assignProductFacet, makeFacetAndAssignValues


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

    newFacet = makeFacetAndAssignValues(configInfo, buyer, admin, nested, 1, 1)

    log.info(newFacet)


def test_verifyMinCount0(configInfo, connections):

    admin = connections['admin']
    buyer = connections['buyer']

    #----------------------------#

    newFacet = makeFacetAndAssignValues(configInfo, buyer, admin, None, 0, 0)

    log.info(newFacet)
    assert facetName in facetNames


def test_deletion(configInfo, connections):
    pass


def test_normal(configInfo, connections):
    pass


def test_facetCreation(configInfo, connections):

    buyer = connections['buyer']
    admin = connections['admin']

    # 1. create a facet as an admin user
