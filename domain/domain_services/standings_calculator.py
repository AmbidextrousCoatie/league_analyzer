"""
StandingsCalculator Domain Service

Calculates league standings based on game results.
Handles team rankings, weekly performances, and season totals.
"""

from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass, field
from domain.entities.game import Game
from domain.entities.team import Team
from domain.value_objects.standings_status import StandingsStatus
from domain.exceptions.domain_exception import DomainException


class InvalidStandingsCalculation(DomainException):
    """Raised when standings calculation fails."""
    pass


@dataclass
class WeeklyPerformance:
    """
    Weekly performance data for a team.
    
    Attributes:
        week: Week number
        score: Total score for the week
        points: Total points for the week
        number_of_games: Number of games played in the week
    """
    week: int
    score: float
    points: float
    number_of_games: int


@dataclass
class TeamStanding:
    """
    Standing data for a team in the league.
    
    Attributes:
        team_id: UUID of the team
        team_name: Name of the team
        position: Current position in standings (1-based)
        total_score: Total score for the season
        total_points: Total points for the season
        average_score: Average score per game
        weekly_performances: List of weekly performances
    """
    team_id: UUID
    team_name: str
    position: int = 0
    total_score: float = 0.0
    total_points: float = 0.0
    average_score: float = 0.0
    weekly_performances: List[WeeklyPerformance] = field(default_factory=list)


@dataclass
class Standings:
    """
    Standings for a league season.
    
    Attributes:
        league_season_id: UUID of the league season
        teams: List of team standings
        status: Publication status (provisional, final, disputed)
        calculated_at: When standings were calculated
    """
    league_season_id: UUID
    teams: List[TeamStanding] = field(default_factory=list)
    status: StandingsStatus = field(default=StandingsStatus.PROVISIONAL)
    calculated_at: datetime = field(default_factory=datetime.utcnow)


