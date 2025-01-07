from enum import Enum
from dataclasses import dataclass




class Mapping(Enum):
    en = 1
    ger = 2
    undef = 99

@dataclass
class Columns:

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


col_names_league_table = Columns(mapping=Mapping.en)

