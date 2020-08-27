import flask
import logging
from werkzeug.debug import DebuggedApplication
from datetime import datetime
from tesla_ver.bubble_chart.bubble_chart import generate_bubble_chart
from tesla_ver.data_uploading.data_uploading import generate_data_uploading


server = flask.Flask(__name__, static_folder="homepage/build/static", template_folder="homepage/build/")

# If application is being run through gunicorn, pass logging through to gunicorn
if __name__ != "__main__":
    # Connects flask logging to the gunicorn logging handler
    gunicorn_logger = logging.getLogger("gunicorn.error")
    server.logger.handlers = gunicorn_logger.handlers
    server.logger.setLevel(gunicorn_logger.level)

server.logger.debug("✅ Flask server created")

server.wsgi_app = DebuggedApplication(server.wsgi_app, evalex=True)

server.logger.debug("Werkzeug DebuggedApplication Created")
# Creates the data uploading screena and connects it to the flask server
generate_data_uploading(server=server)
server.logger.debug("✅ Data Uploading Screen created and connected")

# Creates the bubble chart and connects it to the flask server
generate_bubble_chart(server=server)

server.logger.debug("✅ Bubble Chart Screen created and connected")


@server.route("/")
def index():
    """Renders the landing page."""
    server.logger.debug("rendering homepage")
    return flask.render_template("index.html")


@server.route("/bubblechart.html")
def render_bubble_chart():
    """Redirects to the Dash Bubble chart."""
    server.logger.debug("redirecting to bubblechart")
    return flask.redirect("/bubblechart.html")


@server.route("/datauploading.html")
def render_data_uploading():
    server.logger.debug("redirecting to data uploader")
    return flask.redirect("/datauploading.html")


if __name__ == "__main__":
    server.logger.debug("Server starting")
    server.run(debug=True)
    server.logger.debug("✅ Server started")
