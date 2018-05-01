# filter user workflow tests
import requests
from requests import codes
import pytest
import configparser
import json
import logging
import datetime
import urllib
from random import randint
from faker import Faker


from panoptes import host, auth
from ..authentication import getTokenPasswordGrant, registerUser

from . import fake, getMeProducts, getMe

# TODO: make user set up and tear down a test fixture

def setUp():

    user = registerUser()
    return user


# 1
def test_MeGet():
    #logger = logging.getLogger(test_MeGet.__name__)
    # get me succeeds, and user is active


    token = setUp['access_token']
    user = getMe(token)
    #assert user['Username'] == auth['buyerUsername']
    assert user['Active'] == True



# 2
def test_MeProduct():


    token = getTokenPasswordGrant(auth['buyerUsername'], auth['buyerPassword'], 'Shopper')
    productList = getMeProducts(token)

    assert productList.status_code == 200
    assert productList.is_redirect is False

    assert productList.json()['Meta']['TotalCount'] > 5
    randProduct = productList.json()['Items'][randint(0, productList.json()['Meta']['PageSize'] - 1)]
    product = getMeProducts(token, productID=randProduct['ID'])
    
    print(product)
    print(productList)



#logger.info("Product List: "+str(productList))


searchParams = (["catalogID", "smokebuyer01"], ["search", "*w*"], ["sortBy", "name"], ["page", 5], ["pageSize", 100])
# filterParams =

ids = []

for item in searchParams:
    ids.append(item[0] + '-' + str(item[1]))


#@pytest.mark.parametrize("searchParams", searchParams, ids=ids, )
# 3
def test_MeProductFilter(searchParams):


    allProducts = getMeProducts(auth['buyerUsername'], auth['buyerPassword'])
   
    assert allProducts.status_code == 200
    totalProducts = allProducts.json()['Meta']['TotalCount']
    totalPages = allProducts.json()['Meta']['TotalPages']

    filters = {searchParams[0]: str(searchParams[1])}
    print(filters)

    filterProducts = getMeProducts(auth['buyerUsername'], auth['buyerPassword'], filters)
    assert allProducts.status_code == 200
    assert filterProducts.url == (
                host+'/v1/me/products?' + str(searchParams[0]) + '=' + urllib.parse.quote_plus(
            str(searchParams[1])))
    filterProducts = allProducts.json()['Meta']['TotalCount']
    filterPages = allProducts.json()['Meta']['TotalPages']
 

# what we want: 'catalogID','search',"sortBy","page","pageSize" x filters

