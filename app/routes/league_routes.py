from flask import Blueprint, render_template, jsonify, request
from app.services.league_service import LeagueService
from data_access.schema import Columns, ColumnsExtra
from business_logic.statistics import query_database
from data_access.adapters.data_adapter_factory import DataAdapterSelector
import traceback

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

@bp.route('/league/get_table')
def get_table():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        #match_day should be int
        match_day = int(request.args.get('match_day'))
        
        print(f"Received request with: season={season}, league={league}, match_day={match_day}")
        
        if not season or not league:
            return jsonify({"error": "Season and league are required"}), 400

        #week_data = league_service.get_league_week(league=league, season=season, week=match_day)
        #print(f"Generated week data: {week_data}")

        league_table_data = league_service.get_league_standings_table(league=league, season=season, week=match_day)

        if not league_table_data:
            return jsonify({"message": "No data found for these filters"}), 404
        #print(jsonify(league_table_data))
        return jsonify(league_table_data)
    except Exception as e:
        import traceback
        print(f"Error in get_table: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")  # This will show the full error trace
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_available_matchdays')
def get_available_matchdays():
    try:
        season = request.args.get('season')
        league = request.args.get('league')
        
        if not season or not league:
            return jsonify({"error": "Season and league are required"}), 400
            
        filters = {
            Columns.season: season,
            Columns.league_name: league,
            Columns.input_data: True
        }
        
        # Get available match days for this combination
        #df_filtered = query_database(league_service.df, filters)
        available_matchdays = league_service.get_weeks()
        
        return jsonify({"matchdays": available_matchdays})
    except Exception as e:
        print(f"Error getting available match days: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/league/get_league_history')
def get_league_history():
    try:
        # Get query parameters
        print("GOTCHA!")
        season = request.args.get('season')
        league = request.args.get('league')
        week = request.args.get('week')
        
        if not all([season, league]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        week = int(week) if week is not None else 0
        
        # Use LeagueService
        table_data = league_service.get_league_history_table(
            league_name=league,
            season=season,
            week=week,
            depth=week,
            debug_output=True
        )

        transformed_data = {
            'headerGroups': [
                {'title': group[0], 'colspan': group[1]} 
                for group in table_data['headerGroups']
            ],
            'columns': [
                {'title': col, 'key': str(i)} 
                for i, col in enumerate(table_data['columns'])
            ],
            'data': [
                {str(i): value for i, value in enumerate(row)}
                for row in table_data['data']
            ],
            'rowNumbering': True
        }

        print(transformed_data)
        return jsonify(transformed_data)  # Make sure to jsonify the response
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

