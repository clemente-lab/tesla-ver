import pytest
import os


def test_title(page):
    page.goto(os.getenv("url")+"/datauploading.html")
    assert page.title() == "Dash"

