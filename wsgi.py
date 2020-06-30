import flask
from werkzeug.debug import DebuggedApplication
from tesla_ver.bubble_chart import generate_bubble_chart
from tesla_ver.data_uploading import generate_data_uploading

# Creates the flask server
server = flask.Flask(__name__)
server.wsgi_app = DebuggedApplication(server.wsgi_app, evalex=True)

# Creates the data uploading screena and connects it to the flask server
generate_data_uploading(server=server)

# Creates the bubble chart and connects it to the flask server
generate_bubble_chart(server=server)


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
    server.run(debug=True)
