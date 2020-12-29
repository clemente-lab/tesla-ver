import pytest
from playwright import _page


def test_title(page):
    """Checks for correct page title

    Args:
        page : pytest-playwright fixture object
    """
    page.goto("/")
    assert page.title() == "Tesla-ver"


def test_chart_button(page):
    page.goto("/")
    # page.evalOnSelector("")
    assert page.innerText("css=div .btn.btn-success") == "Bubble Chart"


def test_data_upload_button(page):
    page.goto("/")
    # page.evalOnSelector("")
    assert page.innerText("css=div .btn.btn-primary") == "Data Uploading"


def test_paragraph_header(page):
    page.goto("/")
    assert len(page.querySelectorAll("p")) == 2
