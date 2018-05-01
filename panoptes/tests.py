# tests for the tests god!!! unit tests for the test throne!!
from . import createCreditCardObj, createUserObj
import logging
import json

logging.basicConfig(filename='../logs/example.log',level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_createCard():

    cc = createCreditCardObj()

    logger.debug(json.dumps(cc, indent=2))


def test_createUser():

    u = createUserObj()

    logger.debug(json.dumps(u, indent=2))    

    