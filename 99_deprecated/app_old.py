from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# CSV-Datei laden (dein Datenspeicher) mit dem Separator ";"
df = pd.read_csv('../database/data/bowling_ergebnisse.csv', sep=';')

@app.route('/', methods=['GET', 'POST'])
def index():
    # Alle möglichen Werte für Filteroptionen
    ligen = df['League Name'].unique()
    saisons = df['Season'].unique()
    teams = df['Team Name'].unique()
    spieler = df['Name'].unique()
    match_numbers = df['Match Number'].unique()
    opponents = df['Team Name Opponent'].unique()

    filtered_df = df.copy()
    aggregation_result = None
    match_averages = {}
    opponent_averages = {}

    if request.method == 'POST':
        liga = request.form.get('liga')
        saison = request.form.get('saison')
        team = request.form.get('team')
        spieler = request.form.get('spieler')
        aggregation = request.form.get('aggregation')

        # DataFrame nach den ausgewählten Filtern filtern
        if liga and liga != '':
            filtered_df = filtered_df[filtered_df['League Name'] == liga]
        if saison and saison != '':
            filtered_df = filtered_df[filtered_df['Season'] == saison]
        if team and team != '':
            filtered_df = filtered_df[filtered_df['Team Name'] == team]
        if spieler and spieler != '':
            filtered_df = filtered_df[filtered_df['Name'] == spieler]

        # Aggregation durchführen
        if aggregation == 'average':
            aggregation_result = round(filtered_df['Pins'].mean(), 2)
            for match in match_numbers:
                match_averages[match] = round(filtered_df[filtered_df['Match Number'] == match]['Pins'].mean(), 2)

            for opponent in opponents:
                avg = round(filtered_df[filtered_df['Team Name Opponent'] == opponent]['Pins'].mean(), 2)
                print(avg)
                if avg > 0:
                    opponent_averages[opponent] = avg

        # Aktualisiere die Dropdown-Werte nach den aktuellen Filtern
        ligen = filtered_df['League Name'].unique()
        saisons = filtered_df['Season'].unique()
        teams = filtered_df['Team Name'].unique()
        spieler = filtered_df['Name'].unique()

    return render_template('index_old.html', ligen=ligen, saisons=saisons, teams=teams, spieler=spieler, tables=filtered_df.to_html(classes='data', header="true", index=False), aggregation_result=aggregation_result, match_averages=match_averages, opponent_averages=opponent_averages)

@app.route('/filter', methods=['POST'])
def filter_data():
    filters = request.json
    filtered_df = df.copy()

    liga = filters.get('liga')
    saison = filters.get('saison')
    team = filters.get('team')
    spieler = filters.get('spieler')

    if liga:
        filtered_df = filtered_df[filtered_df['League Name'] == liga]
    if saison:
        filtered_df = filtered_df[filtered_df['Season'] == saison]
    if team:
        filtered_df = filtered_df[filtered_df['Team Name'] == team]
    if spieler:
        filtered_df = filtered_df[filtered_df['Name'] == spieler]

    ligen = filtered_df['League Name'].unique().tolist()
    saisons = filtered_df['Season'].unique().tolist()
    teams = filtered_df['Team Name'].unique().tolist()
    spieler = filtered_df['Name'].unique().tolist()

    return jsonify({
        'ligen': ligen,
        'saisons': saisons,
        'teams': teams,
        'spieler': spieler
    })

if __name__ == '__main__':
    app.run(debug=True)
