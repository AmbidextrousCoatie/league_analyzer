"""
Get Match Overview Handler.

Handler for GetMatchOverviewQuery that retrieves detailed match information
including position-by-position comparisons and team totals.
"""

from typing import Dict, List
from uuid import UUID
from datetime import datetime
from domain.repositories.match_repository import MatchRepository
from domain.repositories.event_repository import EventRepository
from domain.repositories.league_season_repository import LeagueSeasonRepository
from domain.repositories.league_repository import LeagueRepository
from domain.repositories.team_season_repository import TeamSeasonRepository
from domain.repositories.team_repository import TeamRepository
from domain.repositories.club_repository import ClubRepository
from domain.repositories.position_comparison_repository import PositionComparisonRepository
from domain.repositories.match_scoring_repository import MatchScoringRepository
from domain.repositories.player_repository import PlayerRepository
from domain.repositories.scoring_system_repository import ScoringSystemRepository
from domain.entities.position_comparison import ComparisonOutcome
from application.queries.league.get_match_overview_query import GetMatchOverviewQuery
from application.dto.league_dto import (
    MatchOverviewDTO,
    PositionComparisonDTO,
    TeamMatchSummaryDTO
)
from application.exceptions import EntityNotFoundError


class GetMatchOverviewHandler:
    """
    Handler for GetMatchOverviewQuery.
    
    Retrieves detailed match information including:
    - Match metadata (event, league, season, week, round, match number)
    - Team information (names, totals)
    - Position-by-position comparisons (players, scores, points, outcomes)
    - Team scoring (individual points, match points, total points)
    """
    
    def __init__(
        self,
        match_repository: MatchRepository,
        event_repository: EventRepository,
        league_season_repository: LeagueSeasonRepository,
        league_repository: LeagueRepository,
        team_season_repository: TeamSeasonRepository,
        team_repository: TeamRepository,
        club_repository: ClubRepository,
        position_comparison_repository: PositionComparisonRepository,
        match_scoring_repository: MatchScoringRepository,
        player_repository: PlayerRepository,
        scoring_system_repository: ScoringSystemRepository
    ):
        """
        Initialize handler with required repositories.
        
        Args:
            match_repository: Repository for Match entities
            event_repository: Repository for Event entities
            league_season_repository: Repository for LeagueSeason entities
            league_repository: Repository for League entities
            team_season_repository: Repository for TeamSeason entities
            team_repository: Repository for Team entities
            club_repository: Repository for Club entities
            position_comparison_repository: Repository for PositionComparison entities
            match_scoring_repository: Repository for MatchScoring entities
            player_repository: Repository for Player entities
            scoring_system_repository: Repository for ScoringSystem entities
        """
        self._match_repo = match_repository
        self._event_repo = event_repository
        self._league_season_repo = league_season_repository
        self._league_repo = league_repository
        self._team_season_repo = team_season_repository
        self._team_repo = team_repository
        self._club_repo = club_repository
        self._position_comparison_repo = position_comparison_repository
        self._match_scoring_repo = match_scoring_repository
        self._player_repo = player_repository
        self._scoring_system_repo = scoring_system_repository
    
    async def _get_team_name(self, team_id: UUID, club_id: UUID, team_number: int) -> str:
        """
        Get formatted team name (club name + team number if > 1).
        
        Args:
            team_id: UUID of the team
            club_id: UUID of the club
            team_number: Team number within the club
        
        Returns:
            Formatted team name
        """
        club = await self._club_repo.get_by_id(club_id)
        if not club:
            return "Unknown Team"
        
        if team_number and team_number > 1:
            return f"{club.name} {team_number}"
        return club.name
    
    async def handle(self, query: GetMatchOverviewQuery) -> MatchOverviewDTO:
        """
        Handle GetMatchOverviewQuery.
        
        Args:
            query: The query containing match_id
        
        Returns:
            MatchOverviewDTO with detailed match information
        
        Raises:
            EntityNotFoundError: If match or related entities not found
        """
        # 1. Load match
        match = await self._match_repo.get_by_id(query.match_id)
        if not match:
            raise EntityNotFoundError(f"Match {query.match_id} not found")
        
        # 2. Load event
        event = await self._event_repo.get_by_id(match.event_id)
        if not event:
            raise EntityNotFoundError(f"Event {match.event_id} not found for match {query.match_id}")
        
        # 3. Load league season
        league_season = await self._league_season_repo.get_by_id(event.league_season_id)
        if not league_season:
            raise EntityNotFoundError(
                f"LeagueSeason {event.league_season_id} not found for event {event.id}"
            )
        
        # 4. Load league
        league = await self._league_repo.get_by_id(league_season.league_id)
        if not league:
            raise EntityNotFoundError(
                f"League {league_season.league_id} not found for league season {league_season.id}"
            )
        
        # 5. Load team seasons
        team1_season = await self._team_season_repo.get_by_id(match.team1_team_season_id)
        team2_season = await self._team_season_repo.get_by_id(match.team2_team_season_id)
        
        if not team1_season:
            raise EntityNotFoundError(
                f"TeamSeason {match.team1_team_season_id} not found for match {query.match_id}"
            )
        if not team2_season:
            raise EntityNotFoundError(
                f"TeamSeason {match.team2_team_season_id} not found for match {query.match_id}"
            )
        
        # 6. Load teams
        team1 = await self._team_repo.get_by_id(team1_season.team_id)
        team2 = await self._team_repo.get_by_id(team2_season.team_id)
        
        if not team1:
            raise EntityNotFoundError(
                f"Team {team1_season.team_id} not found for team season {team1_season.id}"
            )
        if not team2:
            raise EntityNotFoundError(
                f"Team {team2_season.team_id} not found for team season {team2_season.id}"
            )
        
        # 7. Get team names
        team1_name = await self._get_team_name(team1.id, team1.club_id, team1.team_number)
        team2_name = await self._get_team_name(team2.id, team2.club_id, team2.team_number)
        
        # 8. Load position comparisons
        position_comparisons = await self._position_comparison_repo.get_by_match(match.id)
        
        # 9. Load match scoring for the league season's scoring system
        scoring_system_id = league_season.scoring_system_id  # Already a string
        match_scoring = await self._match_scoring_repo.get_by_match_and_system(
            match.id,
            scoring_system_id
        )
        
        # If no match scoring found, use defaults
        team1_individual_points = match_scoring.team1_individual_points if match_scoring else 0.0
        team2_individual_points = match_scoring.team2_individual_points if match_scoring else 0.0
        team1_match_points = match_scoring.team1_match_points if match_scoring else 0.0
        team2_match_points = match_scoring.team2_match_points if match_scoring else 0.0
        
        # 10. Load scoring system to determine points per position outcome
        scoring_system_uuid = UUID(scoring_system_id)
        scoring_system = await self._scoring_system_repo.get_by_id(scoring_system_uuid)
        if not scoring_system:
            raise EntityNotFoundError(
                f"ScoringSystem {scoring_system_id} not found for league season {league_season.id}"
            )
        
        # 11. Build position comparison DTOs
        position_dtos: List[PositionComparisonDTO] = []
        player_names: Dict[UUID, str] = {}
        
        # Load all player names we need
        player_ids = set()
        for pc in position_comparisons:
            player_ids.add(pc.team1_player_id)
            player_ids.add(pc.team2_player_id)
        
        for player_id in player_ids:
            player = await self._player_repo.get_by_id(player_id)
            if player:
                player_names[player_id] = player.name
        
        # Build position DTOs (positions 0-3)
        for position in range(4):
            # Find comparison for this position
            pc = None
            for comparison in position_comparisons:
                if comparison.position == position:
                    pc = comparison
                    break
            
            if pc:
                # Determine points based on outcome
                if pc.outcome == ComparisonOutcome.TEAM1_WIN:
                    team1_points = scoring_system.points_per_individual_match_win
                    team2_points = scoring_system.points_per_individual_match_loss
                elif pc.outcome == ComparisonOutcome.TEAM2_WIN:
                    team1_points = scoring_system.points_per_individual_match_loss
                    team2_points = scoring_system.points_per_individual_match_win
                else:  # TIE
                    team1_points = scoring_system.points_per_individual_match_tie
                    team2_points = scoring_system.points_per_individual_match_tie
                
                position_dtos.append(PositionComparisonDTO(
                    position=position,
                    team1_player_id=pc.team1_player_id,
                    team1_player_name=player_names.get(pc.team1_player_id, "Unknown Player"),
                    team1_score=int(pc.team1_score),
                    team1_points=team1_points,
                    team2_player_id=pc.team2_player_id,
                    team2_player_name=player_names.get(pc.team2_player_id, "Unknown Player"),
                    team2_score=int(pc.team2_score),
                    team2_points=team2_points,
                    outcome=pc.outcome.value
                ))
            else:
                # No comparison for this position
                position_dtos.append(PositionComparisonDTO(
                    position=position,
                    team1_player_id=UUID('00000000-0000-0000-0000-000000000000'),
                    team1_player_name="-",
                    team1_score=0,
                    team1_points=0.0,
                    team2_player_id=UUID('00000000-0000-0000-0000-000000000000'),
                    team2_player_name="-",
                    team2_score=0,
                    team2_points=0.0,
                    outcome="none"
                ))
        
        # 12. Build team summaries
        team1_summary = TeamMatchSummaryDTO(
            team_id=team1.id,
            team_name=team1_name,
            total_score=int(match.team1_total_score),
            individual_points=team1_individual_points,
            match_points=team1_match_points,
            total_points=team1_individual_points + team1_match_points
        )
        
        team2_summary = TeamMatchSummaryDTO(
            team_id=team2.id,
            team_name=team2_name,
            total_score=int(match.team2_total_score),
            individual_points=team2_individual_points,
            match_points=team2_match_points,
            total_points=team2_individual_points + team2_match_points
        )
        
        # 13. Return DTO
        return MatchOverviewDTO(
            match_id=match.id,
            event_id=event.id,
            league_id=league.id,
            league_name=league.name,
            league_abbreviation=league.abbreviation,
            league_season_id=league_season.id,
            season=league_season.season.value,
            league_week=event.league_week,
            round_number=match.round_number,
            match_number=match.match_number,
            team1=team1_summary,
            team2=team2_summary,
            position_comparisons=position_dtos,
            calculated_at=datetime.utcnow()
        )
