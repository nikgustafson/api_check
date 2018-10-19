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
import requests

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
                     help="Config.ini File Location", default="config.ini")


def pytest_configure(config):
    environment = config.getoption('--ENV')
    reporting = config.getoption('--REPORT')
    configLoc = config.getoption('--CONFIG')
    config.oc_env = str.lower(environment)


@pytest.fixture(scope='session', autouse=True)
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
    # log.info(Path.cwd())
    # log.info(loc.resolve())
    # log.info(loc.exists())
    # log.info(loc.is_dir())
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


@pytest.fixture(scope='session', autouse=True)
def connections(configInfo):

    client_id = configInfo['ADMIN-CLIENTID']
    username = configInfo['ADMIN-USERNAME']
    password = configInfo['ADMIN-PASSWORD']
    scope = ['FullAccess']

    loc_tz = pytz.timezone('America/Chicago')

    # admin token
    adminToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)
    log.debug('admin session token ' + json.dumps(adminToken, indent=2))
    '''
    decoded = jwt.decode(adminToken['access_token'], verify=False)
    #log.info('--------')
    #log.info('today\'s date is:')
    c_dt = loc_tz.localize(datetime.today(), is_dst=False)
    #log.info(c_dt)
    #log.info('--------')

    notbefore = loc_tz.localize(datetime.utcfromtimestamp(
        decoded['nbf']), is_dst=False)
    expiration = loc_tz.localize(datetime.utcfromtimestamp(
        decoded['exp']), is_dst=False)
    log.info('--------')
    log.info('Admin NBF: ' + str(notbefore))
    log.info('Admin EXP: ' + str(expiration))
    log.info('--------')

    #log.info(json.dumps(user, indent=4))
    '''

    # BUYER TOKEN

    client_id = configInfo['BUYER-CLIENTID']
    username = configInfo['BUYER-USERNAME']
    password = configInfo['BUYER-PASSWORD']
    scope = ['Shopper']

    buyerToken = get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)
    log.debug('buyer session token ' + json.dumps(buyerToken, indent=2))
    '''
    decoded = jwt.decode(buyerToken['access_token'], verify=False)
    log.info('--------')
    log.info('today\'s date is:')
    c_dt = loc_tz.localize(datetime.today(), is_dst=False)
    log.info(c_dt)
    log.info('--------')

    notbefore = loc_tz.localize(datetime.utcfromtimestamp(
        decoded['nbf']), is_dst=False)
    expiration = loc_tz.localize(datetime.utcfromtimestamp(
        decoded['exp']), is_dst=False)
    log.info('--------')
    log.info('BUYER NBF: ' + str(notbefore))
    log.info('BUYER EXP: ' + str(expiration))
    log.info('--------')
    '''
    buyer = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + buyerToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    buyer.headers.update(headers)

    admin = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + adminToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    admin.headers.update(headers)

    client_id = configInfo['BUYER-CLIENTID']

    anonToken = get_anon_user_token(configInfo, client_id)
    log.debug('anon session token ' + json.dumps(anonToken, indent=2))
    '''
    decoded = jwt.decode(anonToken['access_token'], verify=False)
    log.info('--------')
    log.info('today\'s date is:')
    c_dt = loc_tz.localize(datetime.today(), is_dst=False)
    log.info(c_dt)
    log.info('--------')

    notbefore = loc_tz.localize(datetime.utcfromtimestamp(
        decoded['nbf']), is_dst=False)
    expiration = loc_tz.localize(datetime.utcfromtimestamp(
        decoded['exp']), is_dst=False)
    log.info('--------')
    log.info('anon NBF: ' + str(notbefore))
    log.info('anon EXP: ' + str(expiration))
    log.info('--------')
    '''
    anon = requests.Session()

    headers = {
        'Authorization': 'Bearer ' + anonToken['access_token'],
        'Content-Type': 'application/json',
        'charset': 'UTF-8'
    }

    anon.headers.update(headers)

    return {
        'admin': admin,
        'buyer': buyer,
        'anon': anon
    }


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
