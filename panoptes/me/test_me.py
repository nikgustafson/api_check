#! tests_me.py


import pytest
import requests
import random
from requests import codes
import logging
import json
import jwt
from datetime import datetime
from pytz import timezone, common_timezones_set
import pytz

from faker import Faker


from ..auth import get_Token_UsernamePassword

from . import registerMe, get_Me

fake = Faker()


log = logging.getLogger(__name__)


def deleteMeAddress(configInfo, session, productID):

    delete = session.delete(configInfo['API'] + 'v1/me/addresses/' + productID)
    log.info(delete.status_code)
    # log.info(delete.json())

    assert delete.status_code is codes.no_content


def createMeAddress(configInfo, session):

    newAddress = {
        "Shipping": True,
        "Billing": bool(random.getrandbits(1)),
        "CompanyName": fake.company(),
        "FirstName": fake.first_name(),
        "LastName": fake.last_name(),
        "Street1": fake.street_address(),
        "Street2": fake.secondary_address(),
        "City": fake.city(),
        "State": fake.state_abbr(),
        "Zip": fake.zipcode_plus4(),
        "Country": fake.country_code(),
        "Phone": fake.phone_number(),
        "AddressName": fake.catch_phrase(),
        "xp": {
            'fake': True
        }
    }

    create = session.post(
        configInfo['API'] + 'v1/me/addresses', json=newAddress)
    log.info(create.json())
    assert create.status_code is codes.created


@pytest.mark.smoke
@pytest.mark.perf
@pytest.mark.description(''' Verifies that a buyer user can create a new private address.\n
						In the Smoke Tests, this verifies that the API can write to the database.''')
def test_meAddressesCreate(configInfo):

    client_id = configInfo['BUYER-CLIENTID']
    username = configInfo['BUYER-USERNAME']
    password = configInfo['BUYER-PASSWORD']
    scope = ['Shopper', 'MeAdmin', 'MeAddressAdmin']

    token = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    buyer = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + token['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    buyer.headers.update(headers)

    meGet = buyer.get(configInfo['API'] + 'v1/me')
    assert meGet.status_code is codes.ok
    # log.info(json.dumps(meGet.json(), indent=4))

    addList = buyer.get(configInfo['API'] + 'v1/me/addresses')
    assert addList.status_code is codes.ok

    # log.info(json.dumps(addList.json()))

    totalAdd = addList.json()['Meta']['TotalCount']

    # okay, we've got the initial total of addresses

    newAdd = createMeAddress(configInfo, buyer)

    # now we've created a new address

    addList2 = buyer.get(configInfo['API'] + 'v1/me/addresses')
    assert addList2.status_code is codes.ok

    assert addList2.json()['Meta']['TotalCount'] == totalAdd + 1


@pytest.mark.smoke
@pytest.mark.perf
@pytest.mark.description(''' Verifies that a buyer user can delete a private address.\n
						In the Smoke Tests, this verifies that the API can write deletes to the database.''')
def test_meAddressesDelete(configInfo):

    client_id = configInfo['BUYER-CLIENTID']
    username = configInfo['BUYER-USERNAME']
    password = configInfo['BUYER-PASSWORD']
    scope = ['Shopper', 'MeAdmin', 'MeAddressAdmin']

    token = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    buyer = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + token['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    buyer.headers.update(headers)

    meGet = buyer.get(configInfo['API'] + 'v1/me')
    assert meGet.status_code is codes.ok
    # log.info(json.dumps(meGet.json(), indent=4))

    addList = buyer.get(configInfo['API'] + 'v1/me/addresses')
    assert addList.status_code is codes.ok

    # log.info(json.dumps(addList.json()))

    totalAdd = addList.json()['Meta']['TotalCount']

    if totalAdd == 0:
        newAdd = createMeAddress(configInfo, buyer)
        totalAdd = totalAdd + 1

    deletedAdd = addList.json()['Items'][0]['ID']
    log.info('Deleted Address ID: ' + deletedAdd)

    deleteMeAddress(configInfo, buyer, deletedAdd)

    addList2 = buyer.get(configInfo['API'] + 'v1/me/addresses')
    assert addList2.status_code is codes.ok

    assert addList2.json()['Meta']['TotalCount'] == totalAdd - 1


@pytest.mark.smoke
@pytest.mark.description(''' Verifies that an anon user can register.''')
def test_meRegistration(configInfo, connections):

    anonToken = connections['anon']

    # register the anon user as a new user
    newUserToken = registerMe(configInfo, anonToken)
    log.info(json.dumps(newUserToken, indent=4))
    jwtHeaders = jwt.get_unverified_header(newUserToken['access_token'])

    decoded = jwt.decode(newUserToken['access_token'], verify=False)

    #log.info('America/Chicago' in common_timezones_set)

    loc_tz = pytz.timezone('America/Chicago')

    log.info('--------')
    log.info('today\'s date is:')
    c_dt = loc_tz.localize(datetime.today(), is_dst=False)
    log.info(c_dt)
    # log.info(loc_dt)
    log.info('--------')
    # log.info(decoded['nbf'])
    # log.info(decoded['exp'])

    # log.info(common_timezones_set)

    notbefore = loc_tz.localize(datetime.utcfromtimestamp(
        decoded['nbf']), is_dst=False)
    expiration = loc_tz.localize(datetime.utcfromtimestamp(
        decoded['exp']), is_dst=False)

    log.info('Registered User\'s NBF: ' + str(notbefore))
    log.info('Registered User\'sEXP: ' + str(expiration))

    user = get_Me(configInfo, newUserToken)
    #log.info(json.dumps(user, indent=4))


@pytest.mark.smoke
@pytest.mark.perf
@pytest.mark.description('Tests all Me list endpoints.')
#@pytest.mark.parametrize("sessions", ['buyer', 'anon'])
@pytest.mark.parametrize("sessions", ['buyer'])
@pytest.mark.parametrize("endpoint", [
    "",
    "products",
    "costcenters",
    "usergroups",
    "addresses",
    "creditcards",
    "categories",
    "orders",
    "promotions",
    "spendingAccounts",
    "shipments",
    "catalogs"

])
def test_me_gets(configInfo, connections, sessions, endpoint):

    session = connections[sessions]

    collection = session.get(configInfo['API'] + 'v1/me/' + endpoint)
    log.info(collection.url)
    # log.info(collection.status_code)

    log.info(repr(collection.elapsed.total_seconds()) + ' seconds elapsed.')
    # log.debug(collection.json())
    if 'Meta' in collection.json().keys():
        log.debug(collection.json()['Meta']['TotalCount'])

    assert collection.status_code is codes.ok


@pytest.mark.smoke
@pytest.mark.perf
@pytest.mark.description('Verifies Facet Navigation appears on me/Products.')
@pytest.mark.parametrize("sessions", ['buyer', 'anon'])
def test_me_facets(configInfo, connections, sessions):

    session = connections[sessions]

    facets = session.get(configInfo['API'] + 'v1/me/products')
    log.info(facets.url)
    # log.info(facets.status_code)
    log.info(repr(facets.elapsed.seconds) + ' seconds OR ' +
             repr(facets.elapsed.microseconds) + ' microseconds')
    #log.debug(json.dumps(facets.json()['Meta'], indent=4))

    if 'Facets' in facets.json()['Meta'].keys():
        assert facets.json()['Meta']['Facets'] is not None
        log.debug(json.dumps(facets.json()['Meta']['Facets'], indent=4))
