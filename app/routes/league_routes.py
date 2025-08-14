from flask import Blueprint, render_template, jsonify, request
from app.services.league_service import LeagueService
from data_access.schema import Columns, ColumnsExtra
from app.services.i18n_service import i18n_service, Language
from business_logic.statistics import query_database
from data_access.adapters.data_adapter_factory import DataAdapterSelector
import traceback
from app.services.data_dict import DataDict

bp = Blueprint('league', __name__)

def get_league_service():
    """Helper function to get LeagueService with database parameter"""
    database = request.args.get('database')
    print(f"🔄 get_league_service called with database: {database}")
    league_service = LeagueService(database=database)
    print(f"✅ LeagueService created with database: {getattr(league_service, 'database', 'None')}")
    return league_service

@bp.route('/league/stats')
def stats():
    try:
        league_service = get_league_service()
        weeks = league_service.get_weeks()
        print(f"Available weeks: {weeks}")  # Debug output
        return render_template('league/stats.html', 
                            season=league_service.get_seasons(),
                            league=league_service.get_leagues(),
                            week=weeks)
    except Exception as e:
        print(f"Error in stats route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_combinations')
def get_combinations():
    try:
        league_service = get_league_service()
        return jsonify(league_service.get_valid_combinations())
    except Exception as e:
        print(f"Error in get_combinations: {str(e)}")
        return jsonify({"error": str(e)}), 500


@bp.route('/league/get_available_weeks')
def get_available_weeks():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        
        if not season or not league:
            return jsonify({"error": "Season and league are required"}), 400
        
        league_service = get_league_service()
        weeks = league_service.get_weeks(league_name=league, season=season)
        return jsonify(weeks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_available_teams')
def get_available_teams():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        
        if not season or not league:
            return jsonify({"error": "Season and league are required"}), 400
        
        league_service = get_league_service()
        teams = league_service.get_teams_in_league_season(league, season)

        return jsonify(teams)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_league_history')
def get_league_history():
    try:
        # Get query parameters
        season = request.args.get('season')
        league = request.args.get('league')
        
        print(f"League History - Received request with: season={season}, league={league}")
        
        if not all([season, league]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Use the new method that returns TableData
        league_service = get_league_service()
        table_data = league_service.get_league_history_table_data(
            league_name=league,
            season=season
        )
        
        #print("::::::::::::::::::::::::::::")
        #print(table_data)
        #print("::::::::::::::::::::::::::::")
        
        # Convert to dictionary and return as JSON
        return jsonify(table_data.to_dict())
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_league_week_table')
def get_league_week_table():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        # week should be int
        week = int(request.args.get('week'))
        # print("get_league_week")
        print(f"🔄 League Standings - Received request with: season={season}, league={league}, week={week}")
        
        if not season or not league:
            return jsonify({"error": i18n_service.get_text("season_league_required")}), 400

        # Get the table data from the service
        # This now returns a TableData object
        league_service = get_league_service()
        print(f"✅ LeagueService created with database: {getattr(league_service, 'database', 'None')}")
        
        table_data = league_service.get_league_week_table_simple(season=season, league=league, week=week)
        print(f"✅ League week table data: {table_data.to_dict() if table_data else 'None'}")
        
        #print("############################")
        #print("league_routes.get_league_week_table: ", end="")
        #print(table_data)
        
        #print("############################")
        
        if not table_data:
            return jsonify({"message": "No data found for these filters"}), 404
        
        # Convert TableData to dictionary and return as JSON
        return jsonify(table_data.to_dict())
    except Exception as e:
        import traceback
        print(f"❌ Error in get_league_week: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")  # This will show the full error trace
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_team_week_details')
def get_team_week_details():
    
    season = request.args.get('season')
    week = request.args.get('week')
    team = request.args.get('team')
    league = request.args.get('league')
    
    print(f"Team Week Details - Received request with: season={season}, league={league}, week={week}, team={team}")

    week = int(request.args.get('week'))
    
    league_service = get_league_service()
    details = league_service.get_team_week_details(league, season, team, week)
    print(details)
    
    return jsonify({'config': details})

@bp.route('/league/get_team_week_details_table')
def get_team_week_details_table():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        week = int(request.args.get('week'))
        team = request.args.get('team')
        
        print(f"Team Week Details Table - Received request with: season={season}, league={league}, week={week}, team={team}")
        
        if not all([season, league, week, team]):
            return jsonify({'error': i18n_service.get_text('missing_parameters')}), 400
        
        # Get the table data from the service
        league_service = get_league_service()
        table_data = league_service.get_team_week_details_table_data(
            league=league, 
            season=season, 
            team=team,
            week=week
        )
        
        if not table_data:
            return jsonify({"message": "No data found for these filters"}), 404
        
        # Convert TableData to dictionary and return as JSON
        print(table_data)
        return jsonify(table_data.to_dict())
        
    except Exception as e:
        import traceback
        print(f"Error in get_team_week_details_table: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_team_week_head_to_head_table')
def get_team_week_head_to_head_table():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        week_str = request.args.get('week')
        team = request.args.get('team')
        view_mode = request.args.get('view_mode', 'own_team')
        
        print(f"Team Week Head-to-Head Table - Received request with: season={season}, league={league}, week={week_str}, team={team}, view_mode={view_mode}")
        
        if not all([season, league, week_str, team]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        week = int(week_str)
        
        # Get the table data from the service
        league_service = get_league_service()
        table_data = league_service.get_team_week_head_to_head_table_data(
            league=league, 
            season=season, 
            team=team, 
            week=week,
            view_mode=view_mode
        )
        
        if not table_data:
            return jsonify({"message": "No data found for these filters"}), 404
        
        # Convert TableData to dictionary and return as JSON
        print(table_data)
        return jsonify(table_data.to_dict())
        
    except Exception as e:
        import traceback
        print(f"Error in get_team_week_head_to_head_table: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_available_seasons')
def get_available_seasons():
    try:
        print(f"🔄 get_available_seasons called")
        league_service = get_league_service()
        print(f"✅ LeagueService created with database: {getattr(league_service, 'database', 'None')}")
        seasons = league_service.get_seasons()
        print(f"✅ Seasons retrieved: {seasons}")
        return jsonify(seasons)
    except Exception as e:
        print(f"❌ Error in get_available_seasons: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_available_leagues')
def get_available_leagues():
    try:
        season = request.args.get('season')
        print(f"🔄 get_available_leagues called with season: {season}")
        league_service = get_league_service()
        print(f"✅ LeagueService created with database: {getattr(league_service, 'database', 'None')}")
        leagues = league_service.get_leagues()
        print(f"✅ Leagues retrieved: {leagues}")
        return jsonify(leagues)
    except Exception as e:
        print(f"❌ Error in get_available_leagues: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_honor_scores')
def get_honor_scores():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        week = int(request.args.get('week'))
        
        print(f"🔄 Honor Scores - Received request with: league={league}, season={season}, week={week}")
        
        league_service = get_league_service()
        print(f"✅ LeagueService created with database: {getattr(league_service, 'database', 'None')}")
        
        honor_scores = league_service.get_honor_scores(
            league=league, 
            season=season, 
            week=week, 
            number_of_individual_scores=3, 
            number_of_team_scores=3, 
            number_of_individual_averages=3, 
            number_of_team_averages=3
        )
        
        print(f"✅ Honor scores data: {honor_scores}")
        return jsonify(honor_scores)
    except Exception as e:
        print(f"❌ Error in get_honor_scores: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_team_points')
def get_team_points():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
           

        print(f"Team Points - Received request with: season={season}, league={league}")
        if not all([season, league]):
            return jsonify({'error': i18n_service.get_text('missing_parameters')}), 400
            
        league_service = get_league_service()
        points = league_service.get_team_points_simple(
            league_name=league,
            season=season
        )
        
        #print(points)
        return jsonify(points)
        
    except Exception as e:
        print(f"Error in get_team_points: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500



@bp.route('/league/get_team_points_vs_average')
def get_team_points_vs_average():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
           

        print(f"Team Points vs Average - Received request with: season={season}, league={league}")
        if not all([season, league]):
            return jsonify({'error': i18n_service.get_text('missing_parameters')}), 400
            
        league_service = get_league_service()
        points_data = league_service.get_team_points_during_season(
            league_name=league,
            season=season
        )

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
       
        #print("############################")
        #print(points_vs_average)    
        #print("############################")
        return jsonify(points_vs_average)
        
    except Exception as e:
        print(f"Error in get_team_points_vs_average: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@bp.route('/get_latest_events')
def get_latest_events():
    try:
        # Get limit parameter with default value of 5
        limit = request.args.get('limit', default=10, type=int)
        
        print(f"Latest Events - Received request with limit={limit}")
        
        # Validate limit
        if limit <= 0:
            return jsonify({'error': 'Limit must be greater than 0'}), 400
            
        league_service = get_league_service()
        events = league_service.get_latest_events(limit=limit)
        #print("league_routes.get_latest_events")
        #print(events)
        print(f"Found {len(events)} latest events")
        return jsonify(events)
        
    except Exception as e:
        print(f"Error in get_latest_events: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_team_positions')
def get_team_positions():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
           

        print(f"Team Positions - Received request with: season={season}, league={league}")
        if not all([season, league]):
            return jsonify({'error': i18n_service.get_text('missing_parameters')}), 400
            
        league_service = get_league_service()
        positions = league_service.get_team_positions_simple(
            league_name=league,
            season=season
        )
        
        #print(positions)
        return jsonify(positions)
        
    except Exception as e:
        print(f"Error in get_team_positions: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_team_averages')
def get_team_averages():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        
        print(f"Team Averages - Received request with: season={season}, league={league}")

        if not all([season, league]):
            return jsonify({'error': i18n_service.get_text('missing_parameters')}), 400
            
        league_service = get_league_service()
        averages = league_service.get_team_averages_simple(
            league_name=league,
            season=season
        )
        #print(averages)
        return jsonify(averages)
        
    except Exception as e:
        print(f"Error in get_team_averages: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@bp.route('/league/set_language', methods=['POST'])
def set_language():
    """Set the current language"""
    try:
        data = request.get_json()
        language_code = data.get('language')
        
        if language_code == 'en':
            i18n_service.set_language(Language.ENGLISH)
        elif language_code == 'de':
            i18n_service.set_language(Language.GERMAN)
        else:
            return jsonify({"error": "Invalid language code"}), 400
        
        return jsonify({
            "success": True,
            "language": language_code,
            "available_languages": i18n_service.get_available_languages()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_translations')
def get_translations():
    """Get all translations for the current language"""
    try:
        return jsonify({
            "success": True,
            "current_language": i18n_service.get_current_language().value,
            "available_languages": i18n_service.get_available_languages(),
            "translations": {
                key: i18n_service.get_text(key) 
                for key in [
                    "points", "score", "average", "position", "team", "name", "week", "total",
                    "ranking", "opponent", "round", "league_standings", "league_history",
                    "team_week_details", "head_to_head", "match_day", "through_week",
                    "week_results", "total_until_week", "select_match_day", "loading_data",
                    "no_data_found", "error_loading_data", "missing_parameters",
                    "match_day_label", "position_label", "points_label", "average_label",
                    "position_progression", "points_progression", "average_progression",
                    "season_league_required", "no_data_available",
                    "league_statistics", "season", "league", "season_overview",
                    "position_in_season_progress", "points_in_season_progress",
                    "points_per_match_day", "position_per_match_day", "average_per_match_day",
                    "points_vs_average", "league_results_match_day", "honor_scores",
                    "top_individual_scores", "top_team_scores", "best_individual_averages",
                    "best_team_averages", "score_sheet_selected_team", "details",
                    "refresh_data", "please_select_combination", "please_select_match_day",
                    "please_select_team", "match_day_label", "match_day_format"
                ]
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@bp.route('/league/get_team_individual_scores_table')
def get_team_individual_scores_table():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        week_str = request.args.get('week')
        team = request.args.get('team')
        if not all([season, league, week_str, team]):
            return jsonify({'error': 'Missing required parameters'}), 400
        week = int(week_str)
        league_service = get_league_service()
        table_data = league_service.get_team_individual_scores_table(
            league=league,
            season=season,
            team=team,
            week=week
        )
        return jsonify(table_data.to_dict())
    except Exception as e:
        import traceback
        print(f"Error in get_team_individual_scores_table: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# ==========================================
# AGGREGATION ENDPOINTS (League-wide over time)
# ==========================================

@bp.route('/league/get_league_averages_history')
def get_league_averages_history():
    """Get league average scores across all seasons"""
    try:
        league = request.args.get('league')
        
        if not league:
            return jsonify({'error': 'Missing required parameter: league'}), 400
        
        print(f"League Averages History - Received request with: league={league}")
        
        debug = request.args.get('debug', 'false').lower() == 'true'
        league_service = get_league_service()
        data = league_service.get_league_averages_history(league=league, debug=debug)
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in get_league_averages_history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_points_to_win_history')
def get_points_to_win_history():
    """Get points needed to win the league across seasons"""
    try:
        league = request.args.get('league')
        
        if not league:
            return jsonify({'error': 'Missing required parameter: league'}), 400
        
        print(f"Points to Win History - Received request with: league={league}")
        
        debug = request.args.get('debug', 'false').lower() == 'true'
        league_service = get_league_service()
        data = league_service.get_points_to_win_history(league=league, debug=debug)
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in get_points_to_win_history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_top_team_performances')
def get_top_team_performances():
    """Get top team performances across all seasons"""
    try:
        league = request.args.get('league')
        
        if not league:
            return jsonify({'error': 'Missing required parameter: league'}), 400
        
        print(f"Top Team Performances - Received request with: league={league}")
        
        league_service = get_league_service()
        table_data = league_service.get_top_team_performances(league=league)
        return jsonify(table_data.to_dict())
        
    except Exception as e:
        print(f"Error in get_top_team_performances: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_top_individual_performances')
def get_top_individual_performances():
    """Get top individual performances across all seasons"""
    try:
        league = request.args.get('league')
        
        if not league:
            return jsonify({'error': 'Missing required parameter: league'}), 400
        
        print(f"Top Individual Performances - Received request with: league={league}")
        
        league_service = get_league_service()
        table_data = league_service.get_top_individual_performances(league=league)
        return jsonify(table_data.to_dict())
        
    except Exception as e:
        print(f"Error in get_top_individual_performances: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_record_games')
def get_record_games():
    """Get record games (highest scoring) across all seasons"""
    try:
        league = request.args.get('league')
        
        if not league:
            return jsonify({'error': 'Missing required parameter: league'}), 400
        
        print(f"Record Games - Received request with: league={league}")
        
        league_service = get_league_service()
        table_data = league_service.get_record_games(league=league)
        return jsonify(table_data.to_dict())
        
    except Exception as e:
        print(f"Error in get_record_games: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_record_individual_games')
def get_record_individual_games():
    """Get record individual games (highest scoring individual performances)"""
    try:
        league = request.args.get('league')
        
        if not league:
            return jsonify({'error': 'Missing required parameter: league'}), 400
        
        print(f"Record Individual Games - Received request with: league={league}")
        
        league_service = get_league_service()
        table_data = league_service.get_record_individual_games(league=league)
        return jsonify(table_data.to_dict())
        
    except Exception as e:
        print(f"Error in get_record_individual_games: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_record_team_games')
def get_record_team_games():
    """Get record team games (highest scoring team performances)"""
    try:
        league = request.args.get('league')
        
        if not league:
            return jsonify({'error': 'Missing required parameter: league'}), 400
        
        print(f"Record Team Games - Received request with: league={league}")
        
        league_service = get_league_service()
        table_data = league_service.get_record_team_games(league=league)
        return jsonify(table_data.to_dict())
        
    except Exception as e:
        print(f"Error in get_record_team_games: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==========================================
# SEASON ENDPOINTS (Season-specific data)
# ==========================================

@bp.route('/league/get_season_timetable')
def get_season_timetable():
    """Get season timetable with match day schedule"""
    try:
        league = request.args.get('league')
        season = request.args.get('season')
        
        if not all([league, season]):
            return jsonify({'error': 'Missing required parameters: league, season'}), 400
        
        print(f"Season Timetable - Received request with: league={league}, season={season}")
        
        league_service = get_league_service()
        data = league_service.get_season_timetable(league=league, season=season)
        return jsonify(data)
        
    except Exception as e:
        print(f"Error in get_season_timetable: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_individual_averages')
def get_individual_averages():
    """Get individual player averages for a season, optionally filtered by week and/or team"""
    try:
        league = request.args.get('league')
        season = request.args.get('season')
        week_str = request.args.get('week')  # Optional parameter
        team = request.args.get('team')  # Optional parameter
        
        if not all([league, season]):
            return jsonify({'error': 'Missing required parameters: league, season'}), 400
        
        # Parse week if provided
        week = None
        if week_str:
            try:
                week = int(week_str)
            except ValueError:
                return jsonify({'error': 'Invalid week parameter: must be an integer'}), 400
        
        filter_info = ""
        if week is not None:
            filter_info += f", week={week}"
        if team is not None:
            filter_info += f", team={team}"
        print(f"🔄 Individual Averages - Received request with: league={league}, season={season}{filter_info}")
        
        league_service = get_league_service()
        print(f"✅ LeagueService created with database: {getattr(league_service, 'database', 'None')}")
        table_data = league_service.get_individual_averages(league=league, season=season, week=week, team=team)
        print(f"✅ Individual averages data: {table_data.to_dict() if table_data else 'None'}")
        return jsonify(table_data.to_dict())
        
    except Exception as e:
        print(f"❌ Error in get_individual_averages: {str(e)}")
        return jsonify({'error': str(e)}), 500