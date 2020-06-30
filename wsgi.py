import flask
from werkzeug.debug import DebuggedApplication
from tesla_ver.bubble_chart import generateBubbleChart

# Creates the flask server
server = flask.Flask(__name__)
server.wsgi_app = DebuggedApplication(server.wsgi_app, evalex=True)

# Creates the dashboard and connects it to the flask server
generateBubbleChart(server=server)


@server.route("/")
def index():
    """Renders the landing page."""
    # TODO: Create an HTML import function
    return """
<html>
<div><h1>Flask App</h1>
    <a href="/bubblechart.html">Bubble Chart</a>
</div>
</html>
"""


@server.route("/bubblechart.html")
def render_bubble_chart():
    """Redirects to the Dash Bubble chart."""
    return flask.redirect("/bubblechart.html")


if __name__ == "__main__":
    server.run(debug=True)
