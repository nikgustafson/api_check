import pytest

def pytest_addoption(parser):
	parser.addoption("--ENV", action="store", help="Choose the API Environment to run against: QA or PROD", default="QA")

@pytest.fixture()
def apiEnv(pytestconfig):
	return pytest.option.ENV 