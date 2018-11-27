import pytest
import logging
import requests

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


@pytest.fixture(scope='session', autouse=True)
def connections(configInfo):

    client_id = configInfo['SELLER-API-CLIENT']
    username = configInfo['SELLER-ADMIN-USERNAME']
    password = configInfo['SELLER-ADMIN-PASSWORD']
    scope = ['FullAccess']

    # can successfully get a token
    adminToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    admin = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + adminToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    admin.headers.update(headers)

    return {
        'admin': admin
    }


def setup_module(module):
    log.info('\nsetup_module()')


def teardown_module(module):
    log.info('teardown_module()')


def setup_function(function):
    log.info('\nsetup_function()')


def teardown_function(function):
    log.info('\nteardown_function()')


def test_1():
    log.info('-  test_1()')


def test_2():
    log.info('-  test_2()')
