#! users/__init__.py


import pytest
import requests
from requests import codes
import logging
import json

from faker import Faker

fake = Faker()


log = logging.getLogger(__name__)


def createUser(configInfo, session):

    profile = fake.profile()
    # log.info(profile)

    newUser = {
        "Username": profile['username'],
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
