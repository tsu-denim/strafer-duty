import os
import pytest
import sys

here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, here)
print(sys.path)

def pytest_addoption(parser):
    parser.addoption("--report_path", action="store", default="junit/integration.xml",
                     help="report_path: report path is the path to the junit report")


@pytest.fixture
def report_path(request):
    return request.config.getoption("--report_path")
