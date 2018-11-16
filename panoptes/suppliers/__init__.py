#! suppliers/__init__.py


import pytest
import requests
from requests import codes
import logging
import json
import uuid
import random
from random import choice
from faker import Faker

fake = Faker()


log = logging.getLogger(__name__)


def createSupplier(configInfo, connections):
    log.info('CREATE THAT SUPPLIER!!')
    admin = connections['admin']

    supplierBody = {
        "ID": "Supplier" + fake.iban(),
        "Name": fake.company(),
        "Active": True,
        "xp": {'faker': True}
    }

    try:
        newSupplier = admin.post(
            configInfo['API'] + 'v1/suppliers', json=supplierBody)
        log.info(newSupplier.status_code)
        log.info(newSupplier.request.body)
        log.info(newSupplier.text)
        assert newSupplier.status_code is codes.created

    except requests.exceptions.RequestException as e:
        log.info(e)

    supplierProfile = admin.get(configInfo[
                                'API'] + 'v1/securityprofiles/assignments', params={'SupplierID': newSupplier.json()['ID']})
    assert supplierProfile.status_code is codes.ok

    if supplierProfile.json()['Meta']['TotalCount'] == 0:
        log.info('assign that supplier a security profile!')
        supplierAssignment = {
            "SecurityProfileID": "fullAccess",
            "SupplierID": newSupplier.json()['ID']
        }
        try:
            supplierProfile = admin.post(
                configInfo['API'] + 'v1/securityprofiles/assignments', json=supplierAssignment)
            log.info(supplierProfile.status_code)
            assert supplierProfile.status_code is codes.created

        except requests.exceptions.RequestException as e:
            log.info(e)

    return newSupplier.json()


def createSupplierUser(configInfo, connections, supplier):

    log.info('CREATE THAT SUPPLIER USER!')

    admin = connections['admin']

    profile = fake.simple_profile()

    userBody = {
        "Username": profile['username'],
        "Password": configInfo['ADMIN-PASSWORD'],
        "FirstName": profile['name'],
        "LastName": profile['name'],
        "Email": profile['username'] + '.' + configInfo['MAILOSAUR-SERVER'] + '@mailosaur.io',
        "Phone": fake.phone_number(),
        "Active": True,
        "xp": {'faker': True}
    }

    try:
        newSupplierUser = admin.post(
            configInfo['API'] + 'v1/suppliers/' + supplier + '/users', json=userBody)
        log.info(newSupplierUser.status_code)
        assert newSupplierUser.status_code is codes.created

    except requests.exceptions.RequestException as e:
        log.info(e)

    return newSupplierUser.json()


def getSupplierUser(configInfo, connections):

    admin = connections['admin']

    try:
        supplierList = admin.get(configInfo['API'] + 'v1/suppliers')
        assert supplierList.status_code is codes.ok
    except requests.exceptions.RequestException as e:
        log.info(e)

    while supplierList.json()['Meta']['TotalCount'] == 0:
        newSupplier = createSupplier(configInfo, connections)
        supplierList = admin.get(configInfo['API'] + 'v1/suppliers')
        assert supplierList.status_code is codes.ok
        log.info(supplierList.json()['Meta']['TotalCount'])

    if supplierList.json()['Meta']['TotalCount'] > 1:
        chosenSupplier = choice(supplierList.json()['Items'])
    else:
        chosenSupplier = supplierList.json()['Items'][0]

    log.info(json.dumps(chosenSupplier, indent=4))

    try:
        supplierUsers = admin.get(
            configInfo['API'] + 'v1/suppliers/' + chosenSupplier['ID'] + '/users')
        assert supplierUsers.status_code is codes.ok
    except requests.exceptions.RequestException as e:
        log.info(e)

    while supplierUsers.json()['Meta']['TotalCount'] == 0:
        newUser = createSupplierUser(
            configInfo, connections, chosenSupplier['ID'])
        supplierUsers = admin.get(
            configInfo['API'] + 'v1/suppliers/' + chosenSupplier['ID'] + '/users')
        assert supplierUsers.status_code is codes.ok
        log.info(supplierUsers.json()['Meta']['TotalCount'])

    if supplierUsers.json()['Meta']['TotalCount'] > 1:
        chosenUser = choice(supplierUsers.json()['Items'])
    else:
        chosenUser = supplierUsers.json()['Items'][0]

    log.info(chosenUser)

    return chosenUser
