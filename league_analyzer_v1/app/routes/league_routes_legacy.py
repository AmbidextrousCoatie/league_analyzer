"""
League Routes Legacy
Archived routes that are only used in test files or completely unused.
These routes are kept for backward compatibility during transition period.

DEPRECATED: These routes are not actively used in production frontend.
They are kept for:
- Reference during migration
- Testing purposes
- Backward compatibility during transition period

Routes in this file:
- get_combinations() - Completely unused in frontend
- get_team_week_details() - Replaced by get_team_week_details_table() in production
- get_team_points_vs_average() - Only used in test files, can be computed client-side
"""
import warnings
from flask import Blueprint, jsonify, request
from app.services.league_service import LeagueService
from app.services.league_service_legacy import LeagueServiceLegacy
from app.services.i18n_service import i18n_service
from app.config.debug_config import debug_config
import traceback
import sys

bp_legacy = Blueprint('league_legacy', __name__)

def get_league_service():
    """Helper function to get LeagueService with database parameter"""
    database = request.args.get('database') or 'db_real'
    debug_config.log_service('LeagueService', 'create', f"database={database}")
    return LeagueService(database=database)

def get_legacy_service():
    """Helper function to get LeagueServiceLegacy wrapper"""
    league_service = get_league_service()
    return LeagueServiceLegacy(league_service)

@bp_legacy.route('/league/get_combinations')
def get_combinations():
    """
    Get valid combinations of season, league, week, and team.
    
    DEPRECATED: This route is not used anywhere in the frontend.
    Consider removing if not needed for testing or future features.
    """
    warnings.warn(
        "Route /league/get_combinations is deprecated and unused in production frontend.",
        DeprecationWarning,
        stacklevel=2
    )
    
    try:
        legacy_service = get_legacy_service()
        return jsonify(legacy_service.get_valid_combinations())
    except Exception as e:
        print(f"Error in get_combinations: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp_legacy.route('/league/get_team_week_details')
def get_team_week_details():
    """
    Get team week details in legacy format.
    
    DEPRECATED: This route has been replaced by /league/get_team_week_details_table
    which returns TableData instead of a config dictionary.
    Only used in test files (app/templates/test/league_tests.html).
    """
    warnings.warn(
        "Route /league/get_team_week_details is deprecated. "
        "Use /league/get_team_week_details_table instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    season = request.args.get('season')
    week = request.args.get('week')
    team = request.args.get('team')
    league = request.args.get('league')
    
    print(f"Team Week Details - Received request with: season={season}, league={league}, week={week}, team={team}")

    week = int(request.args.get('week'))
    
    legacy_service = get_legacy_service()
    details = legacy_service.get_team_week_details(league, season, team, week)
    print(details)
    
    return jsonify({'config': details})

@bp_legacy.route('/league/get_team_points_vs_average')
def get_team_points_vs_average():
    """
    Get team points vs average comparison data.
    
    DEPRECATED: This route is only used in test files.
    The same data can be computed client-side by combining:
    - /league/get_team_points
    - /league/get_team_averages
    """
    warnings.warn(
        "Route /league/get_team_points_vs_average is deprecated and only used in test files. "
        "Consider computing this client-side using get_team_points and get_team_averages.",
        DeprecationWarning,
        stacklevel=2
    )
    
    try:
        season = request.args.get('season')
        league = request.args.get('league')
           

        print(f"Team Points vs Average - Received request with: season={season}, league={league}")
        if not all([season, league]):
            return jsonify({'error': i18n_service.get_text('missing_parameters')}), 400
            
        legacy_service = get_legacy_service()
        points_data = legacy_service.get_team_points_during_season(
            league_name=league,
            season=season
        )

        league_service = get_league_service()
        averages_data = league_service.get_team_averages_simple(
            league_name=league,
            season=season
        )
       
        # Extract data from the new SeriesData structure
        points_raw = points_data["data"]
        averages_raw = averages_data["data"]

        points_vs_average = dict()

        for team, points in points_raw.items():
            averages = averages_raw[team]
            points_vs_average[team] = [[averages[i] , points[i]] for i in range(len(points))]
       
        return jsonify(points_vs_average)
        
    except Exception as e:
        print(f"Error in get_team_points_vs_average: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
