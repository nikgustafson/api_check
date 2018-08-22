import pytest 
import logging

log = logging.getLogger(__name__)

def getConfigData(configInfo):

	log.info('API: '+ repr(configInfo['API']))
	log.info('AUTH: '+ repr(configInfo['AUTH']))

	if 'qa' in configInfo['API']:
		print('api environment is QA!')
		return('QA')
	else:
		print('api env is prod!!')
		return('PROD')