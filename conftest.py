import pytest
import configparser

def pytest_addoption(parser):
	parser.addoption("--ENV", action="store", help="Choose the API Environment to run against: QA or PROD", default="QA")

@pytest.fixture()
def apiEnv(pytestconfig):

	return pytestconfig.option.ENV 

@pytest.fixture()
def configInfo(apiEnv):

	config = configparser.ConfigParser()
	config.read('config.ini') # local config file
	configData = config['QA-CONFIG']

	if str.lower(apiEnv) == 'prod':
		configData = config['PROD-CONFIG']
		return configData 
	else:
		return configData