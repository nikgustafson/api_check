import pytest
import logging
import requests
from requests import codes
from faker import Faker
import random
import json


fake = Faker()

from .auth import get_Token_UsernamePassword
from .products import get_Products, createProducts

log = logging.getLogger(__name__)


def getConfigData(configInfo):

    log.info('API: ' + repr(configInfo['API']))
    log.info('AUTH: ' + repr(configInfo['AUTH']))

    if 'qa' in configInfo['API']:
        log.info('api environment is QA!')
        return('QA')
    else:
        log.info('api env is prod!!')
        return('PROD')
