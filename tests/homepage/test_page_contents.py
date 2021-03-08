import pytest


def test_title(page):
    """Checks for correct page title

    Args:
        page : playwright browser page
    """
    page.goto("/")
    assert page.title() == "Tesla-ver"


def test_chart_button(page):
    """Tests that chart button is styled correctly and has the right name

    Args:
        page : playwright browser page
    """
    page.goto("/")
    assert page.innerText("css=div .btn.btn-success") == "Bubble Chart"


def test_data_upload_button(page):
    page.goto("/")
    assert page.innerText("css=div .btn.btn-primary") == "Data Uploading"


def test_paragraph_header(page):
    page.goto("/")
    assert len(page.querySelectorAll("p")) == 2
