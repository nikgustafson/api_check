#! users/__init__.py


import pytest
import requests
from requests import codes
import logging
import json
import uuid
from faker import Faker

fake = Faker()


log = logging.getLogger(__name__)


def createUser(configInfo, session):

    profile = fake.profile()
    # log.info(profile)

    newUser = {
        "ID": str(uuid.uuid4()),
        "Username": profile['username'] + '-' + str(uuid.uuid4()),
        "Password": profile['ssn'],
        "FirstName": fake.first_name(),
        "LastName": fake.last_name(),
        "Email": profile['username'] + '@.' + configInfo['MAILOSAUR-SERVER'] + '@mailosaur.io',
        "Phone": fake.phone_number(),
        "Active": True,
        "xp": {'genFake': True}
    }

    create = session.post(
        configInfo['API'] + 'v1/buyers/' + configInfo['Buyer'] + '/users/', json=newUser)
    log.info(create.url)
    log.info(create.status_code)
    log.info(create.text)
    assert create.status_code is codes.created

    return create.json()


def assignProducts(configInfo, session, users, PriceScheduleID=None, BuyerID=None, UserGroupID=None):
    log.info('Let\'s Assign Some USERS!')

    if type(products[0]) is dict:
        False

    log.info('assign product to catalog')
    for product in products:
        body = {
            "CatalogID": BuyerID,
            "ProductID": product
        }

        try:
            assignCat = session.post(
                configInfo['API'] + 'v1/catalogs/productassignments', json=body)
            log.info(assignCat.status_code)
           # log.info(assignCat.request.body)
           # log.info(assignCat.text)
            assert assignCat.status_code in [
                codes.created, codes.no_content, codes.ok, '204']

        except requests.exceptions.RequestException as e:
            log.info(e)

    log.info('assign product to ITEM')
    for product in products:
        log.info(product)

        body = {
            "ProductID": product,
            "BuyerID": BuyerID,
            "UserGroupID": UserGroupID,
            "PriceScheduleID": PriceScheduleID
        }

        try:
            assignment = session.post(
                configInfo['API'] + 'v1/products/assignments', json=body)
            log.info(assignment.status_code)
            # log.info(assignment.request.body)
            # log.info(assignment.text)
            assert assignment.status_code in [
                codes.created, codes.no_content, codes.ok, '204']

        except requests.exceptions.RequestException as e:
            log.info(e)

    return True
