import pytest


def test_title(page):
    page.goto("http://localhost:5000")
    assert page.title() == "Tesla-ver"
