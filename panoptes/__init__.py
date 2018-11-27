import pytest
import logging
import requests
from faker import Faker
import json

fake = Faker()

from .auth import get_Token_UsernamePassword

log = logging.getLogger(__name__)


def getConfigData(configInfo):

    log.info('API: ' + repr(configInfo['API']))
    log.info('AUTH: ' + repr(configInfo['AUTH']))

    if 'qa' in configInfo['API']:
        log.info('api environment is QA!')
        return('QA')
    else:
        log.info('api env is prod!!')
        return('PROD')


@pytest.fixture(scope='module')
def buyer_setup(request, configInfo):
    log.info('setting up a new buyer...')
    buyerName = fake.company()
    log.info(buyerName)

    incrementors = configInfo[1].get(
        configInfo[0]['API'] + 'v1/incrementors')
    #log.info(json.dumps(incrementors.json(), indent=4))

    if incrementors.json()['Meta']['TotalCount'] == 0:
        createIncrementors()
        incrementors = configInfo[1].get(
            configInfo[0]['API'] + 'v1/incrementors')

    else:
        assert incrementors.json()['Meta']['TotalCount'] == 3

    buyerBody = {
        "ID": 'Buyer{buyer-incrementor}',
        "Name": buyerName,
        "Active": True,
        "xp": {
            'faker': True
        }
    }
    log.info(json.dumps(buyerBody, indent=4))

    filters = {
        'AllowAnyBuyer': True,
        'IsAnonBuyer': True
    }

    apiClients = configInfo[1].get(
        configInfo[0]['API'] + 'v1/apiclients', params=filters)
    #log.info(json.dumps(apiClients.json(), indent=4))

    newBuyer = configInfo[1].post(
        configInfo[0]['API'] + 'v1/buyers', json=buyerBody)
    log.info(json.dumps(newBuyer.json(), indent=4))

    def buyer_teardown():
        log.info('tearing down the ' + buyerName + ' buyer...')

    request.addfinalizer(buyer_teardown)


def teardown_module(module):
    log.info('teardown_module()')


def test_1(buyer_setup):
    log.info('-  test_1()')


def test_2(buyer_setup):
    log.info('-  test_2()')
