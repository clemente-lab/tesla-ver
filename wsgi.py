import flask
import logging
from werkzeug.debug import DebuggedApplication
from datetime import datetime
from tesla_ver.bubble_chart.bubble_chart import generate_bubble_chart
from tesla_ver.data_uploading.data_uploading import generate_data_uploading


# Sets up logging

logging.basicConfig(
    filename=str(datetime.now()) + ".log",
    filemode="w",
    format="'%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
logging.debug(f"==Log Start==")
# Creates the flask server
logging.debug("Starting Flask Server")

server = flask.Flask(__name__)

logging.debug("✅ Flask server created")

server.wsgi_app = DebuggedApplication(server.wsgi_app, evalex=True)

logging.debug("Werkzeug DebuggedApplication Created")
# Creates the data uploading screena and connects it to the flask server
generate_data_uploading(server=server)
logging.debug("✅ Data Uploading Screen created and connected")

# Creates the bubble chart and connects it to the flask server
generate_bubble_chart(server=server)

logging.debug("✅ Bubble Chart Screen created and connected")


@server.route("/")
def index():
    """Renders the landing page."""
    # TODO: Create an HTML import function
    return """
<html>
<div><h1>Flask App</h1>
    <a href="/datauploading.html">Data Uploading</a>
    <a href="/bubblechart.html">Bubble Chart</a>
</div>
</html>
"""


@server.route("/bubblechart.html")
def render_bubble_chart():
    """Redirects to the Dash Bubble chart."""
    return flask.redirect("/bubblechart.html")


@server.route("/datauploading.html")
def render_data_uploading():
    return flask.redirect("/datauploading.html")


if __name__ == "__main__":
    logging.debug("Server starting")
    server.run(debug=True)
    logging.debug("✅ Server started")
