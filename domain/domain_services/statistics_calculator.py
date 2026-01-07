"""
StatisticsCalculator Domain Service

Calculates statistics for teams and players based on game results.
Provides aggregated data like totals, averages, best/worst scores.
"""

from typing import List, Dict, Optional
from uuid import UUID
from dataclasses import dataclass, field
from domain.entities.game import Game
from domain.exceptions.domain_exception import DomainException


class InvalidStatisticsCalculation(DomainException):
    """Raised when statistics calculation fails."""
    pass


@dataclass
class WeeklyTeamPerformance:
    """
    Weekly performance data for a team.
    
    Attributes:
        week: Week number
        total_score: Total score for the week
        total_points: Total points for the week
        number_of_games: Number of games played in the week
    """
    week: int
    total_score: float
    total_points: float
    number_of_games: int


@dataclass
class TeamStatistics:
    """
    Statistics for a team.
    
    Attributes:
        team_id: UUID of the team
        total_score: Total score for all games
        total_points: Total points for all games
        games_played: Total number of games played
        average_score: Average score per game
        best_score: Best single game score
        worst_score: Worst single game score
        weekly_performances: List of weekly performances
    """
    team_id: UUID
    total_score: float = 0.0
    total_points: float = 0.0
    games_played: int = 0
    average_score: float = 0.0
    best_score: float = 0.0
    worst_score: float = 0.0
    weekly_performances: List[WeeklyTeamPerformance] = field(default_factory=list)


@dataclass
class PlayerStatistics:
    """
    Statistics for a player.
    
    Attributes:
        player_id: UUID of the player
        total_score: Total score for all games
        total_points: Total points for all games
        games_played: Total number of games played
        average_score: Average score per game
        best_score: Best single game score
        worst_score: Worst single game score
    """
    player_id: UUID
    total_score: float = 0.0
    total_points: float = 0.0
    games_played: int = 0
    average_score: float = 0.0
    best_score: float = 0.0
    worst_score: float = 0.0


class StatisticsCalculator:
    """
    Domain service for calculating statistics.
    
    Calculates aggregated statistics for teams and players, including:
    - Total scores and points
    - Averages
    - Best and worst scores
    - Weekly performances
    """
    
    @staticmethod
    def calculate_team_statistics(
        games: List[Game],
        team_id: UUID,
        player_to_team: Optional[Dict[UUID, UUID]] = None,
        team_season_to_team: Optional[Dict[UUID, UUID]] = None,
        event_to_week: Optional[Dict[UUID, int]] = None,
        up_to_week: Optional[int] = None
    ) -> TeamStatistics:
        """
        Calculate statistics for a team.
        
        Args:
            games: List of Game entities (new API: one Game per player)
            team_id: UUID of the team
            player_to_team: Dictionary mapping player_id to team_id (deprecated, use team_season_to_team)
            team_season_to_team: Dictionary mapping team_season_id to team_id (required for new Game API)
            event_to_week: Dictionary mapping event_id to week number (for weekly performance tracking)
            up_to_week: Optional week number to calculate statistics up to (None = all weeks)
        
        Returns:
            TeamStatistics object
        
        Raises:
            InvalidStatisticsCalculation: If calculation fails
        """
        stats = TeamStatistics(team_id=team_id)
        
        # Find team_season_ids for this team
        team_season_ids = set()
        if team_season_to_team:
            team_season_ids = {ts_id for ts_id, t_id in team_season_to_team.items() if t_id == team_id}
        
        # Filter games for this team
        team_games = [
            game for game in games
            if game.team_season_id in team_season_ids
        ]
        
        # Filter by week if specified
        if up_to_week is not None and event_to_week:
            team_games = [
                game for game in team_games
                if event_to_week.get(game.event_id, 999) <= up_to_week
            ]
        
        if not team_games:
            return stats
        
        # Track scores for best/worst
        all_scores: List[float] = []
        weekly_data: Dict[int, Dict[str, float]] = {}
        
        # Process each game (new API: each game is one player's game)
        for game in team_games:
            score = game.score
            points = game.points
            
            # Add to totals
            stats.total_score += score
            stats.total_points += points
            stats.games_played += 1
            all_scores.append(score)
            
            # Track weekly data
            week = 1  # Default
            if event_to_week:
                week = event_to_week.get(game.event_id, 1)
            
            if week not in weekly_data:
                weekly_data[week] = {
                    'score': 0.0,
                    'points': 0.0,
                    'games': 0
                }
            
            weekly_data[week]['score'] += score
            weekly_data[week]['points'] += points
            weekly_data[week]['games'] += 1
        
        # Calculate averages
        if stats.games_played > 0:
            stats.average_score = stats.total_score / stats.games_played
        
        # Calculate best/worst scores
        if all_scores:
            stats.best_score = max(all_scores)
            stats.worst_score = min(all_scores)
        
        # Build weekly performances
        for week in sorted(weekly_data.keys()):
            week_data = weekly_data[week]
            stats.weekly_performances.append(
                WeeklyTeamPerformance(
                    week=week,
                    total_score=week_data['score'],
                    total_points=week_data['points'],
                    number_of_games=week_data['games']
                )
            )
        
        return stats
    
    @staticmethod
    def calculate_player_statistics(
        games: List[Game],
        player_id: UUID,
        event_to_week: Optional[Dict[UUID, int]] = None,
        up_to_week: Optional[int] = None
    ) -> PlayerStatistics:
        """
        Calculate statistics for a player.
        
        Args:
            games: List of Game entities (new API: one Game per player)
            player_id: UUID of the player
            event_to_week: Dictionary mapping event_id to week number (for filtering by week)
            up_to_week: Optional week number to calculate statistics up to (None = all weeks)
        
        Returns:
            PlayerStatistics object
        
        Raises:
            InvalidStatisticsCalculation: If calculation fails
        """
        stats = PlayerStatistics(player_id=player_id)
        
        # Filter games for this player
        player_games = [
            game for game in games
            if game.player_id == player_id
        ]
        
        # Filter by week if specified
        if up_to_week is not None and event_to_week:
            player_games = [
                game for game in player_games
                if event_to_week.get(game.event_id, 999) <= up_to_week
            ]
        
        if not player_games:
            return stats
        
        # Track scores for best/worst
        all_scores: List[float] = []
        
        # Process each game (new API: game.score and game.points are directly available)
        for game in player_games:
            score = game.score
            points = game.points
            
            stats.total_score += score
            stats.total_points += points
            stats.games_played += 1
            all_scores.append(score)
        
        # Calculate averages
        if stats.games_played > 0:
            stats.average_score = stats.total_score / stats.games_played
        
        # Calculate best/worst scores
        if all_scores:
            stats.best_score = max(all_scores)
            stats.worst_score = min(all_scores)
        
        return stats
    

