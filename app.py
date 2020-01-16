from flask import Flask

def create_app():
  app = Flask(__name__,
              instance_relative_config=False)
  app.config.from_object('config.config')

  with app.app_context():
    #import main blueprint
    from . import routes
