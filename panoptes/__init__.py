# panoptes globals
import logging
import configparser
from pathlib import Path
from faker import Faker
import datetime
from datetime import *
import json
import os


fake = Faker()


## Logging

# create logger with 'spam_application'
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('../logs/'+__name__+'.log')


## common api info

cwd = Path.cwd()
print(cwd)

file = os.path.dirname(os.path.realpath('__file__'))
print(file)

environments = {'api':['api', 'qaapi'], 'auth':['auth', 'qaauth']}

env = ''
host = 'https://'+env+'api.ordercloud.io'
authhost = 'https://'+env+'auth.ordercloud.io'
authnet = host+'/v1/integrationproxy/authorizenet'

config = configparser.ConfigParser()


confPath = Path('../config.ini') ## gotta make this a relative path compare
config.read(confPath)
auth = config['LOCUST-AUTH']


# models



def createCreditCardObj():
    """
    creates a dict object with fully random credit card info

    """    
    cardNumber = fake.credit_card_number(card_type=None)

    cc = {
            "CardholderName": fake.name(),
            "CardType": fake.credit_card_provider(card_type=None),
            "CardNumber": cardNumber,
            "ExpirationDate": fake.credit_card_expire(start="now", end="+10y", date_format="%Y/%m/%d"),
            "CardCode": cardNumber[-4:],
            "Shared": False
        }

    return cc
    

def createUserObj():
    """
    creates a dict object with fully random user info
    
    """

    newUserID = fake.ean8()

    user = {
        'ID' : newUserID,
        'Username' : fake.user_name(),
        'FirstName' : fake.first_name(),
        'LastName' : fake.last_name(),
        'Password': fake.password(),
        'Email' : newUserID+'@ordercloud-qa.mailinator.com',
        'Phone' : fake.phone_number(),
        'TermsAccepted':datetime.utcnow().strftime('%Y/%m/%d'),
        'Active' : 'True',
        'xp' : {}
    }


 
 


