import pytest
import tempfile


# build enivrionment 

# install requirements

# make tmp dir

path = tempfile.TemporaryDirectory().name
print(str(path))
# currently runs all tests

pytest.main(['-m smoke', '--ENV=prod', '--junitxml='+str(path)+'-prod-smoke.xml'])
#pytest.main(['-m', '--ENV=prod', '--junitxml='+str(path)+'-prod-search.xml'])
#pytest.main(['-m smoke', '--ENV=qa', '--junitxml='+str(path)+'-qa-smoke.xml'])
#pytest.main(['-m search', '--ENV=qa', '--junitxml='+str(path)+'-qa-search.xml'])