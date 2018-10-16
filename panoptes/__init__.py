import pytest
import logging

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

    return {
        'admin': admin,
        'buyer': buyer
    }
