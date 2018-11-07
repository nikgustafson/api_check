#! tests_me.py


import pytest
import requests
from requests import codes
import logging
import json
import urllib.parse


log = logging.getLogger(__name__)


def test_xpDateFilter(configInfo, connections):

    admin = connections['admin']

    filters = {
        'pageSize': 100
    }
    productList = admin.get(configInfo['API'] + 'v1/products', params=filters)
    log.info(json.dumps(productList.json()))
