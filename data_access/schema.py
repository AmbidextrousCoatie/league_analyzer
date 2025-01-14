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
    points: str = 'Points'
    input_data: str = 'Input Data'
    computed_data: str = 'Computed Data'

    def __str__(self):
        return str(self.get_column_names())

    def get_column_names(self, selection=None):
        if selection is None:
            return [self.season, self.week, self.date, self.league_name, self.location, self.team_name,
                    self.player_name, self.player_id, self.match_number, self.team_name_opponent,
                    self.position, self.score, self.points, self.input_data, self.computed_data]