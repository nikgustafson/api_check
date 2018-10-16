
import json
import logging

import pytest

import requests

from .auth import get_Token_UsernamePassword
from faker import Faker
from requests import codes


fake = Faker()

log = logging.getLogger(__name__)


log.debug('Basic Search Tests Begun...')


@pytest.mark.parametrize("buyer_endpoint", [
    "products"
])
@pytest.mark.Description("facets should only be returned in the meta for faceted lists, not all lists. current facet lists: me/products")
def test_NoFacetsReturnedForNonFacetLists(configInfo, connections, buyer_endpoint):
    '''
    facets should only be returned in the meta for faceted lists, not all lists
    current facet lists:
    - me/products
    '''

    facetList = connections['admin'].get(
        configInfo['API'] + 'v1/ProductFacets')

    assert facetList.status_code is codes.ok

    should_not_have_facet_meta = connections['admin'].get(
        configInfo['API'] + 'v1/' + buyer_endpoint)
    log.debug(should_not_have_facet_meta.json()['Meta'])

    assert should_not_have_facet_meta.status_code is codes.ok
    assert 'Facets' not in should_not_have_facet_meta.json()['Meta']


@pytest.mark.parametrize("endpoint", [
    "products"
])
def test_FacetsReturnedForFacetLists(connections, configInfo, endpoint):
    '''
            facets should only be returned in the meta for faceted lists, not all lists
            current facet lists:
            - me/products
    '''

    should_have_facet_meta = connections['buyer'].get(
        configInfo['API'] + 'v1/Me/' + endpoint)
    log.debug(should_have_facet_meta.json()['Meta'])

    assert should_have_facet_meta.status_code is codes.ok
    assert 'Facets' in should_have_facet_meta.json()['Meta']


@pytest.mark.search
def test_NoAccessForNonFacetOrgs(configInfo, connections):
    '''
    if a user attempts to access facets (such as facets endpoint, or find facets in list meta) from an org without Premium Search turned on, there should be a friendly error. Not an empty list.

    # TODO: expand to use a non facet org 
    '''

    facetList = connections['admin'].get(
        configInfo['API'] + 'v1/ProductFacets')

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
    params = {
        'searchOn': 'Description',
        'search': search_query,
        'pageSize': 100
    }

    searchQuery = params['search']
    log.debug(searchQuery)

    fuzzy = connections['buyer'].get(
        configInfo['API'] + 'v1/me/products', params=params)
    assert fuzzy.status_code is codes.ok
    # log.info(json.dumps(fuzzy.json(), indent=4))

    log.debug('Fuzzy Search: ' + params['search'])
    log.debug(str(fuzzy.json()['Meta']['TotalCount']) + ' Results:')

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


def test_XPAlias(configInfo, connections):

    #/me/products?search=data&searchOn=Description

    noalias = connections['buyer'].get(configInfo['API'] + 'v1/me/products',
                                       params={'searchOn': 'xp=*', 'search': '', 'pageSize': 100})
    assert noalias.status_code is codes.ok

    alias = connections['buyer'].get(configInfo['API'] + 'v1/me/products',
                                     params={'searchOn': 'xp', 'search': '', 'pageSize': 100})
    assert alias.status_code is codes.ok
    log.info(json.dumps(fuzzy.json(), indent=4))

    assert alias.json()['Meta']['TotalCount'] == noalias.json()[
        'Meta']['TotalCount']

    totalCount = alias.json()['Meta']['PageSize']
    # log.debug(totalCount)

    for i in range(0, totalCount):
        # log.info(noalias.json()['Items'][i])
        # log.info(alias.json()['Items'][i])
        assert noalias.json()['Items'][i] == alias.json()['Items'][i]
