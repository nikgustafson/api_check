import pytest
import configparser
import tesults
import sys
import os
from _pytest.runner import runtestprotocol



def pytest_addoption(parser):
		parser.addoption("--ENV", action="store", help="Choose the API Environment to run against: QA or PROD", default="QA")

@pytest.fixture()
def configInfo(pytestconfig):
		global data
		environment = pytestconfig.getoption('--ENV')
		print(environment)
		environment = str.lower(environment)
		config = configparser.ConfigParser()
		config.read('config.ini') # local config file
		configData = config['QA-CONFIG']
		if environment == 'qa':
				configData = config['QA-CONFIG']
		if environment == 'prod':
				configData = config['PROD-CONFIG']
		config = configparser.ConfigParser()
		config.read('config.ini') # local config file
		tesultsKey = configData['TESULTS-KEY']
		print(tesultsKey)
		data['target'] = tesultsKey

		return configData


#----------------------------# tesults set up

# The data variable holds test results and tesults target information, at the end of test run it is uploaded to tesults for reporting.

data = {
		'target': '',
		'results': { 'cases': [] }
}

# Converts pytest test outcome to a tesults friendly result (for example pytest uses 'passed', tesults uses 'pass')
def tesultsFriendlyResult (outcome):
		if (outcome == 'passed'):
				return 'pass'
		elif (outcome == 'failed'):
				return 'fail'
		else:
				return 'unknown'

# Extracts test failure reason
def reasonForFailure (report):
		if report.outcome == 'passed':
				return ''
		else:
				return report.longreprtext

def paramsForTest (item):
		paramKeys = item.get_marker('parametrize')
		if (paramKeys):
				paramKeys = paramKeys.args[0]
				params = {}
				values = item.name.split('[')
				if len(values) > 1:
						values = values[1]
						values = values[:-1] # removes ']'
						values = values.split("-") # values now separated
				else:
						return None
				for key in paramKeys:
						if (len(values) > 0):
								params[key] = values.pop(0)
						return params
		else:
				return None

def filesForTest (item):
	files = []
	path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "path-to-test-generated-files", item.name)
	if os.path.isdir(path):
		for dirpath, dirnames, filenames in os.walk(path):
				for file in filenames:
						files.append(os.path.join(path, file))
	return files

# A pytest hook, called by pytest automatically - used to extract test case data and append it to the data global variable defined above.
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

# A pytest hook, called by pytest automatically - used to upload test results to tesults.
def pytest_unconfigure (config):
		global data
		# Report Build Information (Optional)
		# buildcase = {
		# 'name': '1.0.0', #get_build_number()
		# 'result': 'pass', # Must be 'pass' , 'fail', or 'unknown'
		# 'suite':  '[build]' # Do not change. Indicates this is build information and not a test
		# As with tests you can also add a desc (description), reason, and files!
		# }
		# data['results']['cases'].append(buildcase)

		print ('-----Tesults output-----')
		if len(data['results']['cases']) > 0:
				print ('data: ' + str(data))
				ret = tesults.results(data)
				print ('success: ' + str(ret['success']))
				print ('message: ' + str(ret['message']))
				print ('warnings: ' + str(ret['warnings']))
				print ('errors: ' + str(ret['errors']))
		else:
				print ('No test results.')