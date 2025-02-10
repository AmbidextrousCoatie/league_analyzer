import random

import numpy as np
import pandas as pd

import sys
import os
import itertools
from random import shuffle
from datetime import datetime, timedelta
import calendar

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from database.generator.teams import DataGeneratorTeam
from database.generator.player import DataGeneratorPlayer
from database.generator.league import DataGeneratorLeague

from data_access.schema import Columns


def get_random_city():
    cities_bavaria = ['München', 'Nürnberg', 'Augsburg', 'Regensburg', 'Ingolstadt', 'Würzburg', 'Fürth', 'Erlangen',
                      'Bayreuth', 'Bamberg', 'Aschaffenburg', 'Landshut', 'Kempten', 'Rosenheim', 'Schweinfurt',
                      'Neu-Ulm', 'Passau', 'Straubing', 'Hof', 'Weiden in der Oberpfalz']

    return random.choice(cities_bavaria)


def create_random_player(league_skill):

    return DataGeneratorPlayer(get_random_id(), get_random_first_name(), get_random_last_name(), get_random_skill(league_skill))


def create_league_roster(league: DataGeneratorLeague):
    league.teams = [create_team(league.skill, league.number_of_players_per_team) for i in range(league.number_of_teams)]
    return league


def create_team(league_skill, players_per_team=4):
    home_alley = get_random_city()
    team_name = get_random_team_name(team_city=home_alley)
    players = [create_random_player(league_skill) for i in range(players_per_team)]
    return DataGeneratorTeam(team_name, players, home_alley)


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

    if league_skill - 1 > skill_low:
        skill_low = league_skill - 1
    if league_skill + 1.5 < skill_high:
        skill_high = league_skill + 1.5

    return round(random.uniform(skill_low, skill_high), 1)


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



def find_round_robin_combinations(values: list):
    
    # Generate all possible pairwise combinations
    
    # make values unique
    values = list(set(values))
    
    # if len(values) is odd, add a wildcard
    if len(values) % 2 != 0:
        values.append('wildcard')
    
    number_of_rounds = len(values) - 1
    number_of_pairs_per_round = len(values) // 2


    #all_pairs = list(itertools.combinations(values, 2))

    pairs_as_sets = [set(pair) for pair in itertools.combinations(values, 2)]


    print(pairs_as_sets)
    print("start")
    selected_pairs = []
    
    for round in range(number_of_rounds):
        print("round: ", round)
        pairs_for_round = [pairs_as_sets.pop(0)]
        for i in range(number_of_pairs_per_round - 1):
            print(pairs_as_sets)
            candidate_pair = pairs_as_sets[i]
            for pair in pairs_for_round:
                print(pairs_for_round)
                if candidate_pair.intersection(pair):
                    continue
                    print("ignored pair: ", candidate_pair)
                else:
                    pairs_for_round.append(pairs_as_sets.pop(i))
                    print("selected pair: ", candidate_pair)
        selected_pairs.append(pairs_for_round)

    print(selected_pairs)
    


    return results


def get_round_robin_pairings_old(teams):

    # Wenn die Anzahl der Teams ungerade ist, fügen wir ein Freilos hinzu
    if len(teams) % 2 != 0:
        teams.append('Freilos')
    pairs = list(itertools.combinations(teams, 2))
    shuffled_pairs = shuffle(pairs)
    #print(teams)
    #print(pairs)
    #print(shuffled_pairs)

    n = len(teams)
    pairings = []

    for play_round in range(n - 1):
        pairs = []
        for i in range(n // 2):
            home = teams[i]
            away = teams[n - 1 - i]
            if play_round % 2 == 0:
                pairs.append((home, away))
            else:
                pairs.append((away, home))
        pairings.append(pairs)
        # Die Rotation der Teams für die nächste Runde, ohne das erste Team zu bewegen
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]

    #print(pairings)

    return pairings

