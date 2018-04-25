# pytest globals
import logging
import configparser
from pathlib import Path

__all__ = ["environments", "get_logger", "host", "authhost", "auth"]

## common api info

environments = {'api':['api', 'qaapi'], 'auth':['auth', 'qaauth']}

env = ''
host = 'https://'+env+'api.ordercloud.io'
authhost = 'https://'+env+'auth.ordercloud.io'

config = configparser.ConfigParser()
confPath = Path('../../config.ini')
config.read(confPath)
auth = config['LOCUST-AUTH']


## Logging

logging.basicConfig(filename='../../logs/testRun.log', level=logging.DEBUG, filemode = 'w')

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

''' this is kind of useless rn -- with pytest, __name__ is overwritten
def get_logger():
	logger = logging.getLogger(__name__)

	return(logger)
'''




