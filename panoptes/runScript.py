import pytest


# currently runs all tests

pytest.main(['-m smoke', '--ENV=prod', '--junitxml="prod-smoke.xml"'])
#pytest.main(['-m', '--ENV=prod', '--junitxml='+str(path)+'-prod-search.xml'])
pytest.main(['-m smoke', '--ENV=qa', '--junitxml="qa-smoke.xml"'])
#pytest.main(['-m search', '--ENV=qa', '--junitxml='+str(path)+'-qa-search.xml'])