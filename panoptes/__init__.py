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


@pytest.fixture(scope='module')
def buyer_setup(request, configInfo, connections):
    admin = connections['admin']
    log.info('setting up a new buyer...')
    buyerName = fake.company()

    log.info(buyerName)

    buyerSession = {
        'clientID': '',
        'session': '',
        'buyerID': '',
        'buyerName': buyerName,
        'username': '',
        'userID': '',
        'password': ''

    }

    # make sure an incrementor exists for buyer
    incrementors = admin.get(
        configInfo['API'] + 'v1/incrementors')
    # log.info(json.dumps(incrementors.json(), indent=4))

    if incrementors.json()['Meta']['TotalCount'] == 0:
        createIncrementors()
        incrementors = admin.get(
            configInfo['API'] + 'v1/incrementors')

    else:
        assert incrementors.json()['Meta']['TotalCount'] == 3

    buyerBody = {
        "ID": 'Buyer{buyer-incrementor}',
        "Name": buyerName,
        "Active": True,
        "xp": {
            'faker': True
        }
    }
    log.debug(json.dumps(buyerBody, indent=4))

    # verify that an api client exists that accepts buyers
    filters = {
        'AllowAnyBuyer': True,
        'IsAnonBuyer': True
    }

    apiClients = admin.get(
        configInfo['API'] + 'v1/apiclients', params=filters)
    # log.info(json.dumps(apiClients.json(), indent=4))
    assert apiClients.json()['Meta']['TotalCount'] >= 1
    buyerSession['clientID'] = apiClients.json()['Items'][0]['ID']

    # create new buyer
    newBuyer = admin.post(
        configInfo['API'] + 'v1/buyers', json=buyerBody)
    log.debug(json.dumps(newBuyer.json(), indent=4))
    assert newBuyer.status_code is codes.created
    buyerSession['buyerID'] = newBuyer.json()['ID']
    log.info('Created ' + buyerSession['buyerID'] + ' buyer.')

    # Assign Message Sender to Buyer

    messageSenders = admin.get(
        configInfo['API'] + 'v1/messagesenders/?name=allMessageTypes')
    log.debug(json.dumps(messageSenders.json()['Items'][0], indent=4))
    messageID = messageSenders.json()['Items'][0]['ID']
    assignmentBody = {
        "MessageSenderID": messageID,
        "BuyerID": buyerSession['buyerID']
    }

    assignMessageSender = admin.post(
        configInfo['API'] + 'v1/messagesenders/assignments', json=assignmentBody)
    log.debug(assignMessageSender.status_code)
    assert assignMessageSender.status_code == 204
    # create new user in buyer
    userProfile = fake.profile()
    userBody = {
        "ID": "BuyerUser{user-incrementor}",
        "Username": userProfile['username'],
        "Password": fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True),
        "FirstName": userProfile['name'].split()[0],
        "LastName": userProfile['name'].split()[1],
        "Email": userProfile['mail'].split('@')[0] + '.' + configInfo['MAILOSAUR-SERVER'] + '@mailosaur.io',
        "Phone": fake.phone_number(),
        "Active": True,
        "xp": {
            'faker': True
        }
    }
    log.debug(json.dumps(userBody, indent=4))

    buyerSession['password'] = userBody['Password']

    buyerUser = admin.post(
        configInfo['API'] + 'v1/buyers/' + buyerSession['buyerID'] + '/users', json=userBody)
    log.debug(buyerUser.status_code)
    assert buyerUser.status_code is codes.created
    log.info('Created ' + buyerUser.json()['ID'] + ' user.')

    buyerSession['userID'] = buyerUser.json()['ID']
    buyerSession['username'] = buyerUser.json()['Username']

    # assign security profile

    securityProfiles = admin.get(
        configInfo['API'] + 'v1/securityprofiles/buyerProfile1')
    log.debug(json.dumps(securityProfiles.json(), indent=4))

    assignBody = {
        "SecurityProfileID": "buyerProfile1",
        "BuyerID": buyerSession['buyerID']
    }
    assignProfile = admin.post(
        configInfo['API'] + 'v1/securityprofiles/assignments', json=assignBody)
    log.debug(assignProfile.status_code)
    assert assignProfile.status_code is codes.no_content

    # create a default ship from address

    addressBody = {
        "CompanyName": buyerName,
        "FirstName": "",
        "LastName": "",
        "Street1": fake.street_address(),
        "Street2": None,
        "City": fake.city(),
        "State": fake.state_abbr(),
        "Zip": fake.zipcode(),
        "Country": fake.country_code(),
        "Phone": fake.phone_number(),
        "AddressName": "DefaultShipFromAddress",
        "xp": {
            'fake': True
        }
    }

    newAddress = admin.post(
        configInfo['API'] + 'v1/addresses', json=addressBody)
    log.info(newAddress.status_code)
    assert newAddress.status_code is codes.created

    # create a default catalog and assign to buyer

    defaultCatalog = admin.get(
        configInfo['API'] + 'v1/catalogs/' + buyerSession['buyerID'])

    assert defaultCatalog.status_code is codes.ok

    # price schedule

    psBody = {
        "Name": "defaultPriceSchedule",
        "ApplyTax": True,
        "ApplyShipping": True,
        "MinQuantity": 1,
        "MaxQuantity": random.randint(0, 100),
        "UseCumulativeQuantity": True,
        "RestrictedQuantity": False,
        "PriceBreaks": [
            {
                "Quantity": 1,
                "Price": random.randint(0, 1000)
            }
        ],
        "xp": {}
    }
    log.debug(psBody)

    createPS = admin.post(configInfo['API'] + 'v1/priceschedules', json=psBody)
    log.debug(createPS.status_code)
    assert createPS.status_code is codes.created

    # products create & to catalog
    allProducts = get_Products(configInfo, admin,  {'PageSize': 100})
    log.debug(allProducts['Meta'])
    #assert allProducts['Meta']['TotalCount'] == 0

    newProducts = createProducts(
        configInfo, admin, DefaultPriceScheduleID=createPS.json()['ID'], numberOfProducts=20)
    log.debug(newProducts)

    allProducts = get_Products(configInfo, admin, {'PageSize': 100})
    log.debug(allProducts['Meta'])

    for item in allProducts['Items']:
        assignProductsBody = {
            "CatalogID": buyerSession['buyerID'],
            "ProductID": item['ID']
        }
        productCatalogAssign = admin.post(
            configInfo['API'] + 'v1/catalogs/productassignments/', json=assignProductsBody)
        log.debug(productCatalogAssign.text)
        log.debug(productCatalogAssign.status_code)
        assert productCatalogAssign.status_code is codes.no_content

    # set up buyer user session

    log.debug(buyerSession)
    log.info(connections)

    client_id = buyerSession['clientID']
    username = buyerSession['username']
    password = buyerSession['password']
    scope = ['Shopper', 'MeAdmin']

    # can successfully get a token
    token = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    buyer = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + token['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    buyer.headers.update(headers)

    buyerSession['session'] = buyer

    log.debug(buyerSession)

    connections['buyer'] = buyerSession['session']

    def buyer_teardown():
        log.info('tearing down the buyer user ' +
                 buyerUser.json()['ID'] + '...')

        deleteUser = admin.delete(
            configInfo['API'] + 'v1/buyers/' + buyerSession['buyerID'] + '/users/' + buyerUser.json()['ID'])
        log.debug(deleteUser.status_code)
        assert deleteUser.status_code is codes.no_content

        deleteAddress = admin.delete(
            configInfo['API'] + 'v1/addresses/' + newAddress.json()['ID'])
        log.debug(deleteAddress.status_code)
        assert deleteAddress.status_code is codes.no_content

        log.info('tearing down the ' + buyerName + ' buyer...')
        deleteBuyer = admin.delete(
            configInfo['API'] + 'v1/buyers/' + buyerSession['buyerID'])
        log.debug(deleteBuyer.status_code)
        assert deleteBuyer.status_code is codes.no_content

        log.info('tearing down the all the products...')
        for item in allProducts['Items']:
            deleteProduct = admin.delete(
                configInfo['API'] + 'v1/products/' + item['ID'])
            log.debug(deleteProduct.status_code)
            assert deleteProduct.status_code is codes.no_content

        log.info('tearing down the ' + buyerName + ' catalog...')
        deleteCatalog = admin.delete(
            configInfo['API'] + 'v1/catalogs/' + buyerSession['buyerID'])
        log.debug(deleteCatalog.status_code)
        assert deleteCatalog.status_code is codes.no_content

    request.addfinalizer(buyer_teardown)


def test_1(buyer_setup, connections):
    log.info('-  test_1()')

    log.info(connections['admin'])
    log.info(connections['buyer'])


def test_2(buyer_setup):
    log.info('-  test_2()')
