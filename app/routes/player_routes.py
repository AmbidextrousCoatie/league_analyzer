from flask import Blueprint, render_template, jsonify, request
from app.services.player_service import PlayerService

bp = Blueprint('player', __name__, url_prefix='/player')
player_service = PlayerService()

@bp.route('/stats')
def stats():
    return render_template('player/content.html')

@bp.route('/search')
def search_players():
    search_term = request.args.get('search', '')
    players = player_service.search_players(search_term)
    return jsonify(players)

@bp.route('/get-stats')
def get_stats():
    player_id = request.args.get('player_id')
    stats = player_service.get_personal_stats(player_id)
    return jsonify(stats)

@bp.route('/get_lifetime_stats')
def get_lifetime_stats():
   
    player_name = request.args.get('player_name')
    
    if not player_name:
        return jsonify({'error': 'Player name is required'}), 400
    
    print(f"Player Route: Get Lifetime Stats - Received request with: player_name={player_name}")
    
    stats = player_service.get_lifetime_stats(player_name)  # This will now return both lifetime and season stats
    
    return jsonify(stats)
