import pandas as pd

df = pd.read_csv('database/data/bowling_ergebnisse_reconstructed.csv', sep=';', dtype=str, keep_default_na=False)
players = df[(df['Season'] == '25/26') & (df['League'] == 'BayL') & (df['Week'] == '2') & (df['Team'] == 'BC EMAX Unterföhring 2') & (df['Player'] != 'Team Total')]

print('All BC EMAX Unterföhring 2 players, Week 2 (by Round Number):')
for rnd in sorted(players['Round Number'].unique()):
    rnd_players = players[players['Round Number'] == rnd]
    print(f'\nRound {rnd}:')
    print(rnd_players[['Round Number', 'Player', 'Score', 'Opponent']].to_string())
    print(f'Sum: {rnd_players["Score"].astype(int).sum()}')

print('\n\nTeam Total rows for BC EMAX Unterföhring 2, Week 2:')
team_totals = df[(df['Season'] == '25/26') & (df['League'] == 'BayL') & (df['Week'] == '2') & (df['Team'] == 'BC EMAX Unterföhring 2') & (df['Player'] == 'Team Total')]
print(team_totals[['Round Number', 'Opponent', 'Score', 'Points']].to_string())

