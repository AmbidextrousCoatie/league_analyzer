from flask import Blueprint, render_template, jsonify, request
from app.services.league_service import LeagueService

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
        match_day = request.args.get('match_day')
        
        print(f"Received request with: season={season}, league={league}, match_day={match_day}")
        
        if not season or not league:
            return jsonify({"error": "Season and league are required"}), 400
            
        table_data = league_service.get_table(season, league, match_day)
        #print(f"Generated table data: {table_data}")
        
        if not table_data:
            return jsonify({"message": "No data found for these filters"}), 404
            
        return jsonify(table_data)
    except Exception as e:
        import traceback
        print(f"Error in get_table: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")  # This will show the full error trace
        return jsonify({"error": str(e)}), 500

