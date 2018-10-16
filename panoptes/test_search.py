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


from .auth import get_Token_UsernamePassword
from .products import get_Products, patch_Product
from .me import get_meProducts
from .productFacets import createProductFacet


fake = Faker()

log = logging.getLogger(__name__)


log.debug('Basic Search Tests Begun...')


@pytest.mark.parametrize("buyer_endpoint", [
    "me/products"
])
@pytest.mark.Description("facets should only be returned in the meta for faceted lists, not all lists. current facet lists: me/products")
def test_NoFacetsReturnedForNonFacetLists(configInfo, buyer_endpoint):
    '''
    facets should only be returned in the meta for faceted lists, not all lists
    current facet lists:
    - me/products
    '''

    client_id = configInfo['ADMIN-CLIENTID']
    username = configInfo['ADMIN-USERNAME']
    password = configInfo['ADMIN-PASSWORD']
    scope = ['FullAccess']

    # can successfully get a token
    adminToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    client_id = configInfo['BUYER-CLIENTID']
    username = configInfo['BUYER-USERNAME']
    password = configInfo['BUYER-PASSWORD']
    scope = ['Shopper']

    buyerToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    buyer = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + buyerToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    buyer.headers.update(headers)

    admin = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + adminToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    admin.headers.update(headers)

    log.info(json.dumps(
        buyer.get(configInfo['API'] + 'v1/me').json(), indent=4))
    log.info(json.dumps(
        admin.get(configInfo['API'] + 'v1/me').json(), indent=4))

    facetList = admin.get(configInfo['API'] + 'v1/ProductFacets')

    assert facetList.status_code is codes.ok

    should_not_have_facet_meta = buyer.get(
        configInfo['API'] + 'v1/' + buyer_endpoint)
    log.info(should_not_have_facet_meta.json()['Meta'])

    assert should_not_have_facet_meta.status_code is codes.ok
    assert 'Facets' not in should_not_have_facet_meta.json()['Meta']


@pytest.mark.parametrize("endpoint", [
    "products"
])
def test_FacetsReturnedForFacetLists(configInfo, endpoint):
    '''
            facets should only be returned in the meta for faceted lists, not all lists
            current facet lists:
            - me/products
    '''

    client_id = configInfo['ADMIN-CLIENTID']
    username = configInfo['ADMIN-USERNAME']
    password = configInfo['ADMIN-PASSWORD']
    scope = ['FullAccess']

    # can successfully get a token
    adminToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    client_id = configInfo['BUYER-CLIENTID']
    username = configInfo['BUYER-USERNAME']
    password = configInfo['BUYER-PASSWORD']
    scope = ['Shopper']

    buyerToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    buyer = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + buyerToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    buyer.headers.update(headers)

    admin = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + adminToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    admin.headers.update(headers)

    log.info(json.dumps(
        buyer.get(configInfo['API'] + 'v1/me').json(), indent=4))
    log.info(json.dumps(
        admin.get(configInfo['API'] + 'v1/me').json(), indent=4))

    should_have_facet_meta = buyer.get(
        configInfo['API'] + 'v1/Me/' + endpoint)
    log.info(should_have_facet_meta.json()['Meta'])

    assert should_have_facet_meta.status_code is codes.ok
    assert 'Facets' in should_have_facet_meta.json()['Meta']


@pytest.mark.search
def test_NoAccessForNonFacetOrgs(configInfo):
    '''
    if a user attempts to access facets (such as facets endpoint, or find facets in list meta) from an org without Premium Search turned on, there should be a friendly error. Not an empty list.

    # TODO: expand to use a non facet org 
    '''

    client_id = configInfo['ADMIN-CLIENTID']
    username = configInfo['ADMIN-USERNAME']
    password = configInfo['ADMIN-PASSWORD']
    scope = ['FullAccess']

    # can successfully get a token
    adminToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    client_id = configInfo['BUYER-CLIENTID']
    username = configInfo['BUYER-USERNAME']
    password = configInfo['BUYER-PASSWORD']
    scope = ['Shopper']

    buyerToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    buyer = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + buyerToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    buyer.headers.update(headers)

    admin = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + adminToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    admin.headers.update(headers)

    log.info(json.dumps(
        buyer.get(configInfo['API'] + 'v1/me').json(), indent=4))
    log.info(json.dumps(
        admin.get(configInfo['API'] + 'v1/me').json(), indent=4))

    facetList = admin.get(configInfo['API'] + 'v1/ProductFacets')

    assert facetList.status_code is codes.ok


@pytest.mark.search
@pytest.mark.skip("needs adjusted to handle misspellings better")
@pytest.mark.parametrize("search_query", [
    'data',
    'datas',
    'particular',
    'partikular',
    'sentences',
    'sentances'
])
def test_FuzzySearch(configInfo, search_query):

    #/me/products?search=data&searchOn=Description

    client_id = configInfo['BUYER-CLIENTID']
    username = configInfo['BUYER-USERNAME']
    password = configInfo['BUYER-PASSWORD']
    scope = ['Shopper']

    buyerToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    buyer = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + buyerToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    buyer.headers.update(headers)

    params = {
        'searchOn': 'Description',
        'search': search_query,
        'pageSize': 100
    }

    searchQuery = params['search']
    log.info(searchQuery)

    fuzzy = buyer.get(configInfo['API'] + 'v1/me/products', params=params)
    assert fuzzy.status_code is codes.ok
    # log.info(json.dumps(fuzzy.json(), indent=4))

    log.info('Fuzzy Search: ' + params['search'])
    log.info(str(fuzzy.json()['Meta']['TotalCount']) + ' Results:')

    results = fuzzy.json()['Items']
    # log.info(json.dumps(fuzzy.json()['Items'], indent=4))

    count = 0
    for item in results:
        if searchQuery.lower() in item['Description'].lower():
            log.info('MATCH')
            count += 1
            # log.info(item['Description'])
        else:
            log.info('No Match :(')
            log.info(item['Description'].lower())

    # assert count == fuzzy.json()['Meta']['TotalCount']


def test_XPAlias(configInfo):

    #/me/products?search=data&searchOn=Description

    client_id = configInfo['BUYER-CLIENTID']
    username = configInfo['BUYER-USERNAME']
    password = configInfo['BUYER-PASSWORD']
    scope = ['Shopper']

    buyerToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    buyer = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + buyerToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    buyer.headers.update(headers)

    noalias = buyer.get(configInfo['API'] + 'v1/me/products',
                        params={'searchOn': 'xp=*', 'search': '', 'pageSize': 100})
    assert noalias.status_code is codes.ok

    alias = buyer.get(configInfo['API'] + 'v1/me/products',
                      params={'searchOn': 'xp', 'search': '', 'pageSize': 100})
    assert alias.status_code is codes.ok
    # log.info(json.dumps(fuzzy.json(), indent=4))

    assert alias.json()['Meta']['TotalCount'] == noalias.json()[
        'Meta']['TotalCount']

    totalCount = alias.json()['Meta']['PageSize']
    log.info(totalCount)

    for i in range(0, totalCount):
        log.info(i)
        # log.info(noalias.json()['Items'][i])
        # log.info(alias.json()['Items'][i])
        assert noalias.json()['Items'][i] == alias.json()['Items'][i]
