from flask import Blueprint, render_template, jsonify, request
from app.services.league_service import LeagueService
from data_access.schema import Columns, ColumnsExtra
from business_logic.statistics import query_database
from data_access.adapters.data_adapter_factory import DataAdapterSelector
import traceback
from app.services.data_dict import DataDict

bp = Blueprint('league', __name__)
league_service = LeagueService()

@bp.route('/league/stats')
def stats():
    try:
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
        table_data = league_service.get_league_history_table_data(
            league_name=league,
            season=season
        )
        
        print("::::::::::::::::::::::::::::")
        print(table_data)
        print("::::::::::::::::::::::::::::")
        
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
        print(f"League Standings - Received request with: season={season}, league={league}, week={week}")
        
        if not season or not league:
            return jsonify({"error": "Season and league are required"}), 400

        # Get the table data from the service
        # This now returns a TableData object
        table_data = league_service.get_league_week_table(season=season, league=league, week=week)
        
        print("############################")
        print("league_routes.get_league_week_table: ", end="")
        print(table_data)
        
        print("############################")
        
        if not table_data:
            return jsonify({"message": "No data found for these filters"}), 404
        
        # Convert TableData to dictionary and return as JSON
        return jsonify(table_data.to_dict())
    except Exception as e:
        import traceback
        print(f"Error in get_league_week: {str(e)}")
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
    
    details = league_service.get_team_week_details(league, season, team, week)
    
    return jsonify({'config': details})

@bp.route('/league/get_available_seasons')
def get_available_seasons():
    try:
        seasons = league_service.get_seasons()
        return jsonify(seasons)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_available_leagues')
def get_available_leagues():
    try:
        leagues = league_service.get_leagues()
        return jsonify(leagues)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_honor_scores')
def get_honor_scores():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        week = int(request.args.get('week'))
        
        honor_scores = league_service.get_honor_scores(
            league=league, 
            season=season, 
            week=week, 
            individual_scores=3, 
            team_scores=3, 
            indivdual_averages=3, 
            team_averages=3
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
            return jsonify({'error': 'Missing required parameters'}), 400
            
        points = league_service.get_team_points_during_season(
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
            return jsonify({'error': 'Missing required parameters'}), 400
            
        points_raw = league_service.get_team_points_during_season(
            league_name=league,
            season=season
        )["weekly"]

        averages_raw = league_service.get_team_averages_during_season(
            league_name=league,
            season=season
        )["averages"]
       
        #print(points_raw)
        #print(averages_raw)

        points_vs_average = dict()

        for team, points in points_raw.items():
            averages = averages_raw[team]
            points_vs_average[team] = [[averages[i] , points[i]] for i in range(len(points))]
       
        #print("############################")
        #print(points_vs_average)    
        #print("############################")
        return jsonify(points_vs_average)
        
    except Exception as e:
        print(f"Error in get_team_positions: {str(e)}")
        print(traceback.format_exc())

@bp.route('/get_latest_events')
def get_latest_events():
    try:
        # Get limit parameter with default value of 5
        limit = request.args.get('limit', default=10, type=int)
        
        print(f"Latest Events - Received request with limit={limit}")
        
        # Validate limit
        if limit <= 0:
            return jsonify({'error': 'Limit must be greater than 0'}), 400
            
        events = league_service.get_latest_events(limit=limit)
        print("league_routes.get_latest_events")
        print(events)
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
            return jsonify({'error': 'Missing required parameters'}), 400
            
        positions = league_service.get_team_positions_during_season(
            league_name=league,
            season=season
        )
        
        print(positions)
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
            return jsonify({'error': 'Missing required parameters'}), 400
            
        averages = league_service.get_team_averages_during_season(
            league_name=league,
            season=season
        )
        #print(averages)
        return jsonify(averages)
        
    except Exception as e:
        print(f"Error in get_team_averages: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500