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

@bp.route('/impressum')
def impressum():
    """Impressum page - German legal requirement"""
    return render_template('impressum.html')

@bp.route('/switch-database', methods=['POST'])
def switch_database():
    """Switch database via AJAX"""
    try:
        from flask import request, jsonify
        from app.services.data_manager import DataManager
        from app.config.database_config import database_config
        
        data = request.get_json()
        database = data.get('database')
        
        print(f"🔄 Database switch request received: {database}")
        
        if not database:
            return jsonify({
                'success': False,
                'message': 'No database specified'
            }), 400
        
        # Validate the database exists
        if not database_config.validate_source(database):
            available = database_config.get_available_sources()
            return jsonify({
                'success': False,
                'message': f'Invalid database: {database}. Available: {available}'
            }), 400
        
        print(f"✅ Database {database} is valid, proceeding with switch")
        
        # Force the database switch
        data_manager = DataManager()
        success = data_manager.force_source(database)
        
        if success:
            print(f"✅ Successfully switched to {database}")
            return jsonify({
                'success': True,
                'message': f'Successfully switched to {database}',
                'database': database,
                'current_source': data_manager.current_source
            })
        else:
            print(f"❌ Failed to switch to {database}")
            return jsonify({
                'success': False,
                'message': f'Failed to switch to {database}'
            }), 400
            
    except Exception as e:
        print(f"❌ Error in switch_database: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error switching database: {str(e)}'
        }), 500

@bp.route('/get-data-sources-info')
def get_data_sources_info():
    try:
        # Get database parameter from request
        database = request.args.get('database')
        
        if database:
            # Use the specified database
            data_manager = DataManager()
            # Validate the database
            if not data_manager.validate_source(database):
                return {
                    'success': False,
                    'message': f'Invalid data source: {database}',
                    'available_sources': data_manager.get_available_sources()
                }, 400
            
            return {
                'success': True,
                'current_source': database,
                'current_display_name': data_manager.get_source_display_name(database),
                'available_sources': data_manager.get_available_sources(),
                'sources_info': data_manager.get_sources_info()
            }
        else:
            # Use current session-based approach, but reset to new default if needed
            data_manager = DataManager()
            # Check if session has old default and reset to new default
            session_source = data_manager._get_session_source()
            current_default = data_manager.get_default_source()
            if session_source != current_default:
                # Reset to new default
                data_manager.reset_to_default()
            else:
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
            'current_source': 'db_sim',
            'current_display_name': 'Simulated Data',
            'available_sources': ['db_sim', 'db_real'],
            'message': f'Server error: {str(e)}'
        }, 500

@bp.route('/reload-data')
def reload_data():
    data_source = request.args.get('source', 'db_sim')

    
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
            'available_sources': ['db_sim', 'db_real']
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
            'current_source': 'db_sim',
            'current_display_name': 'Simulated Data',
            'available_sources': ['db_sim', 'db_real'],
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
            'current_source': 'db_sim',
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

@bp.route('/test-database-param')
def test_database_param():
    """Test route to verify database parameter is passed correctly through all layers"""
    try:
        from app.config.database_config import database_config
        
        database = request.args.get('database')
    
        
        if not database:
            return jsonify({
                'success': False,
                'message': 'No database parameter provided'
            }), 400
        
        # Validate database exists
        if not database_config.validate_source(database):
            available = database_config.get_available_sources()
            return jsonify({
                'success': False,
                'message': f'Invalid database: {database}. Available: {available}'
            }), 400
        
        # Test the full chain: Route -> Service -> Server -> DataAdapterFactory -> DataAdapterPandas
        from app.services.league_service import LeagueService
        from business_logic.server import Server
        from data_access.adapters.data_adapter_factory import DataAdapterFactory, DataAdapterSelector
        

        
        # Test LeagueService
        league_service = LeagueService(database=database)
        
        # Test Server
        server = Server(database=database)
        
        # Test DataAdapterFactory
        adapter = DataAdapterFactory.create_adapter(DataAdapterSelector.PANDAS, database=database)
        
        # Get some basic data to verify it's working
        seasons = league_service.get_seasons()
        leagues = league_service.get_leagues()
        

        
        return jsonify({
            'success': True,
            'database': database,
            'seasons': seasons,
            'leagues': leagues,
            'available_sources': database_config.get_available_sources(),
            'message': 'Database parameter passed successfully through all layers'
        })
        
    except Exception as e:
        print(f"Error in test-database-param: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error testing database parameter: {str(e)}'
        }), 500

@bp.route('/test-filter-endpoints')
def test_filter_endpoints():
    """Test all filter endpoints to ensure they use database parameter"""
    try:
        from app.config.database_config import database_config
        
        database = request.args.get('database')
    
        
        if not database:
            return jsonify({
                'success': False,
                'message': 'No database parameter provided'
            }), 400
        
        # Test all filter endpoints
        from app.services.league_service import LeagueService
        league_service = LeagueService(database=database)
        
        # Test each endpoint
        results = {}
        
        # Test seasons
        try:
            seasons = league_service.get_seasons()
            results['seasons'] = {
                'success': True,
                'count': len(seasons),
                'data': seasons[:5]  # First 5 for brevity
            }
        except Exception as e:
            results['seasons'] = {
                'success': False,
                'error': str(e)
            }
        
        # Test leagues
        try:
            leagues = league_service.get_leagues()
            results['leagues'] = {
                'success': True,
                'count': len(leagues),
                'data': leagues[:5]  # First 5 for brevity
            }
        except Exception as e:
            results['leagues'] = {
                'success': False,
                'error': str(e)
            }
        
        # Test weeks (if we have a season and league)
        season = request.args.get('season')
        league = request.args.get('league')
        if season and league:
            try:
                weeks = league_service.get_weeks(league_name=league, season=season)
                results['weeks'] = {
                    'success': True,
                    'count': len(weeks),
                    'data': weeks[:5]  # First 5 for brevity
                }
            except Exception as e:
                results['weeks'] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Test teams (if we have a season and league)
        if season and league:
            try:
                teams = league_service.get_teams_in_league_season(league, season)
                results['teams'] = {
                    'success': True,
                    'count': len(teams),
                    'data': teams[:5]  # First 5 for brevity
                }
            except Exception as e:
                results['teams'] = {
                    'success': False,
                    'error': str(e)
                }
        
        # Test latest events
        try:
            events = league_service.get_latest_events(limit=3)
            results['latest_events'] = {
                'success': True,
                'count': len(events),
                'data': events
            }
        except Exception as e:
            results['latest_events'] = {
                'success': False,
                'error': str(e)
            }
        
        return jsonify({
            'success': True,
            'database': database,
            'results': results,
            'message': 'Filter endpoints tested successfully'
        })
        
    except Exception as e:
        print(f"Error in test-filter-endpoints: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error testing filter endpoints: {str(e)}'
        }), 500