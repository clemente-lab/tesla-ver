import pytest
import os


def test_title(page):
    page.goto(os.getenv("url"))
    assert page.title() == "Dash"

