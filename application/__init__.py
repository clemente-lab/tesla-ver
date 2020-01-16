from flask import Flask

def create_app():
  """Construct the Core application"""
  app = Flask(__name__,
              instance_relative_config=False)
  app.config.from_object('config.Config')

  with app.app_context():
    #blueprints
    from application import routes
    app.register_blueprint(routes.main_bp)

    from application.dash_app.bubble_chart import create_bubble_graph
    app = create_bubble_graph(app)

    return app
