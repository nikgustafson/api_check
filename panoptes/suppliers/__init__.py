#! suppliers/__init__.py


import pytest
import requests
from requests import codes
import logging
import json
import uuid
from faker import Faker

fake = Faker()


log = logging.getLogger(__name__)
