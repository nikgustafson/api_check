import pytest
import configparser
import tesults
import logging
import json
import sys
import os
import pytz
import jwt
from datetime import datetime
from pathlib import Path
from _pytest.runner import runtestprotocol
from .auth import get_Token_UsernamePassword, get_anon_user_token
from .me import get_Me
import requests
from requests import codes
from faker import Faker
import random
import json


fake = Faker()

from .auth import get_Token_UsernamePassword
from .products import get_Products, createProducts


log = logging.getLogger(__name__)


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._previousfailed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        previousfailed = getattr(item.parent, "_previousfailed", None)
        if previousfailed is not None:
            pytest.xfail("previous test failed (%s)" % previousfailed.name)


def pytest_addoption(parser):
    parser.addoption("--ENV", action="store",
                     help="Choose the API Environment to run against: QA or PROD", default="QA")
    parser.addoption("--REPORT", action="store",
                     help="Reporting: YES or NO", default="YES")
    parser.addoption("--CONFIG", action="store",
                     help="Config.ini File Location", default="config_new.ini")


def pytest_configure(config):
    environment = config.getoption('--ENV')
    reporting = config.getoption('--REPORT')
    configLoc = config.getoption('--CONFIG')
    config.oc_env = str.lower(environment)


@pytest.fixture(scope="session", autouse=True)
def configInfo(pytestconfig):
    global data
    global reporting

    p = Path('.')

    environment = pytestconfig.getoption('--ENV')
    print(environment)
    environment = str.lower(environment)
    pytest.global_env = environment

    reporting = pytestconfig.getoption('--REPORT')
    print(reporting)
    reporting = str.lower(reporting)
    pytest.reporting = str.lower(reporting)

    configLoc = pytestconfig.getoption('--CONFIG')

    loc = p.joinpath(configLoc)
    assert loc.exists() is True
    assert loc.is_dir() is False

    # log.info(configLoc)

    config = configparser.ConfigParser()
    print()
    config.read(configLoc)  # local config file
    # log.info(repr(config.sections()))
    configData = config['QA-CONFIG']
    if environment == 'qa':
        assert config.has_section('QA-CONFIG')
        configData = config['QA-CONFIG']
    if environment == 'prod':
        assert config.has_section('PROD-CONFIG')
        configData = config['PROD-CONFIG']
    tesultsKey = configData['TESULTS-KEY']
    # print(tesultsKey)
    data['target'] = tesultsKey

    # print(reporting)
    log.info(reporting)

    return configData


@pytest.fixture(scope="session", autouse=True)
def connections(configInfo):

    client_id = configInfo['SELLER-API-CLIENT']
    username = configInfo['SELLER-ADMIN-USERNAME']
    password = configInfo['SELLER-ADMIN-PASSWORD']
    scope = ['FullAccess']

    # can successfully get a token
    adminToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    admin = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + adminToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    admin.headers.update(headers)

    sessions = {
        'admin': admin
    }

    return sessions


@pytest.fixture(scope="session", autouse=True)
def mod_header(request):
    log.info('\n------------------------------\n| API Environment: ' +
             pytest.global_env + ' |\n------------------------------\n')
    return(pytest.global_env)


@pytest.fixture(scope="session", autouse=True)
def reporting_header(request):
    log.info('\n------------------------------\n| Reporting: ' +
             pytest.reporting + ' |\n------------------------------\n')
    return(pytest.reporting)


@pytest.fixture(scope='module', autouse=True)
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
    log.info('Assigned ' + messageID + ' to ' +
             buyerSession['buyerID'] + ' buyer.')
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
    log.info('Assigned basic security profile to ' +
             buyerSession['buyerID'] + ' buyer.')

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
    log.debug(newAddress.status_code)
    assert newAddress.status_code is codes.created
    log.info('Created new ShipFrom Address')

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
    log.info('Created new Default Price Schedule')

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
    log.info('Created and Assigned 20 products to ' + buyerSession['buyerID'])
    # set up buyer user session

    log.debug(buyerSession)
    log.debug(connections)

    client_id = buyerSession['clientID']
    username = buyerSession['username']
    password = buyerSession['password']
    scope = ['Shopper', 'MeAdmin', 'MeAddressAdmin']

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
    configInfo['Buyer'] = buyerSession['buyerID']

    # anon user session

    # can successfully get a token
    anontoken = get_anon_user_token(configInfo, client_id, scope)
    anon = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + anontoken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    anon.headers.update(headers)

    connections['anon'] = anon

    for item in connections:
        log.debug(item)
        log.debug(connections[item])
       # log.debug(json.dumps(connections[item].auth, indent=4))
        log.debug(connections[item].headers)

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


