#! tests_me.py


import pytest
import requests
from requests import codes
import logging
import json
import uuid

from faker import Faker

fake = Faker()


log = logging.getLogger(__name__)


def get_Me(configInfo, session):

    try:
        me = session.get(configInfo['API'] + 'v1/me')
        log.info(me.text)
        log.info(me.status_code)
        log.info(me.url)
        assert me.status_code is codes.ok
    except:
        raise

    return me.json()


def patch_Me(configInfo, token, newUser):

    headers = {
        'Authorization': 'Bearer ' + token['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    payload = newUser

    me = requests.patch(configInfo['API'] + 'v1/me',
                        json=newUser, headers=headers)

    # log.debug(me.request.headers)
    log.debug(me.request.url)
    # log.debug(json.dumps(me.json(), indent=2))
    log.debug(me.status_code)
    assert me.status_code is codes.ok

    return me.json()


def getMeProducts(configInfo, session, params):

    products = session.get(configInfo['API'] + 'v1/me/products', params=params)
    log.info(products.request.url)
    log.info(products.status_code)
    # log.info(delete.json())

    assert products.status_code is codes.ok

    # log.info(json.dumps(orders.json(), indent=4))

    return products.json()


def get_meProducts(configInfo, token, params):

    if type(token) is dict:
        token = token['access_token']

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    try:
        products = requests.get(
            configInfo['API'] + 'v1/me/products', headers=headers, params=params)

        # log.debug(me.request.headers)
        log.debug(products.request.url)
        log.debug(json.dumps(products.json(), indent=2))
        log.debug(products.status_code)
        assert products.status_code is codes.ok
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    return products.json()


def getMeOrders(configInfo, session):

    orders = session.get(configInfo['API'] + 'v1/me/orders/')
    log.info(orders.request.url)
    log.info(orders.status_code)
    # log.info(delete.json())

    assert orders.status_code is codes.ok

    # log.info(json.dumps(orders.json(), indent=4))

    return orders


def registerMe(configInfo, session):

    profile = fake.profile()
    # log.info(profile)

    newUser = {
        "Username": profile['username'] + str(uuid.uuid4()),
        "Password": profile['ssn'],
        "FirstName": fake.first_name(),
        "LastName": fake.last_name(),
        "Email": profile['username'] + '@.' + configInfo['MAILOSAUR-SERVER'] + '@mailosaur.io',
        "Phone": fake.phone_number(),
        "Active": True,
        "xp": {'genFake': True}
    }

    #?anonUserToken={{anonUserToken}}
    if type(session) is dict:
        # log.info(session)
        token = session['access_token']
        # log.info(token)

        user = requests.put(configInfo['API'] + 'v1/me/register',
                            json=newUser, params={'anonUserToken': token})
       # log.info(user.url)
       # log.info(user.status_code)
       # log.info(user.json())
        assert user.status_code is codes.ok
        return user.json()

    else:
       # log.info(session.headers)

        token = session.headers['Authorization']
      #  log.info(token)
        token = token[7:]
       # log.info(token)

        user = session.put(configInfo['API'] + 'v1/me/register',
                           json=newUser, params={'anonUserToken': token})
        assert user.status_code is codes.ok
        return user.json()
