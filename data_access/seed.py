import random

import numpy as np
import pandas as pd

from business_logic.lib import get_round_robin_pairings
from business_logic.team import Team
from business_logic.player import Player
from business_logic.league import League

from database.definitions import Columns


def get_random_city():
    cities_bavaria = ['München', 'Nürnberg', 'Augsburg', 'Regensburg', 'Ingolstadt', 'Würzburg', 'Fürth', 'Erlangen',
                      'Bayreuth', 'Bamberg', 'Aschaffenburg', 'Landshut', 'Kempten', 'Rosenheim', 'Schweinfurt',
                      'Neu-Ulm', 'Passau', 'Straubing', 'Hof', 'Weiden in der Oberpfalz']

    return random.choice(cities_bavaria)


def create_random_player(league_skill):

    return Player(get_random_id(), get_random_first_name(), get_random_last_name(), get_random_skill(league_skill))


def create_league_roster(league: League):
    league.teams = [create_team(league.skill, league.number_of_players_per_team) for i in range(league.number_of_teams)]
    return league


def create_team(league_skill, players_per_team=4):
    home_alley = get_random_city()
    team_name = get_random_team_name(team_city=home_alley)
    players = [create_random_player(league_skill) for i in range(players_per_team)]
    return Team(team_name, players, home_alley)


def get_random_last_name():
    pool_of_last_names = [
    # Deutsche Nachnamen (70)
    'Müller', 'Schmidt', 'Schneider', 'Fischer', 'Weber', 'Meyer', 'Wagner', 'Becker', 'Schulz', 'Hoffmann',
    'Schäfer', 'Koch', 'Bauer', 'Richter', 'Klein', 'Wolf', 'Schröder', 'Neumann', 'Schwarz', 'Braun',
    'Zimmermann', 'Schmitt', 'Hartmann', 'Krüger', 'Werner', 'Lange', 'Krause', 'Lehmann', 'Schmid', 'Maier',
    'Köhler', 'Herrmann', 'Walter', 'König', 'Mayer', 'Huber', 'Kaiser', 'Fuchs', 'Peters', 'Lang',
    'Scholz', 'Möller', 'Weiß', 'Jung', 'Hahn', 'Keller', 'Hoffmann', 'Schmitz', 'Kraus', 'Meier',
    'Kurz', 'Busch', 'Friedrich', 'Jäger', 'Becker', 'Günther', 'Bergmann', 'Böhm', 'Pohl', 'Roth',
    'Frank', 'Albrecht', 'Ludwig', 'Stark', 'Horn', 'Lorenz', 'Dietrich', 'Vogel', 'Riedel', 'Heil',

    # Amerikanische Nachnamen (20)
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
    'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',

    # Internationale Nachnamen (10)
    'Nguyen', 'Kim', 'Singh', 'Ali', 'Silva', 'Haddad', 'Chen', 'Garcia', 'Rossi', 'Sousa'
    ]

    return pool_of_last_names[random.randint(0, 99)]


def get_random_first_name():

    pool_of_first_names = [
        # Deutsche Vornamen (70)
        'Leon', 'Paul', 'Jonas', 'Ben', 'Elias', 'Finn', 'Noah', 'Lukas', 'Tim', 'Max',
        'Niklas', 'Julian', 'Jakob', 'Moritz', 'Felix', 'Tom', 'Philipp', 'David', 'Theo', 'Kilian',
        'Anton', 'Emil', 'Linus', 'Samuel', 'Leo', 'Julius', 'Carl', 'Henry', 'Finn', 'Lars',
        'Kevin', 'Simon', 'Dominik', 'Bastian', 'Tobias', 'Florian', 'Andreas', 'Martin', 'Stefan', 'Alexander',
        'Oliver', 'Christoph', 'Matthias', 'Daniel', 'Jan', 'Michael', 'Patrick', 'Robert', 'Thomas', 'Johannes',
        'Christian', 'Peter', 'Lukas', 'Markus', 'Sven', 'Max', 'Leonhard', 'Fabian', 'Sebastian', 'Marco',
        'Adrian', 'Arthur', 'Benjamin', 'Eric', 'Georg', 'Heinz', 'Konstantin', 'Ludwig', 'Oscar', 'Vincent',

        # Amerikanische Vornamen (20)
        'Liam', 'William', 'James', 'Logan', 'Mason', 'Ethan', 'Alexander', 'Henry', 'Jackson', 'Sebastian',
        'Michael', 'Joshua', 'Matthew', 'Joseph', 'Daniel', 'Christopher', 'Andrew', 'David', 'John', 'Ryan',

        # Internationale Vornamen (10)
        'Mohammad', 'Hiroshi', 'Diego', 'Luca', 'Matteo', 'Ahmed', 'Ivan', 'Youssef', 'Omar', 'Juan'
    ]

    return pool_of_first_names[random.randint(0, 99)]


def get_random_id(limit_low=10000, limit_high=99999):

    return random.randint(limit_low, limit_high)


def get_random_skill(league_skill):
    skill_low = 0
    skill_high = 10

    if league_skill - 2 > skill_low:
        skill_low = league_skill - 2
    if league_skill + 2 < skill_high:
        skill_high = league_skill + 2

    return random.randint(skill_low*10, skill_high*10) / 10.0


def get_random_team_name(team_city=None, team_number=None):

    if team_city is None:
        team_city = get_random_city()

    if team_number is None:
        team_number = random.randint(1, 99)

    return team_city + " " + str(team_number)


def get_random_alley(teams, week):
    if len(teams) >= week:
        return teams[week - 1].home_alley
    else:
        return get_random_city()


def simulate_season(teams, weeks, number_of_players_per_team, name, season):

    col_names = ['Season', 'Week', 'Datum', 'League Name', 'Spielort', 'Team Name', 'Name', 'EDV', 'Match Number',
                 'Team Name Opponent', 'Position', 'Pins']

    col_names = Columns().get_column_names()

    df_season = pd.DataFrame(columns=col_names)

    team_ids = list(range(len(teams)))
    round_robin_rounds = np.array(get_round_robin_pairings(team_ids))
    round_robin_rounds_per_week = list([np.roll(round_robin_rounds, i) for i in range(weeks)])

    for week in range(weeks):
        # iterate over all pairings
        for match_number, pairings in enumerate(round_robin_rounds_per_week[week]):
            for (team_id, opponent_id) in pairings:
                if team_id == opponent_id:
                    continue
                # print(str(team_id) + " : " + str(opponent_id) + "  |  ", end="")
                # match on team level

                team = teams[team_id]
                team_opponent = teams[opponent_id]

                for player_number in range(number_of_players_per_team):
                    player = team.players[player_number]
                    player_opponent = team_opponent.players[player_number]
                    player_score = teams[team_id].players[player_number].simulate_score()
                    opponent_score = teams[opponent_id].players[player_number].simulate_score()

                    cols_match = [
                        [season, week, "n/a", name, get_random_alley(teams, week), team.team_name, player.get_full_name(), player.id, match_number, team_opponent.team_name, player_number, player_score, np.nan],
                        [season, week, "n/a", name, get_random_alley(teams, week), team_opponent.team_name, player_opponent.get_full_name(), player_opponent.id, match_number, team.team_name, player_number, opponent_score, np.nan]
                        ]
                    df_season = pd.concat([df_season, pd.DataFrame(cols_match, columns=col_names)], ignore_index=True)
                    # print(df_season)

    df_season = df_season.sort_values(by=['Week', 'Team', 'Match', 'Position'])
    return df_season