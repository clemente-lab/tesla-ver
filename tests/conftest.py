import os

pytest_plugins = ("playwright", "parallel")

import pytest


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "ignoreHTTPSErrors": True}


def pytest_addoption(parser):
    parser.addoption("--url", action="store", default="http://localhost:5000", help="target url")


def pytest_configure(config):
    os.environ["url"] = config.getoption("url")

