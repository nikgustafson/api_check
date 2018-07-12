#! tests_messageSenders.py


import pytest
import requests
from requests import codes
import logging
import json
from faker import Faker
from random import randint

import test_me
import test_auth

from mailosaur import MailosaurClient
from mailosaur.models import SearchCriteria






fake = Faker()
log = logging.getLogger(__name__)


def findEmail(configInfo, sentTo = 0, subject = 0, body = 0):

	client = MailosaurClient(configInfo('MAILOSAUR-KEY'))

	criteria = SearchCriteria()

	if sentTo is not 0:
		criteria.sent_to = sentTo
	if subject is not 0:
		criteria.subject = sentTo
	if body is not 0:
		criteria.body = body

	
	client.messages.search(configInfo('MAILOSAUR-SERVER'), criteria)





"""
variation: user types
	- anon buyer user who does not register
	- anon buyer user who does register (after order create)
	- previously registered buyer user
	- registered admin user in buyer app
"""
@pytest.mark.description("Verifies that the ForgottenPassword message sender successfully sends an email when triggered. NOTE: this message sender is only triggered by the '/v1/password/reset' endpoint.")
def test_ForgottenPassword(configInfo):

	"""
	verifies that Forgotten Password (Password Reset) emails are sent and recieved for Ordercloud application users.
	"""


	client_id = configInfo['BUYER-CLIENTID']
	username = configInfo['BUYER-USERNAME']
	password = configInfo['BUYER-PASSWORD']
	scope = ['Shopper', 'MeAdmin']



	# auth as buyer user
	token = test_auth.get_Token_UsernamePassword(configInfo, client_id, username, password, scope)

	resetUrl = fake.url()

	user = test_me.get_Me(configInfo, token['access_token'])
	userEmail = user['Email']

	# make sure the user has the right email server
	if configInfo['MAILOSAUR-SERVER'] not in userEmail:

		newEmail = { 'Email': user['Username']+'.'+configInfo['MAILOSAUR-SERVER']+'@mailosaur.io' }
		log.debug(newEmail)

		user = test_me.patch_Me(configInfo, token, newUser = newEmail)
		log.debug(user)

	# reset that password!
	resetcall = test_auth.post_resetPassword(configInfo, token, resetUrl)

	# get that email







	
	pwEmailSubject = 'Here is the link to reset your password'
	# logger.info(pwEmailSubject)

   # logger.debug = "checking email for " + pwEmailSubject
   # results = findEmail(newUser.email, pwEmailSubject)

@pytest.mark.description(
	"Verifies that the OrderSubmitted message sender is working. \
	Test registers an Anon User, creates an order with lineitem, and submits the order. After order submit, test verifies that an OrderSubmitted email was recieved by the order submitting user.")
def test_OrderSubmitted():
	"""
	verifies that Order Submit emails are being sent for the following types of users:
		1. Anon Users who do not register during checkout
		2. Anon Users who register during checkout process (after order is created)
		3. Previously registered buyer users 
	returns: nothing
	"""

	pass

def test_ShipmentCreated():

	"""
	emails should be sent for Ordercloud application users.
	returns: nothing
	"""
	pass


@pytest.mark.description("Verifies that User who submitted an order for approval recieves OrderApproved message sender email.\
	CURRENTLY A STUB.")
def test_OrderApproved():

	"""
	emails should be sent for Ordercloud application users.
	returns: nothing
	"""
	pass
@pytest.mark.description("Verifies that User who submitted an order for approval recieves OrderDeclined message sender email.\
	CURRENTLY A STUB.")
def test_OrderDeclined():

	"""
	emails should be sent for Ordercloud application users.
	returns: nothing
	"""
	pass

@pytest.mark.description("Verifies that User who submitted an order for approval recieves OrderSubmittedForApproval message sender email.\
	CURRENTLY A STUB.")
def test_OrderSubmittedForApproval():

	"""
	emails should be sent for Ordercloud application users.
	returns: nothing
	"""
	pass

def test_OrderSubmittedForYourApprovalHasBeenApproved():

	"""
	emails should be sent for Ordercloud application users.
	returns: nothing
	"""
	pass

def test_OrderSubmittedForYourApprovalHasBeenDeclined():

	"""
	emails should be sent for Ordercloud application users.
	returns: nothing
	"""
	pass