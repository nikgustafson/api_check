import pytest 
import logging

log = logging.getLogger(__name__)

def getConfigData(configInfo):

	log.info('API: '+ repr(configInfo['API']))
	log.info('AUTH: '+ repr(configInfo['AUTH']))

	if 'qa' in configInfo['API']:
		log.info('api environment is QA!')
		return('QA')
	else:
		log.info('api env is prod!!')
		return('PROD')