def generate_nested_round_robin_pairings(teams):
    """
    Generate a nested list of pairings for a round-robin tournament with an extra layer for match numbers.

    Args:
        teams (list): List of team names.

    Returns:
        list: Nested list where the outer list represents match days,
              the second layer represents match numbers on that day,
              and the innermost lists contain the pairings [Team1, Team2].
    """
    # If odd number of teams, add a dummy team for byes
    if len(teams) % 2 != 0:
        teams.append("BYE")
    
    n = len(teams)
    match_days = n - 1  # Number of match days for even number of teams
    matches_per_day = n // 2  # Number of concurrent matches per match day

    # Initialize the list to hold all match days
    all_match_days = []

    # Create a list of teams excluding the first one for rotation
    teams_rotating = teams[1:]

    for day in range(match_days):
        # List to hold all match numbers for the current match day
        match_numbers = []
        
        # Divide the rotating teams into chunks for match numbers
        # Each chunk represents a match number (time slot) with concurrent matches
        # For simplicity, we'll assign one match number per concurrent pairing
        # This can be adjusted based on specific requirements

        # Shuffle the teams_rotating to create concurrent pairings
        concurrent_pairings = []
        temp_rotating = teams_rotating.copy()

        for i in range(0, len(temp_rotating), matches_per_day):
            pairings = []
            for j in range(matches_per_day):
                if i + j < len(temp_rotating):
                    pairings.append([temp_rotating[i + j], temp_rotating[-(i + j + 1)]])
            if pairings:
                concurrent_pairings.append(pairings)
        
        match_numbers.extend(concurrent_pairings)

        # Fix the first team and rotate the rest
        fixed_team = teams[0]
        rotated = [teams_rotating[-1]] + teams_rotating[:-1]
        teams_rotating = rotated

        # Pair the fixed team with the last team in the rotated list
        first_pair = [fixed_team, teams_rotating[-1]]
        if "BYE" not in first_pair:
            # Insert the first pair at the beginning
            match_numbers.insert(0, [first_pair])

        # Pair the remaining teams
        paired = []
        for i in range(matches_per_day):
            team1 = teams_rotating[i]
            team2 = teams_rotating[-i - 1]
            if "BYE" not in [team1, team2]:
                pair = [team1, team2]
                # Find the match number (time slot) to append this pairing
                if i < len(match_numbers):
                    match_numbers[i].append(pair)
                else:
                    match_numbers.append([pair])
        
        all_match_days.append(match_numbers)

    return all_match_days

# Example Usage
teams = ["A", "B", "C", "D"]
pairings = generate_nested_round_robin_pairings(teams)

for day_num, day in enumerate(pairings, start=1):
    print(f"Match Day {day_num}:")
    for match_num, match in enumerate(day, start=1):
        print(f"  Match Number {match_num}:")
        for pairing in match:
            print(f"    {pairing[0]} vs {pairing[1]}")
    print()

def transfer_teams_after_season(league_major, league_minor, number_of_teams_transferred):
    print(league_major)
    
    teams_promoted_out, _ = league_minor.get_names_of_teams_that_will_change_leagues(number_of_teams_transferred, 0)
    _, teams_demoted_out = league_major.get_names_of_teams_that_will_change_leagues(0, number_of_teams_transferred)
    teams_going_to_minor_league = league_major.eject_team_from_league(teams_demoted_out)
    teams_going_to_major_league = league_minor.eject_team_from_league(teams_promoted_out)
    
    print("Aufsteiger:")
    for team in teams_going_to_major_league:
        print(team.get_name())
    print("Absteiger:")
    for team in teams_going_to_minor_league:
        
        print(team.get_name())
    league_major.add_team_to_league(teams_going_to_major_league)
    league_minor.add_team_to_league(teams_going_to_minor_league)

    print(league_major)


