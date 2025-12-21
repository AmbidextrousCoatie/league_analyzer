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
        player_to_team: Dict[UUID, UUID],
        up_to_week: Optional[int] = None
    ) -> TeamStatistics:
        """
        Calculate statistics for a team.
        
        Args:
            games: List of Game entities
            team_id: UUID of the team
            player_to_team: Dictionary mapping player_id to team_id
            up_to_week: Optional week number to calculate statistics up to (None = all weeks)
        
        Returns:
            TeamStatistics object
        
        Raises:
            InvalidStatisticsCalculation: If calculation fails
        """
        stats = TeamStatistics(team_id=team_id)
        
        # Filter games for this team and optional week
        team_games = [
            game for game in games
            if (game.team_id == team_id or game.opponent_team_id == team_id) and
            (up_to_week is None or game.week <= up_to_week)
        ]
        
        if not team_games:
            return stats
        
        # Track scores for best/worst
        all_scores: List[float] = []
        weekly_data: Dict[int, Dict[str, float]] = {}
        
        # Process each game
        for game in team_games:
            team_score, team_points, game_scores = StatisticsCalculator._extract_team_data(
                game, team_id, player_to_team
            )
            
            # Add to totals
            stats.total_score += team_score
            stats.total_points += team_points
            stats.games_played += len(game_scores)
            all_scores.extend(game_scores)
            
            # Track weekly data
            if game.week not in weekly_data:
                weekly_data[game.week] = {
                    'score': 0.0,
                    'points': 0.0,
                    'games': 0
                }
            
            weekly_data[game.week]['score'] += team_score
            weekly_data[game.week]['points'] += team_points
            weekly_data[game.week]['games'] += len(game_scores)
        
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
        up_to_week: Optional[int] = None
    ) -> PlayerStatistics:
        """
        Calculate statistics for a player.
        
        Args:
            games: List of Game entities
            player_id: UUID of the player
            up_to_week: Optional week number to calculate statistics up to (None = all weeks)
        
        Returns:
            PlayerStatistics object
        
        Raises:
            InvalidStatisticsCalculation: If calculation fails
        """
        stats = PlayerStatistics(player_id=player_id)
        
        # Filter games for this player and optional week
        player_games = [
            game for game in games
            if any(r.player_id == player_id for r in game.results) and
            (up_to_week is None or game.week <= up_to_week)
        ]
        
        if not player_games:
            return stats
        
        # Track scores for best/worst
        all_scores: List[float] = []
        
        # Process each game
        for game in player_games:
            result = next(
                (r for r in game.results if r.player_id == player_id),
                None
            )
            
            if result and not result.is_team_total:
                score = float(result.score)
                points = float(result.points)
                
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
    
    @staticmethod
    def _extract_team_data(
        game: Game,
        team_id: UUID,
        player_to_team: Dict[UUID, UUID]
    ) -> tuple[float, float, List[float]]:
        """
        Extract team score, points, and individual scores from a game.
        
        Args:
            game: Game entity
            team_id: UUID of the team
            player_to_team: Dictionary mapping player_id to team_id
        
        Returns:
            Tuple of (total_score, total_points, list_of_individual_scores)
        """
        total_score = 0.0
        total_points = 0.0
        individual_scores: List[float] = []
        
        # Find results for this team
        for result in game.results:
            if result.is_team_total:
                continue
            
            player_team_id = player_to_team.get(result.player_id)
            if player_team_id == team_id:
                score = float(result.score)
                points = float(result.points)
                
                total_score += score
                total_points += points
                individual_scores.append(score)
        
        return total_score, total_points, individual_scores

