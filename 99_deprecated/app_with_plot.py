from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly.express as px
import plotly
import json

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

    filtered_df = df.copy()
    kpis = {}
    spieler_positionen = None
    player_avg_json = None

    if request.method == 'POST':
        spieler = request.form.get('spieler')
        auswertungszeitraum = request.form.get('auswertungszeitraum')

        if spieler and spieler != '':
            filtered_df = filtered_df[filtered_df['Name'] == spieler]

        if auswertungszeitraum and auswertungszeitraum != 'gesamt':
            filtered_df = filtered_df[filtered_df['Season'] == auswertungszeitraum]

        kpis = {
            'pins_im_schnitt': round(filtered_df['Pins'].mean(), 2),
            'min_pins': filtered_df['Pins'].min(),
            'max_pins': filtered_df['Pins'].max(),
            'anzahl_spiele': filtered_df.shape[0]
        }

        spieler_positionen = filtered_df.groupby('Position').size().to_dict()

        # Durchschnitt Pins des Spielers pro Woche im Verlauf
        player_avg = filtered_df.groupby('Week')['Pins'].mean().reset_index()
        # Durchschnitt Pins der Liga pro Woche im Verlauf
        league_avg = df[df['League Name'].isin(filtered_df['League Name'].unique())].groupby('Week')['Pins'].mean().reset_index()

        player_avg_fig = px.line(player_avg, x='Week', y='Pins', title='Schnitt des Spielers über die Wochen', labels={'Pins': 'Durchschnittliche Pins'})
        league_avg_fig = px.line(league_avg, x='Week', y='Pins', title='Schnitt der Liga über die Wochen', labels={'Pins': 'Durchschnittliche Pins'})
        league_avg_fig.update_traces(name='Liga Schnitt', mode='lines')
        player_avg_fig.add_traces(league_avg_fig.data)

        player_avg_json = json.dumps(player_avg_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html', ligen=ligen, saisons=saisons, teams=teams, spieler=spieler, kpis=kpis, spieler_positionen=spieler_positionen, player_avg_json=player_avg_json)

if __name__ == '__main__':
    app.run(debug=True)
