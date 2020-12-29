import pytest
import os
from time import sleep


def test_title(page):
    page.goto("/datauploading.html")
    sleep(1)
    assert page.title() == "Dash"

