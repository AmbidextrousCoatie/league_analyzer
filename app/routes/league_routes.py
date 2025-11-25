from flask import Blueprint, render_template, jsonify, request
from app.services.league_service import LeagueService
from data_access.schema import Columns, ColumnsExtra
from app.services.i18n_service import i18n_service, Language
from business_logic.statistics import query_database
from data_access.adapters.data_adapter_factory import DataAdapterSelector
import traceback
import sys
from app.services.data_dict import DataDict
from app.config.debug_config import debug_config
from app.models.table_data import TableData, ColumnGroup, Column
from business_logic.league import longNames

bp = Blueprint('league', __name__)

def get_league_service():
    """Helper function to get LeagueService with database parameter"""
    database = request.args.get('database') or 'db_real'  # Default to db_real if no database specified
    debug_config.log_service('LeagueService', 'create', f"database={database}")
    return LeagueService(database=database)

@bp.route('/league/funsies')
def funsies():
    return render_template('funsies.html')

@bp.route('/league/stats')
def stats():
    try:
        params = dict(request.args)
        debug_config.log_route('league.stats', params)
        
        league_service = get_league_service()
        weeks = league_service.get_weeks()
        return render_template('league/stats.html', 
                            season=league_service.get_seasons(),
                            league=league_service.get_leagues(),
                            week=weeks)
    except Exception as e:
        debug_config.log_route('league.stats', params, f"ERROR: {str(e)}")
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

