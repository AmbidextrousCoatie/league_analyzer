from flask import Flask, request, send_from_directory
import os
import time

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
    
    # Custom static file handler with cache-busting
    @app.route('/static/<path:filename>')
    def custom_static(filename):
        """Serve static files with cache-busting headers"""
        response = send_from_directory(app.static_folder, filename)
        
        # Add cache-busting headers for JavaScript and CSS files
        if filename.endswith(('.js', '.css')):
            # Set cache headers to prevent caching
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            
            # Add ETag based on file modification time for conditional requests
            file_path = os.path.join(app.static_folder, filename)
            if os.path.exists(file_path):
                mtime = os.path.getmtime(file_path)
                response.set_etag(f'"{int(mtime)}"')
        
        return response
    
    # Template helper for cache busting
    @app.context_processor
    def inject_cache_buster():
        """Inject cache busting helper into templates"""
        from app.utils.cache_buster import get_static_url
        return dict(static_url=get_static_url)
    
    from app.routes import main, player_routes, league_routes, team_routes
    app.register_blueprint(main.bp)
    app.register_blueprint(player_routes.bp)
    app.register_blueprint(league_routes.bp)
    app.register_blueprint(team_routes.bp)
    return app 