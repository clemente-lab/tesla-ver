def test_title(page):
    """Checks for correct page title

    Args:
        page : playwright browser page
    """
    page.goto("/")
    assert page.title() == "Tesla-ver"
