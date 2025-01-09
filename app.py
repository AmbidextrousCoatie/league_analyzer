from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import plotly
import json

import sys
import os

#sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from data_access.read import read
from database.definitions import Columns
from business_logic.statistics import calculate_score_average_player, calculate_score_min_player, calculate_score_max_player, calculate_games_count_player, calculate_score_average_league
app = Flask(__name__, template_folder='html/templates')

# CSV-Datei laden (dein Datenspeicher) mit dem Separator ";"
df = pd.read_csv('database/data/bowling_ergebnisse.csv', sep=';')

@app.route('/', methods=['GET', 'POST'])
def index():
    # Alle möglichen Werte für Filteroptionen
    all_leagues = read(df, Columns.league_name, unique=True, as_list=True)
    all_seasons = read(df, Columns.season, unique=True, as_list=True)
    all_teams = read(df, Columns.team_name, unique=True, as_list=True)
    all_players = read(df, Columns.player_name, unique=True, as_list=True)

    filtered_df = df.copy()
    html_kpis = {}
    spieler_positionen = None
    player_avg_json = None
    heatmap_json = None
    heatmap_abweichung_json = None

    if request.method == 'POST':
        spieler = request.form.get('spieler')
        auswertungszeitraum = request.form.get('auswertungszeitraum')

        if auswertungszeitraum and auswertungszeitraum != 'gesamt':
            filtered_df = read(filtered_df, filters={Columns.season: auswertungszeitraum})

        html_kpis = {
            'pins_im_schnitt': calculate_score_average_player(filtered_df, spieler),
            'min_pins': calculate_score_min_player(filtered_df, spieler),
            'max_pins': calculate_score_max_player(filtered_df, spieler),
            'anzahl_spiele': calculate_games_count_player(filtered_df, spieler)
        }

        spieler_positionen = filtered_df.groupby('Position').size().to_dict()

        # Durchschnitt Pins des Spielers pro Woche im Verlauf
        player_avg = calculate_score_average_player(filtered_df, spieler, group_by=Columns.week)
        #player_avg = calculate_score_average_player(filtered_df, spieler, Columns.score, Columns.week)
        # Durchschnitt Pins der Liga pro Woche im Verlauf
        league_avg = calculate_score_average_league(filtered_df, Columns.score, Columns.week)

        player_avg_fig = px.line(player_avg, x='Week', y='Pins', title='Schnitt des Spielers über die Wochen', labels={'Pins': 'Durchschnittliche Pins'})
        league_avg_fig = px.line(league_avg, x='Week', y='Pins', title='Schnitt der Liga über die Wochen', labels={'Pins': 'Durchschnittliche Pins'})
        league_avg_fig.update_traces(name='Liga Schnitt', mode='lines')
        player_avg_fig.add_traces(league_avg_fig.data)

        player_avg_json = json.dumps(player_avg_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Heatmap: Durchschnittliche Pins pro Woche und Team
        if auswertungszeitraum and auswertungszeitraum != 'gesamt':
            heatmap_df = df[df['Season'] == auswertungszeitraum].groupby(['Team', 'Week', 'Spielort'])['Pins'].mean().reset_index()
        else:
            heatmap_df = df.groupby(['Team', 'Week', 'Spielort'])['Pins'].mean().reset_index()

        heatmap_fig = go.Figure(data=go.Heatmap(
            z=heatmap_df['Pins'],
            x=heatmap_df['Week'],
            y=heatmap_df['Team Name'],
            colorscale=[[0, 'red'], [0.5, 'yellow'], [0.75, 'green'], [1, 'blue']],
            colorbar={'title': 'Durchschnittliche Pins'},
        ))

        heatmap_fig.update_layout(
            title='Durchschnittliche Pins pro Woche und Team',
            xaxis=dict(title='Woche', tickmode='array', tickvals=heatmap_df['Week'].unique(), ticktext=heatmap_df['Spielort'].unique()),
            yaxis=dict(title='Team')
        )

        heatmap_json = json.dumps(heatmap_fig, cls=plotly.utils.PlotlyJSONEncoder)

        # Heatmap für die Abweichung des Teamschnitts in der Woche vom Saisondurchschnitt
        season_avg = df.groupby(['Team Name'])['Pins'].mean().reset_index()
        heatmap_abweichung_df = pd.merge(heatmap_df, season_avg, on='Team Name', suffixes=('_week', '_season'))
        heatmap_abweichung_df['Abweichung'] = heatmap_abweichung_df['Pins_week'] - heatmap_abweichung_df['Pins_season']

        heatmap_abweichung_fig = go.Figure(data=go.Heatmap(
            z=heatmap_abweichung_df['Abweichung'],
            x=heatmap_abweichung_df['Week'],
            y=heatmap_abweichung_df['Team Name'],
            colorscale=[[0, 'red'], [0.5, 'white'], [1, 'blue']],
            zmin=-15,
            zmax=15,
            colorbar={'title': 'Abweichung (Pins)'},
        ))

        heatmap_abweichung_fig.update_layout(
            title='Abweichung des Teamschnitts in der Woche vom Saisondurchschnitt',
            xaxis=dict(title='Woche', tickmode='array', tickvals=heatmap_abweichung_df['Week'].unique(), ticktext=heatmap_abweichung_df['Spielort'].unique()),
            yaxis=dict(title='Team')
        )

        heatmap_abweichung_json = json.dumps(heatmap_abweichung_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', ligen=all_leagues, saisons=all_seasons, teams=all_teams, spieler=all_players, html_kpis=html_kpis, spieler_positionen=spieler_positionen, player_avg_json=player_avg_json, heatmap_json=heatmap_json, heatmap_abweichung_json=heatmap_abweichung_json)

if __name__ == '__main__':
    app.run(debug=True)
