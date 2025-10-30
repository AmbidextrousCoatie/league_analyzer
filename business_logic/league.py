import pandas as pd


levels = {
    "1. Bundesliga": 1,
    "2. Bundesliga": 2,
    "BayL": 3,
    "LL N1": 4, 
    "LL N2": 4,
    "LL S": 4,
    "BZOL N1": 5,
    "BZOL N2": 5,
    "BZOL S1": 5,
    "BZOL S2": 5,
    "BZL N1": 6,
    "BZL N2": 6,
    "BZL S1": 6,
    "BZL S2": 6,
    "KL N1": 7,
    "KL N2": 7,
    "KL S1": 7,
    "KL S2": 7
}

class League:

    def __init__(self, league_name, number_of_teams, number_of_players_per_team, names_of_all_exiting_teams=[], weeks=None, skill_level: int = 7):
        self.name = league_name
        self.number_of_teams = number_of_teams
        self.number_of_players_per_team = number_of_players_per_team
        self.skill = skill_level
        self.weeks = number_of_teams if weeks is None else weeks
        self.teams = []

    def __str__(self):

        all_teams = [team.get_name() for team in self.teams]
        return "\n" + self.name + "\n------------------\n" + "\n".join(all_teams)


def get_league_week(df: pd.DataFrame, season: str, league: str, week: int, cumulated: bool = False) -> pd.DataFrame:
    if cumulated:
        return df.loc[(df['Season'] == season) & (df['League'] == league) & (df['Week'] <= week)]
    else:
        return df.loc[(df['Season'] == season) & (df['League'] == league) & (df['Week'] == week)]


def get_league_standings(season: str, league: str, week: int, cumulated: bool = False) -> pd.DataFrame:
     # if cumulated, get all weeks up to the requested week for the season + league combo

    if cumulated:
        return df.loc[(df['Season'] == season) & (df['League'] == league) & (df['Week'] <= week)]
    else:
        return df.loc[(df['Season'] == season) & (df['League'] == league) & (df['Week'] == week)]




    
    pass