"""
Get Team Score Sheet Handler.

Handler for GetTeamScoreSheetQuery that retrieves detailed score sheet data
for a specific team including individual scores, opponent scores, and points.
"""

from typing import Dict, Optional
from uuid import UUID
from domain.repositories.league_repository import LeagueRepository
from domain.repositories.league_season_repository import LeagueSeasonRepository
from domain.repositories.team_season_repository import TeamSeasonRepository
from domain.repositories.event_repository import EventRepository
from domain.repositories.match_repository import MatchRepository
from domain.repositories.game_result_repository import GameResultRepository
from domain.repositories.position_comparison_repository import PositionComparisonRepository
from domain.repositories.scoring_system_repository import ScoringSystemRepository
from domain.repositories.player_repository import PlayerRepository
from domain.repositories.club_repository import ClubRepository
from domain.repositories.team_repository import TeamRepository
from domain.entities.position_comparison import ComparisonOutcome
from application.queries.league.get_team_score_sheet_query import GetTeamScoreSheetQuery
from application.dto.team_score_sheet_dto import (
    TeamScoreSheetDTO,
    MatchScoreSheetDTO,
    PositionScoreDTO,
    PositionSummaryDTO
)
from application.exceptions import EntityNotFoundError


class GetTeamScoreSheetHandler:
    """
    Handler for GetTeamScoreSheetQuery.
    
    Retrieves detailed score sheet data for a team including:
    - Individual scores per position per match
    - Opponent scores per position
    - Awarded points per position
    - Team total scores and match points
    - Summary statistics
    """
    
    def __init__(
        self,
        league_repository: LeagueRepository,
        league_season_repository: LeagueSeasonRepository,
        team_season_repository: TeamSeasonRepository,
        event_repository: EventRepository,
        match_repository: MatchRepository,
        game_result_repository: GameResultRepository,
        position_comparison_repository: PositionComparisonRepository,
        scoring_system_repository: ScoringSystemRepository,
        player_repository: PlayerRepository,
        club_repository: ClubRepository,
        team_repository: TeamRepository
    ):
        """
        Initialize handler with required repositories.
        
        Args:
            league_repository: Repository for League entities
            league_season_repository: Repository for LeagueSeason entities
            team_season_repository: Repository for TeamSeason entities
            event_repository: Repository for Event entities
            match_repository: Repository for Match entities
            game_result_repository: Repository for GameResult entities
            position_comparison_repository: Repository for PositionComparison entities
            scoring_system_repository: Repository for ScoringSystem entities
            player_repository: Repository for Player entities
            club_repository: Repository for Club entities
            team_repository: Repository for Team entities
        """
        self._league_repo = league_repository
        self._league_season_repo = league_season_repository
        self._team_season_repo = team_season_repository
        self._event_repo = event_repository
        self._match_repo = match_repository
        self._game_result_repo = game_result_repository
        self._position_comparison_repo = position_comparison_repository
        self._scoring_system_repo = scoring_system_repository
        self._player_repo = player_repository
        self._club_repo = club_repository
        self._team_repo = team_repository
    
    async def handle(self, query: GetTeamScoreSheetQuery) -> TeamScoreSheetDTO:
        """
        Handle GetTeamScoreSheetQuery.
        
        Args:
            query: The query containing league_season_id, team_season_id, and optional week
        
        Returns:
            TeamScoreSheetDTO with detailed score sheet data
        
        Raises:
            EntityNotFoundError: If league_season, team_season, or scoring system not found
        """
        # 1. Load league season
        league_season = await self._league_season_repo.get_by_id(query.league_season_id)
        if not league_season:
            raise EntityNotFoundError(f"LeagueSeason {query.league_season_id} not found")
        
        # 2. Load team season
        team_season = await self._team_season_repo.get_by_id(query.team_season_id)
        if not team_season:
            raise EntityNotFoundError(f"TeamSeason {query.team_season_id} not found")
        
        # Verify team season belongs to league season
        if team_season.league_season_id != league_season.id:
            raise EntityNotFoundError(
                f"TeamSeason {query.team_season_id} does not belong to LeagueSeason {query.league_season_id}"
            )
        
        # 3. Load scoring system
        scoring_system_id = UUID(league_season.scoring_system_id)
        scoring_system = await self._scoring_system_repo.get_by_id(scoring_system_id)
        if not scoring_system:
            raise EntityNotFoundError(
                f"ScoringSystem {scoring_system_id} not found for LeagueSeason {league_season.id}"
            )
        
        # 4. Load events for the league season
        events = await self._event_repo.get_by_league_season(league_season.id)
        
        # Build event_to_week mapping
        event_to_week: Dict[UUID, int] = {}
        for event in events:
            week = event.league_week if event.league_week is not None else 1
            event_to_week[event.id] = week
        
        # 5. Get team name from team entity
        team = await self._team_repo.get_by_id(team_season.team_id)
        if not team:
            raise EntityNotFoundError(f"Team {team_season.team_id} not found")
        team_name = team.name
        
        # 6. Load matches and build score sheet
        match_sheets: list[MatchScoreSheetDTO] = []
        wins = 0
        losses = 0
        ties = 0
        total_team_match_points = 0.0
        total_individual_points = 0.0
        
        # Track points per position for summary
        position_points: Dict[int, float] = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}
        position_matches: Dict[int, int] = {0: 0, 1: 0, 2: 0, 3: 0}
        
        for event in events:
            # Filter by week if specified
            if query.week is not None:
                event_week = event_to_week.get(event.id)
                if event_week is None or event_week != query.week:
                    continue
            
            # Load matches for this event where team participated
            matches = await self._match_repo.get_by_event(event.id)
            
            for match in matches:
                # Check if team is in this match
                is_team1 = match.team1_team_season_id == query.team_season_id
                is_team2 = match.team2_team_season_id == query.team_season_id
                
                if not (is_team1 or is_team2):
                    continue
                
                # Determine opponent
                opponent_team_season_id = match.team2_team_season_id if is_team1 else match.team1_team_season_id
                opponent_team_season = await self._team_season_repo.get_by_id(opponent_team_season_id)
                if not opponent_team_season:
                    continue
                
                opponent_team = await self._team_repo.get_by_id(opponent_team_season.team_id)
                if not opponent_team:
                    continue
                opponent_team_name = opponent_team.name
                
                # Load game results for this match
                game_results = await self._game_result_repo.get_by_match(match.id)
                
                # Load position comparisons
                position_comparisons = await self._position_comparison_repo.get_by_match(match.id)
                
                # Build position scores
                position_scores: list[PositionScoreDTO] = []
                
                # Get team and opponent game results
                team_game_results = [gr for gr in game_results if gr.team_season_id == query.team_season_id]
                opponent_game_results = [gr for gr in game_results if gr.team_season_id == opponent_team_season_id]
                
                # Calculate team totals
                team_total_score = sum(int(gr.score) for gr in team_game_results)
                opponent_total_score = sum(int(gr.score) for gr in opponent_game_results)
                
                # Determine match outcome and points
                if team_total_score > opponent_total_score:
                    team_match_points = scoring_system.points_per_team_match_win
                    opponent_match_points = scoring_system.points_per_team_match_loss
                    wins += 1
                elif opponent_total_score > team_total_score:
                    team_match_points = scoring_system.points_per_team_match_loss
                    opponent_match_points = scoring_system.points_per_team_match_win
                    losses += 1
                else:
                    team_match_points = scoring_system.points_per_team_match_tie
                    opponent_match_points = scoring_system.points_per_team_match_tie
                    ties += 1
                
                total_team_match_points += team_match_points
                
                # Build position scores
                for position in range(4):  # Positions 0-3
                    # Find team's player at this position
                    team_gr = next((gr for gr in team_game_results if gr.position == position), None)
                    opponent_gr = next((gr for gr in opponent_game_results if gr.position == position), None)
                    
                    if team_gr and opponent_gr:
                        # Get player names
                        team_player = await self._player_repo.get_by_id(team_gr.player_id)
                        opponent_player = await self._player_repo.get_by_id(opponent_gr.player_id)
                        
                        team_player_name = team_player.name if team_player else "Unknown"
                        opponent_player_name = opponent_player.name if opponent_player else "Unknown"
                        
                        # Find position comparison to get points
                        pc = next((p for p in position_comparisons if p.position == position), None)
                        
                        # Calculate individual points based on outcome
                        if pc:
                            if is_team1:
                                # Team is team1 in comparison
                                if pc.outcome == ComparisonOutcome.TEAM1_WIN:
                                    points = scoring_system.points_per_individual_match_win
                                elif pc.outcome == ComparisonOutcome.TEAM2_WIN:
                                    points = scoring_system.points_per_individual_match_loss
                                else:  # TIE
                                    points = scoring_system.points_per_individual_match_tie
                            else:
                                # Team is team2 in comparison
                                if pc.outcome == ComparisonOutcome.TEAM1_WIN:
                                    points = scoring_system.points_per_individual_match_loss
                                elif pc.outcome == ComparisonOutcome.TEAM2_WIN:
                                    points = scoring_system.points_per_individual_match_win
                                else:  # TIE
                                    points = scoring_system.points_per_individual_match_tie
                        else:
                            points = 0.0
                        
                        position_scores.append(PositionScoreDTO(
                            position=position,
                            player_id=team_gr.player_id,
                            player_name=team_player_name,
                            score=int(team_gr.score),
                            opponent_player_id=opponent_gr.player_id,
                            opponent_player_name=opponent_player_name,
                            opponent_score=int(opponent_gr.score),
                            points=points
                        ))
                        
                        # Update position summary
                        position_points[position] += points
                        position_matches[position] += 1
                        total_individual_points += points
                
                # Create match score sheet
                match_sheets.append(MatchScoreSheetDTO(
                    match_id=match.id,
                    event_id=event.id,
                    week=event_to_week.get(event.id, 1),
                    round_number=match.round_number,
                    match_number=match.match_number,
                    opponent_team_season_id=opponent_team_season_id,
                    opponent_team_name=opponent_team_name,
                    team_total_score=team_total_score,
                    opponent_total_score=opponent_total_score,
                    team_match_points=team_match_points,
                    opponent_match_points=opponent_match_points,
                    position_scores=position_scores
                ))
        
        # 7. Build position summaries
        position_summaries = [
            PositionSummaryDTO(
                position=pos,
                total_points=position_points[pos],
                matches_played=position_matches[pos]
            )
            for pos in range(4)
        ]
        
        # 8. Get league name
        league = await self._league_repo.get_by_id(league_season.league_id)
        league_name = league.name if league else f"League {league_season.league_id}"
        
        # 9. Return DTO
        return TeamScoreSheetDTO(
            league_season_id=league_season.id,
            league_name=league_name,
            season=league_season.season.value,
            team_season_id=query.team_season_id,
            team_name=team_name,
            week=query.week,
            matches=match_sheets,
            position_summaries=position_summaries,
            total_team_match_points=total_team_match_points,
            total_individual_points=total_individual_points,
            total_points=total_team_match_points + total_individual_points,
            wins=wins,
            losses=losses,
            ties=ties
        )
