#! tests_messageSenders.py


import pytest
import requests
from requests import codes
import logging
import json
from faker import Faker
from random import randint

from .. import me
from .. import auth

from mailosaur import MailosaurClient
from mailosaur.models import SearchCriteria

from requests.auth import HTTPBasicAuth






fake = Faker()
log = logging.getLogger(__name__)


# message senders~~~

def listServers(configInfo):

	user = configInfo['MAILOSAUR-KEY']

	serverlist = requests.get('https://mailosaur.com/api/servers',  auth=(user, ''))
	assert serverlist.status_code is codes.ok
	#log.info(json.dumps(serverlist.json(), indent=4))

	return serverlist.json()

def listEmails(configInfo):

	user = configInfo['MAILOSAUR-KEY']
	server = configInfo['MAILOSAUR-SERVER']

	emailList = requests.get('https://mailosaur.com/api/messages',  auth=(user, ''), params = {'server':server})

	assert emailList.status_code is codes.ok
	#log.debug(json.dumps(emailList.json(), indent=4))

	return emailList.json()

def getEmail(configInfo, emailID):

	user = configInfo['MAILOSAUR-KEY']
	server = configInfo['MAILOSAUR-SERVER']

	gotEmail = requests.get('https://mailosaur.com/api/messages/'+emailID,  auth=(user, ''))

	assert gotEmail.status_code is codes.ok
	#log.debug(json.dumps(gotEmail.json(), indent=4))

	return gotEmail.json()


def deleteEmail(configInfo, emailID):

	user = configInfo['MAILOSAUR-KEY']
	server = configInfo['MAILOSAUR-SERVER']

	delEmail = requests.delete('https://mailosaur.com/api/messages/'+emailID,  auth=(user, ''))

	assert delEmail.status_code is codes.no_content
	#log.info(delEmail)

	return delEmail


def findEmail(configInfo, sentTo = None, subject = None, body = None):

	user = configInfo['MAILOSAUR-KEY']
	server = configInfo['MAILOSAUR-SERVER']

	criteria = {
		'sentTo': sentTo,
		'subject': subject,
		'body': body
	}

	queryMessages = requests.post('https://mailosaur.com/api/messages/search', auth=(user, ''), params = {'server':server}, json=criteria)

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

	queryMessages = requests.post('https://mailosaur.com/api/messages/await', auth=(user, ''), params = {'server':server}, json=criteria)
	#log.debug(queryMessages.text)


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

	newCard = buyer.post(configInfo['API']+'v1/integrationproxy/authorizenet', json = body)
	log.info(newCard.request.url)
	log.info(newCard.status_code)
	#log.info(json.dumps(newCard.json(), indent=4))

	#auth.net needs another body check -- codes will lie

	assert newCard.status_code is codes.created
	assert newCard.json()['ResponseHttpStatusCode'] is codes.ok
	return newCard.json()
	
		