def generate_league_dates(season, league_size):
    # Parse season start year from format "23/24" -> 2023
    start_year = 2000 + int(season.split('/')[0])
    
    # Find first Sunday in October of start year
    c = calendar.monthcalendar(start_year, 10)  # October
    # Get the first Sunday (0-based index 6) that isn't 0
    first_sunday = next(week[6] for week in c if week[6] != 0)
    
    # Create start date
    start_date = datetime(start_year, 10, first_sunday)
    
    # Determine weeks between matches based on league size
    if league_size == 6:
        weeks_between = 5
    elif league_size == 8:
        weeks_between = 4
    elif league_size == 10:
        weeks_between = 3
    else:
        raise ValueError("Unsupported league size")
    
    # Number of match days needed (each team plays against every other team)
    num_match_days = league_size - 1
    
    # Generate all dates
    dates = []
    current_date = start_date
    for _ in range(num_match_days):
        dates.append(current_date)
        current_date += timedelta(weeks=weeks_between)
    
    return dates


def simulate_season(teams, weeks, number_of_players_per_team, name, season):

    col_names = Columns().get_column_names()

    df_season = pd.DataFrame(columns=col_names)

    team_ids = list(range(len(teams)))
    round_robin_rounds = np.array(get_round_robin_pairings_old(team_ids))
    #round_robin_rounds_per_week = list([np.roll(round_robin_rounds, i) for i in range(weeks)])

    # find players that have a good day
    # 50 % that on player in each team has a good day
    # select random 
    
    dates = generate_league_dates(season, len(teams))

    for week, date in enumerate(dates):
        #print("\n week: ", week)


        teams_with_good_day = [random.randint(0, 1) for i in range(len(teams))]
        players_with_good_day = [random.randint(0, number_of_players_per_team-1) for i in range(len(teams_with_good_day) )]
        teams_with_bad_day = [random.randint(0, 1) for i in range(len(teams))]
        players_with_bad_day = [random.randint(0, number_of_players_per_team-1) for i in range(len(teams_with_good_day) )]
        
        
        alley = get_random_alley(teams, week)
        # iterate over all pairings

        for round_number, pairings in enumerate(round_robin_rounds):
            #print(pairings)
            match_number = 0
            for (team_id, opponent_id) in pairings:
                if team_id == opponent_id:
                    continue
                
                #print(str(team_id) + " : " + str(opponent_id) + "  |  ", end="")
                # match on team level

                team = teams[team_id]
                team_opponent = teams[opponent_id]
                team_is_home_alley = team.home_alley == alley
                opponent_is_home_alley = team_opponent.home_alley == alley

                for player_number in range(number_of_players_per_team):
                    player = team.players[player_number]
                    player_has_good_day = teams_with_good_day[team_id] and players_with_good_day[team_id] == player_number
                    player_has_bad_day = teams_with_bad_day[team_id] and players_with_bad_day[team_id] == player_number
                    player_opponent = team_opponent.players[player_number]  
                    player_opponent_has_good_day = teams_with_good_day[opponent_id] and players_with_good_day[opponent_id] == player_number
                    player_opponent_has_bad_day = teams_with_bad_day[opponent_id] and players_with_bad_day[opponent_id] == player_number
                    player_score = teams[team_id].players[player_number].simulate_score(team_is_home_alley, player_has_good_day, player_has_bad_day)
                    opponent_score = teams[opponent_id].players[player_number].simulate_score(opponent_is_home_alley, player_opponent_has_good_day, player_opponent_has_bad_day)

                    cols_match = [
                        [season, week+1, date, name, number_of_players_per_team, alley, round_number, match_number, 
                         team.team_name, player_number, player.get_full_name(), player.id, team_opponent.team_name, 
                         player_score, np.nan, True, False],
                        [season, week+1, date, name, number_of_players_per_team, alley, round_number, match_number, 
                         team_opponent.team_name, player_number, player_opponent.get_full_name(), player_opponent.id, team.team_name,
                         opponent_score, np.nan, True, False]
                        ]
                    df_season = pd.concat([df_season, pd.DataFrame(cols_match, columns=col_names)], ignore_index=True)
                    # print(df_season)
                match_number += 1

    df_season = df_season.sort_values(by=[Columns.week, Columns.round_number, Columns.match_number, Columns.team_name, Columns.position])
    return df_season