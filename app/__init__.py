from flask import Flask
import os

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
    app.secret_key = 'your-secret-key-here'
    
    from app.routes import main, player_routes, league_routes, team_routes
    app.register_blueprint(main.bp)
    app.register_blueprint(player_routes.bp)
    app.register_blueprint(league_routes.bp)
    app.register_blueprint(team_routes.bp)
    return app 