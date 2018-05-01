# authentication to api and verification that it's up
import requests
from requests import codes
import pytest
import logging
from . import check_env
from .. import environments


def test_apiEnvEndpoint():
	logger = logging.getLogger(__name__)
	for key in environments.keys():
		for env in environments[key]:
			logger.debug(env)
			assert check_env(env).status_code == 200
			assert check_env(env).is_redirect is False




