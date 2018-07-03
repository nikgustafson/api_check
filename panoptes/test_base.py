#! tests_base.py

import pytest
import requests


@pytest.fixture()
def apiEnv(pytestconfig):
	return pytest.option.ENV 

def test_fixtures_for_options(apiEnv):
	print('api environment set to: ', apiEnv)

