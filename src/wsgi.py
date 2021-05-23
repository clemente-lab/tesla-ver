# import flask
import logging
from flask import Flask, render_template, redirect, session
from werkzeug.debug import DebuggedApplication
from datetime import datetime
from os import urandom
from uuid import uuid4
from functools import wraps
from tesla_ver.bubble_chart.bubble_chart import generate_charting
from tesla_ver.data_uploading.data_uploading import generate_data_uploading


server = Flask(__name__, static_folder="homepage/build/static", template_folder="homepage/build/")

# set a new random secret key for sessions on each app launch
server.secret_key = urandom(24)

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
generate_charting(server=server)

server.logger.debug("✅ Bubble Chart Screen created and connected")

def check_uuid_initialized(redirect_func):
    @wraps(redirect_func)
    def wrapped(*args, **kwargs):
        uuid = session.get('uuid')
        if uuid:
            return redirect_func(*args, **kwargs)
        else:
            # session['uuid'] = str(uuid4().hex)
            session['uuid'] = None
            return redirect_func(*args, **kwargs)
    return wrapped



@server.route("/")
@check_uuid_initialized
def index():
    """Renders the landing page."""
    server.logger.debug("rendering homepage")
    server.logger.debug("User with UUID:" + session.get('uuid') + "connected to homepage")
    return render_template("index.html")

@server.route("/datauploading.html")
@check_uuid_initialized
def render_data_uploading():
    server.logger.debug("redirecting to data uploader")
    server.logger.debug("User with UUID:" + session.get('uuid') + "connected to data uploading")
    return redirect("/datauploading.html")


@server.route("/bubblechart.html")
@check_uuid_initialized
def render_charting_page():
    """Redirects to the Dash Bubble chart."""
    server.logger.debug("redirecting to bubblechart")
    server.logger.debug("User with UUID:" + session.get('uuid') + "connected to charting")
    return redirect("/bubblechart.html")


if __name__ == "__main__":
    server.logger.debug("Server starting")
    server.run(debug=True)
    server.logger.debug("✅ Server started")
