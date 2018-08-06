#! tests_messageSenders.py


import pytest
import requests
from requests import codes
import logging
import json
from faker import Faker
from random import randint

import me
import auth

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



