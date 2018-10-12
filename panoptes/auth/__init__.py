
import pytest
import requests
from requests import codes
import logging
import json
from faker import Faker

from .. import me


fake = Faker()


log = logging.getLogger(__name__)


def get_anon_user_token(configInfo, client_id):

    anon_token = get_Token_ClientID(configInfo, client_id, scope=['Shopper'])

    log.info(anon_token)
    return anon_token


def get_Token_ClientID(configInfo, client_id, scope=[]):

    scopes = ' '.join(scope)

    payload = {
        'client_id': client_id,
        'grant_type': 'client_credentials',
        'Scope': scopes
    }
    log.debug(payload)

    headers = {'Content-Type': 'text/html'}

    token = requests.post(
        configInfo['AUTH'] + 'oauth/token', data=payload, headers=headers)
    log.debug(token.request.headers)
    log.debug(token.request.body)
    log.debug(json.dumps(token.json(), indent=2))
    assert token.status_code is codes.ok

    return token.json()


def get_Token_UsernamePassword(configInfo, client_id, username, password, scope=[]):
    """


    """

    scopes = ' '.join(scope)

    payload = {
        'client_id': client_id,
        'grant_type': 'password',
        'username': username,
        'password': password,
        'Scope': scopes
    }
    log.debug(payload)

    headers = {'Content-Type': 'text/html'}

    token = requests.post(
        configInfo['AUTH'] + 'oauth/token', data=payload, headers=headers)
    # log.debug(token.request.headers)
    # log.debug(token.request.body)
    log.debug(json.dumps(token.json(), indent=2))
    assert token.status_code is codes.ok

    return token.json()


def post_resetPassword(configInfo, token, resetUrl):
    """
    Sends a temporary verification code via email, which must subsequently be passed in a Reset Password call.
    """

    user = me.get_Me(configInfo, token)
    # log.debug(user)

    payload = {
        'ClientID': configInfo['BUYER-CLIENTID'],
        'Email': user['Email'],
        'username': user['Username'],
        'URL': resetUrl
    }
    log.debug(json.dumps(payload, indent=2))

    headers = {
        'Content-Type': 'application/json',
        'Autentication': 'Bearer ' + token['access_token']}

    log.debug(headers)

    reset = requests.post(
        configInfo['API'] + 'v1/password/reset', json=payload, headers=headers)
    log.debug(reset)
    assert reset.status_code is codes.no_content