#----------------------------# tesults set up

# The data variable holds test results and tesults target information, at
# the end of test run it is uploaded to tesults for reporting.

data = {
    'target': '',
    'results': {'cases': []}
}

reporting = ''

# Converts pytest test outcome to a tesults friendly result (for example
# pytest uses 'passed', tesults uses 'pass')


def tesultsFriendlyResult(outcome):
    if (outcome == 'passed'):
        return 'pass'
    elif (outcome == 'failed'):
        return 'fail'
    else:
        return 'unknown'

# Extracts test failure reason


def reasonForFailure(report):
    if report.outcome == 'passed':
        return ''
    else:
        return report.longreprtext


def paramsForTest(item):
    paramKeysObj = item.get_marker('parametrize')
    if (paramKeysObj):
        index = 0
        paramKeys = []
        while (index < len(paramKeysObj.args)):
            keys = paramKeysObj.args[index]
            keys = keys.split(",")
            for key in keys:
                paramKeys.append(key)
            index = index + 2
        params = {}
        values = item.name.split('[')
        if len(values) > 1:
            values = values[1]
            values = values[:-1]  # removes ']'
            valuesSplit = values.split("-")  # values now separated
            if len(valuesSplit) > len(paramKeys):
                params["[" + "-".join(paramKeys) + "]"] = "[" + values + "]"
            else:
                for key in paramKeys:
                    if (len(valuesSplit) > 0):
                        params[key] = valuesSplit.pop(0)
            return params
        else:
            return None
    else:
        return None


def filesForTest(item):
    files = []
    path = os.path.join(os.path.dirname(os.path.realpath(
        __file__)), "path-to-test-generated-files", item.name)
    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for file in filenames:
                files.append(os.path.join(path, file))
    return files

# A pytest hook, called by pytest automatically - used to extract test
# case data and append it to the data global variable defined above.


def pytest_runtest_protocol(item, nextitem):
    global data
    reports = runtestprotocol(item, nextitem=nextitem)
    for report in reports:
        if report.when == 'call':
            testcase = {
                'name': item.name,
                'result': tesultsFriendlyResult(report.outcome),
                'suite': str(item.parent.name),
                'desc': item.name,
                'reason': reasonForFailure(report)
            }
            files = filesForTest(item)
            if len(files) > 0:
                testcase['files'] = files
            params = paramsForTest(item)
            if (params):
                testcase['params'] = params
            testname = item.name.split('[')
            if len(testname) > 1:
                testcase['name'] = testname[0]
            paramDesc = item.get_marker('description')
            if (paramDesc):
                testcase['desc'] = paramDesc.args[0]
            data['results']['cases'].append(testcase)
    return True

# A pytest hook, called by pytest automatically - used to upload test
# results to tesults.


def pytest_unconfigure(config):
    global data
    global reporting
    # Report Build Information (Optional)
    # buildcase = {
    # 'name': '1.0.0', #get_build_number()
    # 'result': 'pass', # Must be 'pass' , 'fail', or 'unknown'
    # 'suite':  '[build]' # Do not change. Indicates this is build information and not a test
    # As with tests you can also add a desc (description), reason, and files!
    # }
    # data['results']['cases'].append(buildcase)
   # log.info(config)
    # log.info(reporting)
    # print(reporting)
    if reporting == 'yes':
        print('-----Tesults output-----')
        if len(data['results']['cases']) > 0:
            print('data: ' + str(data))
            ret = tesults.results(data)
            print('success: ' + str(ret['success']))
            print('message: ' + str(ret['message']))
            print('warnings: ' + str(ret['warnings']))
            print('errors: ' + str(ret['errors']))
        else:
            print('No test results.')
    else:
        print('-----No Reporting-----')
