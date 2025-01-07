from enum import Enum
from dataclasses import dataclass


class Mapping(Enum):
    en = 1
    ger = 2


@dataclass
class __Columns:

    season: str
    week: str
    date: str
    league_name: str
    location: str
    team_name: str
    player_name: str
    player_id: str
    match_number: str
    team_name_opponent: str
    position: str
    score: str
    points: str

    [field.name for field in fields(C)]

def Columns(mapping=Mapping.en):
    if mapping == Mapping.en:
        return __Columns(season="Season", week="Week", date="Date", league_name="League", location="Location",
                         team_name="Team Name", player_name="Player", player_id="Player ID", match_number="Match Number",
                         team_name_opponent="Team Name Opponent", position="Position", score="Score", points="Points")
    elif mapping == Mapping.ger:
        return __Columns(season="Saison", week="Spieltag", date="Datum", league_name="Liga", location="Spielort",
                         team_name="Team Name", player_name="Spieler", player_id="EDV", match_number="Spiel",
                         team_name_opponent="Gegner", position="Position", score="Ergebnis", points="Punkte")
    else:  # default = english mapping
        return __Columns(season="Season", week="Week", date="Date", league_name="League", location="Location",
                         team_name="Team Name", player_name="Player", player_id="Player ID", match_number="Match Number",
                         team_name_opponent="Team Name Opponent", position="Position", score="Score", points="Points")

