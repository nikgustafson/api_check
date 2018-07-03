#! tests_base.py

import pytest
import requests
import logging



log = logging.getLogger(__name__)


def test_fixtures_for_options(apiEnv):

	log.info('api environment set to: '+str(apiEnv))

def test_configData(configInfo):

	log.info('API: '+ configInfo['API'])
	log.info('AUTH: '+ configInfo['AUTH'])

