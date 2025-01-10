from flask import Blueprint, render_template, session, redirect, url_for, request
from app.services.player_service import PlayerService

bp = Blueprint('player', __name__, url_prefix='/player')
player_service = PlayerService()

@bp.route('/select')
def select():
    players = player_service.get_all_players()
    return render_template('player/select.html', players=players)

@bp.route('/select/<player_id>')
def select_player(player_id):
    session['selected_player'] = player_id
    return redirect(request.referrer)

@bp.route('/personal')
def personal_stats():
    player_id = session.get('selected_player')
    
    if not player_id:
        return redirect(url_for('player.select'))
    
    season = session.get('selected_season', 'all')
    stats = player_service.get_personal_stats(player_id, season)
    return render_template('player/personal.html', stats=stats)

@bp.route('/comparison')
def team_comparison():
    player_id = session.get('selected_player')
    season = session.get('selected_season', 'all')
    
    if not player_id:
        return redirect(url_for('player.select_player'))
    
    comparison = player_service.get_team_comparison(player_id, season)
    return render_template('player/comparison.html', comparison=comparison)

@bp.route('/historical')
def historical_data():
    player_id = session.get('selected_player')
    
    if not player_id:
        return redirect(url_for('player.select_player'))
    
    history = player_service.get_historical_data(player_id)
    return render_template('player/historical.html', history=history) 