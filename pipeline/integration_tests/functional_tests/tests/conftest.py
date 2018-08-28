import pytest


def pytest_addoption(parser):
    parser.addoption("--report_path", action="store", default="junit/integration.xml",
                     help="report_path: report path is the path to the junit report")


@pytest.fixture
def report_path(request):
    return request.config.getoption("--report_path")
