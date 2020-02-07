import dash
import flask
from tesla_ver.bubble_chart import generateBubbleChart

server = flask.Flask(__name__)
app = generateBubbleChart(server= server)

@server.route('/')
def index():
    return '''
<html>
<div>
    <h1>Flask App</h1>
    <a href="/bubblechart.html">Bubble Chart</a>
</div>
</html>
'''
@server.route('/bubblechart.html')
def render_bubble_chart():
  return flask.redirect('/bubblechart.html')

if __name__ == '__main__':
    server.run(debug=True)