@bp.route('/league/get_available_rounds')
def get_available_rounds():
    try:
        params = dict(request.args)
        debug_config.log_route('league.get_available_rounds', params)
        
        season = request.args.get('season')
        league = request.args.get('league')
        week = request.args.get('week')
        
        if not all([season, league, week]):
            return jsonify({"error": "Season, league, and week are required"}), 400
        
        try:
            week = int(week)
        except ValueError:
            return jsonify({"error": "Week must be a valid integer"}), 400
        
        league_service = get_league_service()
        rounds = league_service.get_available_rounds(season=season, league=league, week=week)
        
        response_size = sys.getsizeof(str(rounds))
        debug_config.log_route('league.get_available_rounds', params, response_size)
        
        return jsonify(rounds)
    except Exception as e:
        debug_config.log_route('league.get_available_rounds', dict(request.args), f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_game_overview')
def get_game_overview():
    try:
        params = dict(request.args)
        debug_config.log_route('league.get_game_overview', params)
        
        season = request.args.get('season')
        league = request.args.get('league')
        week = request.args.get('week')
        round_number = request.args.get('round')
        
        if not all([season, league, week, round_number]):
            return jsonify({"error": "Season, league, week, and round are required"}), 400
        
        try:
            week = int(week)
            round_number = int(round_number)
        except ValueError:
            return jsonify({"error": "Week and round must be valid integers"}), 400
        
        league_service = get_league_service()
        table_data = league_service.get_game_overview_data(
            season=season,
            league=league,
            week=week,
            round_number=round_number
        )
        
        response_data = table_data.to_dict()
        response_size = sys.getsizeof(str(response_data))
        debug_config.log_route('league.get_game_overview', params, response_size)
        
        return jsonify(response_data)
    except Exception as e:
        debug_config.log_route('league.get_game_overview', dict(request.args), f"ERROR: {str(e)}")
        if debug_config.is_debug_enabled('routes'):
            traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_game_team_details')
def get_game_team_details():
    try:
        params = dict(request.args)
        debug_config.log_route('league.get_game_team_details', params)
        
        season = request.args.get('season')
        league = request.args.get('league')
        week = request.args.get('week')
        team = request.args.get('team')
        round_number = request.args.get('round')
        
        if not all([season, league, week, team, round_number]):
            return jsonify({"error": "Season, league, week, team, and round are required"}), 400
        
        try:
            week = int(week)
            round_number = int(round_number)
        except ValueError:
            return jsonify({"error": "Week and round must be valid integers"}), 400
        
        league_service = get_league_service()
        table_data = league_service.get_game_team_details_data(
            season=season,
            league=league,
            week=week,
            team=team,
            round_number=round_number
        )
        
        response_data = table_data.to_dict()
        response_size = sys.getsizeof(str(response_data))
        debug_config.log_route('league.get_game_team_details', params, response_size)
        
        return jsonify(response_data)
    except Exception as e:
        debug_config.log_route('league.get_game_team_details', dict(request.args), f"ERROR: {str(e)}")
        if debug_config.is_debug_enabled('routes'):
            traceback.print_exc()
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
        params = dict(request.args)
        debug_config.log_route('league.get_league_history', params)
        
        season = request.args.get('season')
        league = request.args.get('league')
        
        if not all([season, league]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        league_service = get_league_service()
        table_data = league_service.get_league_history_table_data(
            league_name=league,
            season=season
        )
        
        response_data = table_data.to_dict()
        response_size = sys.getsizeof(str(response_data))
        debug_config.log_route('league.get_league_history', params, response_size)
        
        return jsonify(response_data)
        
    except Exception as e:
        debug_config.log_route('league.get_league_history', dict(request.args), f"ERROR: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_league_week_table')
def get_league_week_table():
    try:
        params = dict(request.args)
        debug_config.log_route('league.get_league_week_table', params)
        
        season = request.args.get('season')
        league = request.args.get('league')
        week = int(request.args.get('week'))
        
        if not season or not league:
            return jsonify({"error": i18n_service.get_text("season_league_required")}), 400

        league_service = get_league_service()
        table_data = league_service.get_league_week_table_simple(season=season, league=league, week=week)
        
        if not table_data:
            return jsonify({"message": "No data found for these filters"}), 404
        
        response_data = table_data.to_dict()
        response_size = sys.getsizeof(str(response_data))
        debug_config.log_route('league.get_league_week_table', params, response_size)
        
        return jsonify(response_data)
    except Exception as e:
        debug_config.log_route('league.get_league_week_table', dict(request.args), f"ERROR: {str(e)}")
        if debug_config.is_debug_enabled('routes'):
            traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_season_league_standings')
def get_season_league_standings():
    try:
        params = dict(request.args)
        debug_config.log_route('league.get_season_league_standings', params)
        
        season = request.args.get('season')
        
        if not season:
            return jsonify({"error": i18n_service.get_text("season_required")}), 400

        league_service = get_league_service()
        standings_data = league_service.get_season_league_standings(season=season)
        
        if not standings_data:
            return jsonify({"message": "No data found for this season"}), 404
        
        response_size = sys.getsizeof(str(standings_data))
        debug_config.log_route('league.get_season_league_standings', params, response_size)
        
        return jsonify(standings_data)
    except Exception as e:
        debug_config.log_route('league.get_season_league_standings', dict(request.args), f"ERROR: {str(e)}")
        if debug_config.is_debug_enabled('routes'):
            traceback.print_exc()
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
        return jsonify(table_data.to_dict())
        
    except Exception as e:
        import traceback
        print(f"Error in get_team_week_head_to_head_table: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_available_seasons')
def get_available_seasons():
    try:
        params = dict(request.args)
        debug_config.log_route('league.get_available_seasons', params)
        
        league = request.args.get('league')
        team = request.args.get('team')
        #print(f"####################### route get_available_seassons - league_name: {league} and team_name: {team}")
        league_service = get_league_service()
        seasons = league_service.get_seasons(league_name=league, team_name=team)
        
        response_size = sys.getsizeof(str(seasons))
        debug_config.log_route('league.get_available_seasons', params, response_size)
        
        return jsonify(seasons)
    except Exception as e:
        debug_config.log_route('league.get_available_seasons', dict(request.args), f"ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_available_leagues')
def get_available_leagues():
    try:
        season = request.args.get('season')
    
        league_service = get_league_service()
        leagues = league_service.get_leagues()
        enriched_leagues = [
            {
                "short_name": league,
                "long_name": longNames.get(league, league),
                "value": league
            }
            for league in leagues
        ]
        return jsonify(enriched_leagues)
    except Exception as e:
        print(f"Error in get_available_leagues: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_honor_scores')
def get_honor_scores():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        week = int(request.args.get('week'))
        

        
        league_service = get_league_service()
        
        honor_scores = league_service.get_honor_scores(
            league=league, 
            season=season, 
            week=week, 
            number_of_individual_scores=3, 
            number_of_team_scores=3, 
            number_of_individual_averages=3, 
            number_of_team_averages=3
        )
        

        return jsonify(honor_scores)
    except Exception as e:
        print(f"Error in get_honor_scores: {str(e)}")
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
        params = dict(request.args)
        debug_config.log_route('league.get_latest_events', params)
        
        limit = request.args.get('limit', default=10, type=int)
        
        if limit <= 0:
            return jsonify({'error': 'Limit must be greater than 0'}), 400
            
        league_service = get_league_service()
        events = league_service.get_latest_events(limit=limit)
        
        response_size = sys.getsizeof(str(events))
        debug_config.log_route('league.get_latest_events', params, response_size)
        
        return jsonify(events)
        
    except Exception as e:
        debug_config.log_route('league.get_latest_events', dict(request.args), f"ERROR: {str(e)}")
        if debug_config.is_debug_enabled('routes'):
            traceback.print_exc()
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
            "translations_version": i18n_service.get_translations_version(),
            "translations": {
                key: i18n_service.get_text(key) 
                for key in [
                    # Common table headers
                    "points", "score", "average", "position", "team", "name", "week", "total",
                    "ranking", "opponent", "round", "pins", "avg", "games", "high_game",
                    "location", "status", "date", "player", "season", "league",
                    
                    # Table titles and descriptions
                    "league_standings", "league_history", "team_week_details", "head_to_head", 
                    "match_day", "through_week", "week_results", "total_until_week",
                    "match_info", "match", "total_points", "team_performance", "season_timetable",
                    "individual_averages", "individual_performance", "record_individual_games", 
                    "record_team_games", "team_vs_team_comparison_matrix",
                    
                    # Navigation and UI
                    "select_match_day", "loading_data", "no_data_found", "error_loading_data", 
                    "missing_parameters", "no_data", "no_league_data_available",
                    "no_data_available_for", "no_timetable_available", "no_individual_data_available",
                    "no_data_available_for_team_week",
                    
                    # Chart labels
                    "match_day_label", "position_label", "points_label", "average_label",
                    "position_progression", "points_progression", "average_progression",
                    "cumulative_points",
                    
                    # Error messages
                    "season_league_required", "no_data_available", "error_loading_timetable",
                    "error_loading_individual_averages", "error_loading_individual_record_games",
                    "error_loading_team_record_games", "error_loading_data_for",
                    
                    # Language names
                    "english", "german",
                    
                    # Card headers and UI elements
                    "league_statistics", "season_overview", "position_in_season_progress", 
                    "points_in_season_progress", "points_per_match_day", "position_per_match_day", 
                    "average_per_match_day", "points_vs_average", "league_results_match_day", 
                    "honor_scores", "top_individual_scores", "top_team_scores", 
                    "best_individual_averages", "best_team_averages", "score_sheet_selected_team", 
                    "details", "refresh_data", "please_select_combination", "please_select_match_day",
                    "please_select_team", "match_day_format",
                    
                    # Additional UI elements
                    "league_leader", "league_average", "pins_per_game", "weeks_completed",
                    "through_week", "game", "score_sheet_for", "history", "top_team_performances",
                    "venue", "match_schedule", "top_individual_performances", "individual_scores",
                    "all_individual_scores_for", "view", "own_team", "standings", 
                    "win_percentage", "performance", "average_scores_and_match_points_between_teams",
                    "week", "season",

                    # Namespaced: UI languages
                    "ui.language.english", "ui.language.german",

                    # Namespaced: actions and status
                    "action.refresh", "action.update", "action.dismiss",
                    "status.loading", "status.loading_data", "status.no_data",
                    "status.initialization_error.title", "status.initialization_error.message",
                    # Initialization placeholders on league page
                    "status.initializing.season_league_standings", "status.initializing.league_aggregation",
                    "status.initializing.league_season_overview", "status.initializing.season_overview",
                    "status.initializing.matchday", "status.initializing.team_details",
                    "status.initializing.team_performance", "status.initializing.team_win_percentage",

                    # Namespaced: table headers
                    "table.header.points", "table.header.score", "table.header.average",
                    "table.header.position", "table.header.team", "table.header.name",
                    "table.header.week", "table.header.total", "table.header.ranking",
                    "table.header.opponent", "table.header.round",

                    # Namespaced: blocks
                    "block.matchday.title", "block.team_performance.title", "block.team_details.title",
                    "block.team_details.view.classic", "block.team_details.view.new",
                    "block.clutch_analysis.title", "block.clutch_analysis.description",
                    "block.consistency_metrics.title", "block.consistency_metrics.description",
                    "block.special_matches.title", "block.special_matches.description",

                    # Namespaced: messages
                    "msg.please_select.match_day", "msg.please_select.season_league", "msg.please_select.team",

                    # Namespaced: Clutch Analysis UI
                    "ui.clutch.threshold", "ui.clutch.points", "ui.clutch.title", "ui.clutch.total_games",
                    "ui.clutch.clutch_games", "ui.clutch.clutch_wins", "ui.clutch.win_percentage",
                    "ui.clutch.try_different", "ui.clutch.stats_placeholder", "ui.clutch.margin",

                    # Namespaced: Consistency Metrics UI
                    "ui.consistency.basic_stats", "ui.consistency.score_range", "ui.consistency.description",

                    # Namespaced: Win Percentage UI
                    "ui.win_percentage.title", "ui.win_percentage.description", "ui.win_percentage.individual",
                    "ui.win_percentage.individual_desc", "ui.win_percentage.trends", "ui.win_percentage.trends_desc",
                    "ui.win_percentage.player", "ui.win_percentage.weekly", "ui.win_percentage.totals",
                    "ui.win_percentage.total_wins", "ui.win_percentage.total_matches", "ui.win_percentage.win_percentage",

                    # Namespaced: League Aggregation/Overview UI
                    "ui.league.aggregation.title", "ui.league.all_time", "ui.league.performance_all_seasons",
                    "ui.league.averages_over_time", "ui.league.points_to_win", "ui.league.season_overview.title",

                    # Namespaced: League Comparison / Heatmap / Team-vs-Team
                    "ui.league_comparison.title", "ui.league_comparison.description", "ui.league_comparison.chart_title",
                    "ui.league_comparison.loading", "ui.league_comparison.loading_table", "ui.league_comparison.table_placeholder",
                    "ui.comparison.difference", "ui.team_vs_team.description", "ui.heatmap.legend",
                    "ui.heatmap.score", "ui.heatmap.points", "ui.heatmap.low", "ui.heatmap.high", "ui.range_label",

                    # Namespaced: Team Performance UI
                    "ui.team_performance.title", "ui.team_performance.description", "ui.team_performance.individual",
                    "ui.team_performance.individual_desc", "ui.team_performance.trends", "ui.team_performance.trends_desc",
                    "ui.team_performance.player_performance", "ui.team_performance.player_perf_desc",
                    "ui.team_performance.weekly_avg_game", "ui.team_performance.total_score", "ui.team_performance.avg_per_game",

                    # Namespaced: Team History UI
                    "ui.team_history.title", "ui.team_history.description", "ui.team_history.chart_title",
                    "ui.team_history.loading", "ui.team_history.tooltip.league", "ui.team_history.tooltip.final_position"
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

@bp.route('/league/get_team_analysis')
def get_team_analysis():
    """Get detailed team analysis including individual player performance and win percentages"""
    try:
        league = request.args.get('league')
        season = request.args.get('season')
        team = request.args.get('team')
        
        if not all([league, season, team]):
            return jsonify({'error': 'Missing required parameters: league, season, team'}), 400
        
        print(f"Team Analysis - Received request with: league={league}, season={season}, team={team}")
        
        league_service = get_league_service()
        analysis_data = league_service.get_team_analysis(league=league, season=season, team=team)
        return jsonify(analysis_data)
        
    except Exception as e:
        print(f"Error in get_team_analysis: {str(e)}")
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
        league_service = get_league_service()
        table_data = league_service.get_individual_averages(league=league, season=season, week=week, team=team)

        return jsonify(table_data.to_dict())
        
    except Exception as e:
        print(f"Error in get_individual_averages: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_team_vs_team_comparison')
def get_team_vs_team_comparison():
    """Get team vs team comparison matrix with heat map data"""
    try:
        league = request.args.get('league')
        season = request.args.get('season')
        week = request.args.get('week')
        
        if not league or not season:
            return jsonify({'error': 'League and season are required'}), 400
        
        # Convert week to int if provided
        week_int = None
        if week:
            try:
                week_int = int(week)
            except ValueError:
                return jsonify({'error': 'Invalid week parameter'}), 400
        
        # Get league service and fetch real data
        league_service = get_league_service()
        table_data = league_service.get_team_vs_team_comparison_table(league, season, week_int)
        
        return jsonify(table_data.to_dict())
        
    except Exception as e:
        print(f"Error in get_team_vs_team_comparison: {str(e)}")
        return jsonify({'error': str(e)}), 500
