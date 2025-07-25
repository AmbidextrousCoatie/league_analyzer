from flask import Blueprint, render_template, request, jsonify
from app.services.team_service import TeamService

bp = Blueprint('team', __name__)

team_service=TeamService()

@bp.route('/team/stats')
def stats():
    return render_template('team/stats.html')

@bp.route('/team/get_teams')
def get_teams():
    try:

        teams = team_service.get_all_teams(
            league_name=None,
            season=None
        )
        return jsonify(teams)
        
    except Exception as e:
        print(f"Error in get_teams: {str(e)}")
        return jsonify({'error': str(e)}), 500 
    

@bp.route('/team/get_available_seasons')
def get_available_seasons():
    try:
        team_name = request.args.get('team_name')

        if not team_name:
            return jsonify({'error': 'Missing required parameters'}), 400

        print(f"Team Route: Get Available Seasons - Received request with: team_name={team_name}")

        return jsonify(team_service.get_available_seasons(team_name=team_name))
    except Exception as e:
        print(f"Error in get_available_seasons: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/team/get_available_weeks')
def get_available_weeks():
    try:
        team_name = request.args.get('team_name')
        season = request.args.get('season')

        if not all([team_name, season]):
            return jsonify({'error': 'Missing required parameters'}), 400

        print(f"Team Route: Get Available Weeks - Received request with: team_name={team_name}, season={season}")
        return jsonify(team_service.get_available_weeks(team_name=team_name, season=season))
    except Exception as e:
        print(f"Error in get_available_seasons: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/team/get_team_history')
def get_team_history():
    try:
        team_name = request.args.get('team_name')
        if not team_name:
            return jsonify({'error': 'Missing team_name parameter'}), 400
            
        # Example response structure:
        # {
        #     "18/19": {"league_name": "Liga A", "final_position": 3},
        #     "19/20": {"league_name": "Liga A", "final_position": 8},
        #     "20/21": {"league_name": "Liga B", "final_position": 1}
        # }
        history = team_service.get_team_history(team_name=team_name)

        return jsonify(history)
        

    except Exception as e:
        print(f"Error in get_team_history: {str(e)}")
        return jsonify({'error': str(e)}), 500





@bp.route('/team/get_special_matches')
def get_special_matches():
    try:
        team_name = request.args.get('team_name')
        if not team_name:
            return jsonify({'error': 'Missing team_name parameter'}), 400
        special_matches = team_service.get_special_matches(team_name=team_name)
        print(special_matches)
        return jsonify(special_matches)
    except Exception as e:
        print(f"Error in get_special_matches: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/team/get_league_comparison')
def get_league_comparison():
    try:
        team_name = request.args.get('team_name')
        if not team_name:
            return jsonify({'error': 'Missing team_name parameter'}), 400
        
        comparison_data = team_service.get_league_comparison_data(team_name=team_name)
        return jsonify(comparison_data)
    except Exception as e:
        print(f"Error in get_league_comparison: {str(e)}")
        return jsonify({'error': str(e)}), 500
