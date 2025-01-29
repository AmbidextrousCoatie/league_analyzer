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
                            seasons=league_service.get_seasons(),
                            leagues=league_service.get_leagues(),
                            weeks=weeks)
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


@bp.route('/api/league/available_weeks')
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

@bp.route('/api/league/available_teams')
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
        # print("GOTCHA!")
        season = request.args.get('season')
        league = request.args.get('league')
        #week = request.args.get('week')
        
        #print(f"League History - Received request with: season={season}, league={league}, week={week}")
        print(f"League History - Received request with: season={season}, league={league}")
        


        if not all([season, league]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        #week = int(week) if week is not None else 0
        
        # Use LeagueService
        table_data = league_service.get_league_history_table(
            league_name=league,
            season=season,
            week=None,
            depth=None,
            debug_output=False
        )

        transformed_data = DataDict().transform_dict(table_data)

        # print(transformed_data.to_dict())
        return jsonify(transformed_data.to_dict())  # Make sure to jsonify the response
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/league/get_league_week')
def get_league_week():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        #week should be int
        week = int(request.args.get('week'))
        #print("get_league_week")
        print(f"League Standings - Received request with: season={season}, league={league}, week={week}")
        
        if not season or not league:
            return jsonify({"error": "Season and league are required"}), 400

        #week_data = league_service.get_league_week(league=league, season=season, week=week)
        #print(f"Generated week data: {week_data}")

        league_table_data = league_service.get_league_week_table(league=league, season=season, week=week)

        transformed_data = DataDict().transform_dict(league_table_data)
        #print(transformed_data)
        
        transformed_data.make_sortable([1,2,3,4,5,6])

        
        if not transformed_data:
            return jsonify({"message": "No data found for these filters"}), 404
        #print(jsonify(league_table_data))
        return jsonify(transformed_data.to_dict())
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

@bp.route('/api/league/available_seasons')
def get_available_seasons():
    try:
        seasons = league_service.get_seasons()
        return jsonify(seasons)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/league/available_leagues')
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
        
        return jsonify(averages)
        
    except Exception as e:
        print(f"Error in get_team_averages: {str(e)}")
        return jsonify({'error': str(e)}), 500