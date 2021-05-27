import datetime
from pathlib import Path
from time import sleep

def test_main_process(page):
  """Walks through the main workflow of the app, taking screenshots at each step

  Args:
      page : playwright browser page
  """
  page.goto("/")
  # current_time = datetime.date.today().strftime("%d-%m-%Y")
  current_time = datetime.datetime.now()
  # screenshot_path = Path('./tests/screenshots')
  page.screenshot(path=f"./tests/screenshots/main-page-{current_time}.png")
  # page.screenshot(path=f'wow_test.png')
  page.click('"Data Uploading"')

# Intercepts filechooser event and uploads test dataset (tesla_data_10.tsv)
  with page.expect_file_chooser() as fc_info:
    page.click("id=upload")

  file_chooser = fc_info.value
  file_chooser.set_files("./data/tesla_data_10.tsv")

  sleep(1)

  page.screenshot(path=f"./tests/screenshots/data-page-{current_time}.png")


# Uploads the data to redis
  page.click("id=redis-upload-button")

  sleep(1)

# Switches to graphing page
  page.click("id=graph-link")

  sleep(2)

# clicks button to display graph
  page.click("id=upload-button")
  sleep(0.5)
  page.screenshot(path=f"./tests/screenshots/graphing-unclicked-page-{current_time}.png")


# select values for dropdowns and take a screenshot of the dot plot without animation
  page.click("id=y_dropdown")
  page.click("text=Bacteria 2")

  page.click("id=x_dropdown")
  page.click("text=Bacteria 3")

  page.screenshot(path=f"./tests/screenshots/graphing-dots-{current_time}.png")

#Switch to line plots and screenshot

  page.click("text=Line Plots")
  # print("selected line graphs")
  page.screenshot(path=f"./tests/screenshots/graphing-line-plots-{current_time}.png")
