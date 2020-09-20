import os

pytest_plugins = "playwright", "dash", "parallel"


def pytest_addoption(parser):
    parser.addoption("--url", action="store", default="http://localhost:5000", help="target url")


def pytest_configure(config):
    os.environ["url"] = config.getoption("url")