class StandingsCalculator:
    """
    Domain service for calculating league standings.
    
    Calculates team standings based on game results, including:
    - Total points and scores per team
    - Weekly performances
    - Team rankings (by points, then by score)
    """
    
    @staticmethod
    def calculate_standings(
        games: List[Game],
        teams: Dict[UUID, Team],
        league_season_id: UUID,
        up_to_week: Optional[int] = None,
        player_to_team: Optional[Dict[UUID, UUID]] = None,
        status: StandingsStatus = StandingsStatus.PROVISIONAL
    ) -> Standings:
        """
        Calculate standings for teams in a league season.
        
        Args:
            games: List of Game entities
            teams: Dictionary mapping team_id to Team entities
            league_season_id: UUID of the league season
            up_to_week: Optional week number to calculate standings up to (None = all weeks)
            player_to_team: Optional dictionary mapping player_id to team_id
            status: Publication status of standings (default: PROVISIONAL)
        
        Returns:
            Standings object with team standings and status
        
        Raises:
            InvalidStandingsCalculation: If calculation fails
        """
        if not teams:
            return Standings(
                league_season_id=league_season_id,
                teams=[],
                status=status
            )
        
        # Filter games by league and optional week
        # Note: We'll need to filter by league_season_id once Game has that link
        league_games = [
            game for game in games
            if (up_to_week is None or game.week <= up_to_week)
        ]
        
        # Initialize standings for all teams
        team_standings: Dict[UUID, TeamStanding] = {}
        for team_id, team in teams.items():
            team_standings[team_id] = TeamStanding(
                team_id=team_id,
                team_name=team.name
            )
        
        # Process each game
        for game in league_games:
            StandingsCalculator._process_game(
                game, team_standings, teams, player_to_team
            )
        
        # Calculate averages and sort by position
        for standing in team_standings.values():
            StandingsCalculator._calculate_average(standing)
        
        # Sort by points (descending), then by score (descending)
        sorted_team_standings = sorted(
            team_standings.values(),
            key=lambda s: (s.total_points, s.total_score),
            reverse=True
        )
        
        # Assign positions
        for i, standing in enumerate(sorted_team_standings, 1):
            standing.position = i
        
        return Standings(
            league_season_id=league_season_id,
            teams=sorted_team_standings,
            status=status
        )
    
    @staticmethod
    def _process_game(
        game: Game,
        standings: Dict[UUID, TeamStanding],
        teams: Dict[UUID, Team],
        player_to_team: Optional[Dict[UUID, UUID]] = None
    ) -> None:
        """
        Process a single game and update standings.
        
        Args:
            game: Game entity to process
            standings: Dictionary of team standings to update
            teams: Dictionary of teams
            player_to_team: Optional dictionary mapping player_id to team_id
        """
        if game.team_id not in standings or game.opponent_team_id not in standings:
            # Skip games with teams not in the standings
            return
        
        # Calculate team scores and points from game results
        team1_score, team1_points = StandingsCalculator._calculate_team_totals(
            game, game.team_id, player_to_team
        )
        team2_score, team2_points = StandingsCalculator._calculate_team_totals(
            game, game.opponent_team_id, player_to_team
        )
        
        # Update team 1 standings
        team1_standing = standings[game.team_id]
        team1_standing.total_score += team1_score
        team1_standing.total_points += team1_points
        
        # Update or create weekly performance for team 1
        StandingsCalculator._update_weekly_performance(
            team1_standing, game.week, team1_score, team1_points
        )
        
        # Update team 2 standings
        team2_standing = standings[game.opponent_team_id]
        team2_standing.total_score += team2_score
        team2_standing.total_points += team2_points
        
        # Update or create weekly performance for team 2
        StandingsCalculator._update_weekly_performance(
            team2_standing, game.week, team2_score, team2_points
        )
    
    @staticmethod
    def _calculate_team_totals(
        game: Game,
        team_id: UUID,
        player_to_team: Optional[Dict[UUID, UUID]] = None
    ) -> tuple[float, float]:
        """
        Calculate total score and points for a team in a game.
        
        Args:
            game: Game entity
            team_id: UUID of the team
            player_to_team: Optional dictionary mapping player_id to team_id
        
        Returns:
            Tuple of (total_score, total_points)
        """
        total_score = 0.0
        total_points = 0.0
        
        # If we have player-to-team mapping, use it
        if player_to_team:
            for result in game.results:
                if result.is_team_total:
                    continue
                
                player_team_id = player_to_team.get(result.player_id)
                if player_team_id == team_id:
                    total_score += float(result.score)
                    total_points += float(result.points)
        else:
            # Fallback: assume results are ordered by team
            # First half are team1, second half are team2
            # This is a simplification for Phase 1
            players_per_team = len([r for r in game.results if not r.is_team_total]) // 2
            
            if game.team_id == team_id:
                # First half of results
                team_results = game.results[:players_per_team]
            elif game.opponent_team_id == team_id:
                # Second half of results
                team_results = game.results[players_per_team:players_per_team * 2]
            else:
                return 0.0, 0.0
            
            # Sum scores and points (excluding team totals)
            for result in team_results:
                if not result.is_team_total:
                    total_score += float(result.score)
                    total_points += float(result.points)
        
        return total_score, total_points
    
    @staticmethod
    def _update_weekly_performance(
        standing: TeamStanding,
        week: int,
        score: float,
        points: float
    ) -> None:
        """
        Update or create weekly performance for a team.
        
        Args:
            standing: TeamStanding to update
            week: Week number
            score: Score for this week
            points: Points for this week
        """
        # Find existing weekly performance
        existing = next(
            (wp for wp in standing.weekly_performances if wp.week == week),
            None
        )
        
        if existing:
            # Update existing
            existing.score += score
            existing.points += points
            existing.number_of_games += 1
        else:
            # Create new
            standing.weekly_performances.append(
                WeeklyPerformance(
                    week=week,
                    score=score,
                    points=points,
                    number_of_games=1
                )
            )
    
    @staticmethod
    def _calculate_average(standing: TeamStanding) -> None:
        """
        Calculate average score for a team standing.
        
        Args:
            standing: TeamStanding to update
        """
        total_games = sum(
            wp.number_of_games for wp in standing.weekly_performances
        )
        
        if total_games > 0:
            standing.average_score = standing.total_score / total_games
        else:
            standing.average_score = 0.0

