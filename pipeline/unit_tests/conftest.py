import sys
import os

# Make sure that the application source directory (this directory's parent) is
# on sys.path.
import pytest

here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, here)
print(sys.path)


def pytest_addoption(parser):
    parser.addoption("--test_resource_path", action="store", default="pipeline/unit_tests/test_resources/",
                     help="test_resource_path: test_resource_path is the path to the unit test mocking files")


@pytest.fixture
def test_resource_dir(request):
    return request.config.getoption("--test_resource_path")