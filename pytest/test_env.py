# test that the api env is up
import requests
import pytest

environments = {'api':['api', 'qaapi'], 'auth':['auth', 'qaauth']}

def check_env(input):
#"Environment":"prod","Version":"1.0.73.889","Branch":"default","Commit":"ed55689508097909378cc244f5d020a3312d112d","CommitDate":"2018-03-21T22:18:13+00:00","BuildDate":"2018-03-21T16:05:51+00:00	
	d = requests.get('https://'+input+'.ordercloud.io/env')

	return(d)

def check_GetMe(input):
	d = requests.get('https://'+input+'.ordercloud.io/v1/me')
	return(d)


def test_env():
	for key in environments.keys():
		for env in environments[key]:
			assert check_env(env).status_code == 200
			assert check_env(env).is_redirect is False


def test_endpointAccessShouldFailWithoutAuth():
	for env in environments['api']:
		assert check_GetMe(env).status_code == 401
		assert check_GetMe(env).is_redirect is False
	

