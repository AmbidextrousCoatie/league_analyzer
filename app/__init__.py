from flask import Flask, request
import os

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
    app.secret_key = 'your-secret-key-here'
    
    # Configure session for production
    app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem for production
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session lifetime
    app.config['SESSION_FILE_THRESHOLD'] = 500  # Number of sessions before cleanup
    
    # Add middleware to ensure DataManager loads fresh data from session
    @app.before_request
    def ensure_fresh_data():
        """Ensure DataManager loads fresh data from session on every request"""
        try:
            from app.services.data_manager import DataManager
            # Create a DataManager instance to ensure it loads from session
            # This is crucial for production with multiple worker processes
            data_manager = DataManager()
            # Force reload from session to ensure consistency
            data_manager.force_reload_from_session()
        except Exception as e:
            # Log error but don't break the request
            print(f"Warning: Could not ensure fresh data: {e}")
    
    from app.routes import main, player_routes, league_routes, team_routes
    app.register_blueprint(main.bp)
    app.register_blueprint(player_routes.bp)
    app.register_blueprint(league_routes.bp)
    app.register_blueprint(team_routes.bp)
    return app 