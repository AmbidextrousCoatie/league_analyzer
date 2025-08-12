from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from data_access.pd_dataframes import fetch_column
from app.services.data_manager import DataManager
import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/set-season/<season>')
def set_season(season):
    session['selected_season'] = season
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/overall/<analysis>')
def overall_stats(analysis):
    season = session.get('selected_season', 'all')
    return render_template('overall.html', analysis=analysis, season=season)

@bp.route('/league/<analysis>')
def league_stats(analysis):
    season = session.get('selected_season', 'all')
    return render_template('league/stats.html', analysis=analysis, season=season)

@bp.route('/team/<analysis>')
def team_stats(analysis):
    season = session.get('selected_season', 'all')
    return render_template('team/stats.html', analysis=analysis, season=season)

@bp.route('/player/<analysis>')
def player_stats(analysis):
    season = session.get('selected_season', 'all')
    return render_template('player/content.html', analysis=analysis, season=season)

@bp.route('/get-data-sources-info')
def get_data_sources_info():
    try:
        data_manager = DataManager()
        # Force reload from session to ensure consistency across workers
        data_manager.force_reload_from_session()
        return {
            'success': True,
            'current_source': data_manager.current_source,
            'current_display_name': data_manager.get_source_display_name(data_manager.current_source),
            'available_sources': data_manager.get_available_sources(),
            'sources_info': data_manager.get_sources_info()
        }
    except Exception as e:
        print(f"ERROR: Exception in get_data_sources_info: {e}")
        return {
            'success': False,
            'current_source': 'bowling_ergebnisse.csv',
            'current_display_name': 'Simulated Data',
            'available_sources': ['bowling_ergebnisse.csv', 'bowling_ergebnisse_real.csv'],
            'message': f'Server error: {str(e)}'
        }, 500

@bp.route('/reload-data')
def reload_data():
    data_source = request.args.get('source', 'bowling_ergebnisse.csv')
    print(f"DEBUG: Reloading data with source: {data_source}")
    
    try:
        data_manager = DataManager()
        # Force reload from session to ensure consistency across workers
        data_manager.force_reload_from_session()
        
        # Validate the requested source
        if not data_manager.validate_source(data_source):
            return {
                'success': False,
                'message': f'Invalid or inaccessible data source: {data_source}',
                'available_sources': data_manager.get_available_sources(),
                'sources_info': data_manager.get_sources_info()
            }, 400
        
        # Attempt to reload data
        success = data_manager.reload_data(data_source)
        
        if success:
            print(f"DEBUG: DataManager current source: {data_manager.current_source}")
            return {
                'success': True,
                'current_source': data_manager.current_source,
                'current_display_name': data_manager.get_source_display_name(data_manager.current_source),
                'message': f'Data source switched to {data_manager.get_source_display_name(data_manager.current_source)}',
                'available_sources': data_manager.get_available_sources(),
                'sources_info': data_manager.get_sources_info()
            }
        else:
            return {
                'success': False,
                'message': f'Failed to switch to {data_source}, rolled back to previous source',
                'current_source': data_manager.current_source,
                'current_display_name': data_manager.get_source_display_name(data_manager.current_source),
                'available_sources': data_manager.get_available_sources(),
                'sources_info': data_manager.get_sources_info()
            }, 500
            
    except Exception as e:
        print(f"ERROR: Exception in reload_data: {e}")
        return {
            'success': False,
            'message': f'Server error: {str(e)}',
            'available_sources': ['bowling_ergebnisse.csv', 'bowling_ergebnisse_real.csv']
        }, 500

@bp.route('/get-data-source')
def get_data_source():
    try:
        data_manager = DataManager()
        # Force reload from session to ensure consistency across workers
        data_manager.force_reload_from_session()
        return {
            'success': True,
            'current_source': data_manager.current_source,
            'current_display_name': data_manager.get_source_display_name(data_manager.current_source),
            'available_sources': data_manager.get_available_sources(),
            'sources_info': data_manager.get_sources_info()
        }
    except Exception as e:
        print(f"ERROR: Exception in get_data_source: {e}")
        return {
            'success': False,
            'current_source': 'bowling_ergebnisse.csv',
            'current_display_name': 'Simulated Data',
            'available_sources': ['bowling_ergebnisse.csv', 'bowling_ergebnisse_real.csv'],
            'message': f'Server error: {str(e)}'
        }, 500

@bp.route('/data-source-changed')
def data_source_changed():
    """Notify frontend that data source has changed"""
    try:
        data_manager = DataManager()
        return {
            'success': True,
            'current_source': data_manager.current_source,
            'current_display_name': data_manager.get_source_display_name(data_manager.current_source),
            'available_sources': data_manager.get_available_sources(),
            'sources_info': data_manager.get_sources_info(),
            'timestamp': datetime.datetime.now().isoformat()
        }
    except Exception as e:
        print(f"ERROR: Exception in data_source_changed: {e}")
        return {
            'success': False,
            'current_source': 'bowling_ergebnisse.csv',
            'current_display_name': 'Simulated Data',
            'message': f'Server error: {str(e)}'
        }, 500

@bp.route('/test')
def test():
    """Test page for API routes"""
    return render_template('test_new.html')

@bp.route('/database-test')
def database_test():
    """Test page for database switching functionality"""
    return render_template('database_test.html')

@bp.route('/debug-session')
def debug_session():
    """Debug endpoint to check session and data source status"""
    try:
        from flask import session
        data_manager = DataManager()
        
        debug_info = {
            'session_id': session.get('_id', 'No session ID'),
            'session_source': session.get('selected_database', 'No source in session'),
            'data_manager_source': data_manager.current_source,
            'data_loaded': data_manager.df is not None,
            'data_rows': len(data_manager.df) if data_manager.df is not None else 0,
            'available_sources': data_manager.get_available_sources(),
            'session_keys': list(session.keys())
        }
        
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': str(e.__traceback__)
        }), 500