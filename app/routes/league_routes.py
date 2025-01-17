from flask import Blueprint, render_template, jsonify, request
from app.services.league_service import LeagueService
from data_access.schema import Columns
from business_logic.statistics import query_database
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

        week_data = league_service.get_league_week(league=league, season=season, week=match_day)
        print(f"Generated week data: {week_data}")

        table_data = league_service.get_league_standings(league=league, season=season, week=match_day)
        print(f"Generated table data: {table_data}")
        
        if not table_data:
            return jsonify({"message": "No data found for these filters"}), 404
            
        return jsonify(table_data)
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

@bp.route('/league/get_position_history')
def get_position_history():
    result = {
        'matchDays': [],
        'teams': [],
        'data': []
    }
    return jsonify(result)
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
        
        # Get data for all match days
        df_filtered = query_database(league_service.df, filters)
        
        if df_filtered.empty:
            return jsonify({
                'matchDays': [],
                'teams': [],
                'data': []
            })
        
        match_days = [int(x) for x in sorted(df_filtered[Columns.week].unique())]
        teams = sorted(df_filtered['Team'].unique())
        print("-->" + str(teams))
        position_data = []
        for match_day in match_days:
            # Get standings for this match day using the existing service method
            standings = league_service.get_league_stanings(
                league_service.df,
                filters,
                match_day,
                cumulative=True,
                include_changes=False
            )
            
            # Sort standings by Points and Average (same as in calculate_standings)
            standings = standings.sort_values(['Points', 'Average'], ascending=[False, False])
            standings = standings.reset_index(drop=True)  # Reset index to get proper positions
            
            # Record position for each team
            for team in teams:
                team_data = standings[standings['Team'] == team]
                if not team_data.empty:
                    position = team_data.index[0] + 1  # Get position from sorted index
                    print(f"Match day {match_day}, {team}: Position {position}, Points {team_data['Points'].iloc[0]}")
                    position_data.append({
                        'matchDay': int(match_day),
                        'team': str(team),
                        'position': int(position)
                    })
        
        result = {
            'matchDays': match_days,
            'teams': [str(t) for t in teams],
            'data': position_data
        }
        return jsonify(result)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

