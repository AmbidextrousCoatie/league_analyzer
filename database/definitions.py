from enum import Enum
from dataclasses import dataclass

@dataclass
class Columns:
    season: str = 'Season'
    week: str = 'Week'
    date: str = 'Date'
    league_name: str = 'League'
    location: str = 'Location'
    team_name: str = 'Team'
    player_name: str = 'Player'
    player_id: str = 'Player ID'
    match_number: str = 'Match Number'
    team_name_opponent: str = 'Opponent'
    position: str = 'Position'
    score: str = 'Score'
    points: str = 'Points',
    input_data: str = 'Input Data'
    computed_data: str = 'Computed Data'

    def __str__(self):
        return str(self.get_column_names())

    def get_column_names(self, selection=None):
        if selection is None:
            return [self.season, self.week, self.date, self.league_name, self.location, self.team_name,
                    self.player_name, self.player_id, self.match_number, self.team_name_opponent,
                    self.position, self.score, self.points, self.input_data, self.computed_data]


class Mapping(Enum):
    en = 1
    ger = 2
    undef = 99

@dataclass
class Columns_deprecated:

    season: str

    def __init__(self, mapping=Mapping.en):
        if mapping == Mapping.en:
            self.season = "Season"
            self.week = "Week"
            self.date = "Date"
            self.league_name = "League"
            self.location = "Location"
            self.team_name = "Team"
            self.player_name = "Player"
            self.player_id = "Player ID"
            self.match_number = "Match"
            self.team_name_opponent = "Opponent"
            self.position = "Position"
            self.score = "Score"
            self.points = "Points"

        elif mapping == Mapping.ger:
            self.season = "Saison"
            self.week = "Spieltag"
            self.date = "Datum"
            self.league_name = "Liga"
            self.location = "Spielort"
            self.team_name = "Team"
            self.player_name = "Spieler"
            self.player_id = "EDV"
            self.match_number = "Spiel"
            self.team_name_opponent = "Gegner"
            self.position = "Position"
            self.score = "Ergebnis"
            self.points = "Punkte"
        else:
            self.__init__(mapping=Mapping.en)

    def __str__(self):
        return str(self.get_column_names())

    def get_column_names(self, selection=None):
        if selection is None:
            return [self.season, self.week, self.date, self.league_name, self.location, self.team_name,
                    self.player_name, self.player_id, self.match_number, self.team_name_opponent,
                    self.position, self.score, self.points]


# col_names_league_table = Columns_deprecated(mapping=Mapping.en)

