from flask import Blueprint, render_template, session, redirect, url_for, request
from data_access.pd_dataframes import fetch_column
from app.services.data_manager import DataManager

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/set-season/<season>')
def set_season(season):
    session['selected_season'] = season
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/overall/<analysis>')
def overall_stats(analysis):
    season = session.get('selected_season', 'all')
    return render_template('overall.html', analysis=analysis, season=season)

@bp.route('/league/<analysis>')
def league_stats(analysis):
    season = session.get('selected_season', 'all')
    return render_template('league/stats.html', analysis=analysis, season=season)

@bp.route('/team/<analysis>')
def team_stats(analysis):
    season = session.get('selected_season', 'all')
    return render_template('team/stats.html', analysis=analysis, season=season)

@bp.route('/player/<analysis>')
def player_stats(analysis):
    season = session.get('selected_season', 'all')
    return render_template('player/content.html', analysis=analysis, season=season)

@bp.route('/reload-data')
def reload_data():
    data_source = request.args.get('source', 'bowling_ergebnisse.csv')
    print(f"DEBUG: Reloading data with source: {data_source}")
    data_manager = DataManager()
    data_manager.reload_data(data_source)
    print(f"DEBUG: DataManager current source: {data_manager.current_source}")
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/get-data-source')
def get_data_source():
    data_manager = DataManager()
    return {'current_source': data_manager.current_source}

@bp.route('/test')
def test():
    """Test page for API routes"""
    return render_template('test.html')