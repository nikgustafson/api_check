import pytest
import tempfile


# build enivrionment 

# install requirements

# make tmp dir

path = tempfile.TemporaryDirectory().name
print(str(path))
# currently runs all tests

pytest.main(['-m smoke', '--ENV=prod', '--junitxml='+str(path)])
pytest.main(['-m search', '--ENV=prod', '--junitxml='+str(path)])