import pytest
import tempfile
import os


# build enivrionment 

# install requirements


# set current dir

cwd = os.getcwd();
print(cwd)
if 'panoptes' not in cwd:
	default_path = '../api-check/panoptes'
	os.chdir(default_path)

cwd = os.getcwd();
print(cwd)

# make tmp dir

path = tempfile.TemporaryDirectory().name
print(str(path))

# currently runs all tests

pytest.main(['-m smoke', '--ENV=prod', '--junitxml='+str(path)+'-prod-smoke.xml'])
#pytest.main(['-m', '--ENV=prod', '--junitxml='+str(path)+'-prod-search.xml'])
pytest.main(['-m smoke', '--ENV=qa', '--junitxml='+str(path)+'-qa-smoke.xml'])
#pytest.main(['-m search', '--ENV=qa', '--junitxml='+str(path)+'-qa-search.xml'])