#! tests_messageSenders.py


import pytest
import requests
from requests import codes
import logging
import json
from faker import Faker
from random import randint
import pytz
import jwt
from datetime import datetime

from .. import me
from .. import auth

from mailosaur import MailosaurClient
from mailosaur.models import SearchCriteria

from requests.auth import HTTPBasicAuth


fake = Faker()
log = logging.getLogger(__name__)
loc_tz = pytz.timezone('America/Chicago')


# message senders~~~

def resetEmail(configInfo, connections, user):

    if configInfo['MAILOSAUR-SERVER'] not in user['Email']:

        newEmail = {'Email': user['Username'] + '.' +
                    configInfo['MAILOSAUR-SERVER'] + '@mailosaur.io'}
        log.info(newEmail)

        patchedUser = connections['admin'].patch(
            configInfo['API'] + 'v1/buyers/' + configInfo['Buyer'] + '/users/' + user['ID'], json={'Email': newEmail['Email']})
        log.info(patchedUser.url)
        log.info(json.dumps(patchedUser.json(), indent=4))

        assert patchedUser.status_code is codes.ok

        userEmail = patchedUser.json()['Email']

        return userEmail


def listServers(configInfo):

    user = configInfo['MAILOSAUR-KEY']

    serverlist = requests.get(
        'https://mailosaur.com/api/servers',  auth=(user, ''))
    assert serverlist.status_code is codes.ok
    #log.info(json.dumps(serverlist.json(), indent=4))

    return serverlist.json()


def listEmails(configInfo):

    user = configInfo['MAILOSAUR-KEY']
    server = configInfo['MAILOSAUR-SERVER']

    emailList = requests.get(
        'https://mailosaur.com/api/messages',  auth=(user, ''), params={'server': server})

    assert emailList.status_code is codes.ok
    #log.debug(json.dumps(emailList.json(), indent=4))

    return emailList.json()


def getEmail(configInfo, emailID):

    user = configInfo['MAILOSAUR-KEY']
    server = configInfo['MAILOSAUR-SERVER']

    gotEmail = requests.get(
        'https://mailosaur.com/api/messages/' + emailID,  auth=(user, ''))

    assert gotEmail.status_code is codes.ok
    #log.debug(json.dumps(gotEmail.json(), indent=4))

    return gotEmail.json()


def deleteEmail(configInfo, emailID):

    user = configInfo['MAILOSAUR-KEY']
    server = configInfo['MAILOSAUR-SERVER']

    delEmail = requests.delete(
        'https://mailosaur.com/api/messages/' + emailID,  auth=(user, ''))

    assert delEmail.status_code is codes.no_content
    # log.info(delEmail)

    return delEmail


def findEmail(configInfo, sentTo=None, subject=None, body=None):

    user = configInfo['MAILOSAUR-KEY']
    server = configInfo['MAILOSAUR-SERVER']

    criteria = {
        'sentTo': sentTo,
        'subject': subject,
        'body': body
    }

    queryMessages = requests.post('https://mailosaur.com/api/messages/search',
                                  auth=(user, ''), params={'server': server}, json=criteria)

    assert queryMessages.status_code is codes.ok

    #log.debug(json.dumps(queryMessages.json(), indent=4))

    return(queryMessages.json())

    #client.messages.search(configInfo('MAILOSAUR-SERVER'), criteria)


def awaitEmail(configInfo, sentTo, subject, body):

    user = configInfo['MAILOSAUR-KEY']
    server = configInfo['MAILOSAUR-SERVER']

    criteria = {
        'sentTo': sentTo,
        'subject': subject,
        'body': body
    }

    queryMessages = requests.post('https://mailosaur.com/api/messages/await',
                                  auth=(user, ''), params={'server': server}, json=criteria)
    # log.debug(queryMessages.text)

    assert queryMessages.status_code in (codes.ok, codes.no_content)

    if queryMessages.status_code is codes.no_content:
        return(queryMessages.status_code)
    else:
        #log.info(json.dumps(queryMessages.json(), indent=4))
        return(queryMessages.json())


# auth.net

def createCreditCard(configInfo, body, token):

    buyer = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + token['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    buyer.headers.update(headers)

    decoded = jwt.decode(buyer.headers['Authorization'][7:], verify=False)
    log.info('--------')
    log.info('today\'s date is:')
    c_dt = loc_tz.localize(datetime.today(), is_dst=False)
    log.info(c_dt)
    log.info('--------')

    notbefore = loc_tz.localize(datetime.utcfromtimestamp(
        decoded['nbf']), is_dst=False)
    expiration = loc_tz.localize(datetime.utcfromtimestamp(
        decoded['exp']), is_dst=False)
    log.info('--------')
    log.info('Card User\'s NBF: ' + str(notbefore))
    log.info('Card User\'s EXP: ' + str(expiration))
    log.info('--------')

    newCard = buyer.post(
        configInfo['API'] + 'v1/integrationproxy/authorizenet', json=body)
    log.info(newCard.request.url)
    log.info(newCard.status_code)

    log.info('NEW CARD')
    log.info(newCard.text)
    log.info(json.dumps(newCard.json(), indent=4))

    # auth.net needs another body check -- codes will lie

    assert newCard.status_code is codes.created
    assert newCard.json()['ResponseHttpStatusCode'] is codes.ok
    return newCard.json()
