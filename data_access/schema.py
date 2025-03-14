from dataclasses import dataclass


@dataclass
class Columns:
    season: str = 'Season'
    week: str = 'Week'
    date: str = 'Date'
    league_name: str = 'League'
    players_per_team: str = 'Players per Team'
    location: str = 'Location'
    round_number: str = 'Round Number'
    match_number: str = 'Match Number'
    team_name: str = 'Team'
    position: str = 'Position'
    player_name: str = 'Player'
    player_id: str = 'Player ID'
    team_name_opponent: str = 'Opponent'
    score: str = 'Score'
    points: str = 'Points'
    input_data: str = 'Input Data'
    computed_data: str = 'Computed Data'

    def __str__(self):
        return str(self.get_column_names())

    def get_column_names(self, selection=None):
        if selection is None:
            return [self.season, self.week, self.date, self.league_name, self.players_per_team, self.location, self.round_number, 
                    self.match_number, self.team_name, self.position, self.player_name, self.player_id, self.team_name_opponent,
                    self.score, self.points, self.input_data, self.computed_data]
        
@dataclass
class ColumnsExtra:
    position: str = '#'
    score_average: str = 'Average'
    score_average_weekly: str = 'ScoreAverageWeekly'
    score_weekly: str = 'ScoreWeekly'
    points_weekly: str = 'PointsWeekly'
    position_change: str = 'PositionChange'
    points_cumulative: str = 'PointsCumulative'
    position_weekly: str = 'PositionWeekly'
    position_cumulative: str = 'PositionCumulative' 
    margin: str = 'WinMargin'
