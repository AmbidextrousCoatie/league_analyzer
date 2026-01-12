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
        team_season_to_team: Optional[Dict[UUID, UUID]] = None,
        event_to_week: Optional[Dict[UUID, int]] = None,
        status: StandingsStatus = StandingsStatus.PROVISIONAL
    ) -> Standings:
        """
        Calculate standings for teams in a league season.
        
        Args:
            games: List of Game entities (new API: one Game per player)
            teams: Dictionary mapping team_id to Team entities
            league_season_id: UUID of the league season
            up_to_week: Optional week number to calculate standings up to (None = all weeks)
            player_to_team: Optional dictionary mapping player_id to team_id (deprecated, use team_season_to_team)
            team_season_to_team: Optional dictionary mapping team_season_id to team_id (required for new Game API)
            event_to_week: Optional dictionary mapping event_id to week number (for weekly performance tracking)
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
        
        # Initialize standings for all teams
        team_standings: Dict[UUID, TeamStanding] = {}
        for team_id, team in teams.items():
            team_standings[team_id] = TeamStanding(
                team_id=team_id,
                team_name=team.name
            )
        
        # Group games by event_id and team_season_id
        # New Game API: each Game represents one player, so we need to aggregate
        from collections import defaultdict
        event_team_games: Dict[tuple[UUID, UUID], List[Game]] = defaultdict(list)
        
        for game in games:
            if game.team_season_id is None:
                continue
            # Filter by week if specified (requires event_to_week mapping)
            if up_to_week is not None and event_to_week:
                week = event_to_week.get(game.event_id)
                if week is None or week > up_to_week:
                    continue
            event_team_games[(game.event_id, game.team_season_id)].append(game)
        
        # Process each event-team combination
        for (event_id, team_season_id), team_games in event_team_games.items():
            # Map team_season_id to team_id
            if team_season_to_team:
                team_id = team_season_to_team.get(team_season_id)
            else:
                # Fallback: try to find team_id from teams dict (won't work with new API)
                team_id = None
            
            if team_id is None or team_id not in team_standings:
                # Skip if we can't map team_season_id to team_id
                continue
            
            # Sum scores and points for this team in this event
            total_score = sum(game.score for game in team_games)
            total_points = sum(game.points for game in team_games)
            number_of_games = len(team_games)  # Count of individual player games
            
            # Get week number for weekly performance
            week = 1  # Default
            if event_to_week:
                week = event_to_week.get(event_id, 1)
            
            # Update standings
            standing = team_standings[team_id]
            standing.total_score += total_score
            standing.total_points += total_points
            
            # Update weekly performance
            StandingsCalculator._update_weekly_performance(
                standing, week, total_score, total_points, number_of_games
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
    def _update_weekly_performance(
        standing: TeamStanding,
        week: int,
        score: float,
        points: float,
        number_of_games: int
    ) -> None:
        """
        Update or create weekly performance for a team.
        
        Args:
            standing: TeamStanding to update
            week: Week number
            score: Score for this week
            points: Points for this week
            number_of_games: Number of individual player games in this week
        """
        # Find existing weekly performance
        existing = next(
            (wp for wp in standing.weekly_performances if wp.week == week),
            None
        )
        
        if existing:
            # Update existing (accumulate scores, points, and game count)
            existing.score += score
            existing.points += points
            existing.number_of_games += number_of_games
        else:
            # Create new
            standing.weekly_performances.append(
                WeeklyPerformance(
                    week=week,
                    score=score,
                    points=points,
                    number_of_games=number_of_games
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

