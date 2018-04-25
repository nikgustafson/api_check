"""Define some fixtures to use in the project."""


import pytest
import configparser
import logging
from collections import namedtuple

@pytest.fixture(scope='session')
def setEnv(env=''):

	hosts = namedtuple('Hosts', ['apiHost', 'authHost', 'integrationHost'])

	hosts.apiHost = 'https://'+env+'api.ordercloud.io'
	hosts.authHost = 'https://'+env+'auth.ordercloud.io'
	hosts.integrationHost = hosts.apiHost+'/v1/integrationproxy/'

	return(hosts)


@pytest.fixture(autouse=True, scope='session')
def initLogging():
	logging.basicConfig(filename='../logs/testRun.log', level=logging.DEBUG, filemode = 'w')

@pytest.fixture(autouse=True, scope='session')
def getConfig():
	config = configparser.ConfigParser()
	config.read('../config.ini')
	auth = config['LOCUST-AUTH']

	return(auth)

@pytest.fixture(scope='function')
def user_dict():
	newUserID = fake.ean8()

	user = {
	  'ID' : newUserID,
	  'Username' : fake.user_name(),
	  'FirstName' : fake.first_name(),
	  'LastName' : fake.last_name(),
	  'Password': fake.password(),
	  'Email' : newUserID+'@ordercloud-qa.mailinator.com',
	  'Phone' : fake.phone_number(),
	  'TermsAccepted':datetime.utcnow().strftime('%Y/%m/%d'),
	  'Active' : 'True',
	  'xp' : {}
	}

	return(user)