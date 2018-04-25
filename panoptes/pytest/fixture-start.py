#authentication
import requests
from requests import codes as codes
import pytest
import configparser
import json
import logging
import datetime
import urllib
from random import randint
from faker import Faker
fake = Faker()

@pytest.mark.usefixtures('setEnv')
class TestAuth():

	def test_fix():
		print("we did it!")
		

