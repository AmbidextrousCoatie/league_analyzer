"""
Get Team Week Details Handler.

Handler for GetTeamWeekDetailsQuery that retrieves team performance summary
for a specific week.
"""

from typing import Dict, List
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
from domain.repositories.team_repository import TeamRepository
from application.queries.league.get_team_week_details_query import GetTeamWeekDetailsQuery
from application.dto.team_week_details_dto import (
    TeamWeekDetailsDTO,
    MatchWeekSummaryDTO,
    PlayerWeekPerformanceDTO
)
from domain.entities.position_comparison import ComparisonOutcome
from application.exceptions import EntityNotFoundError
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class GetTeamWeekDetailsHandler:
    """
    Handler for GetTeamWeekDetailsQuery.
    
    Retrieves team performance summary for a specific week including:
    - Match summaries (opponent, scores, results)
    - Player performances
    - Week totals and statistics
    """
    
    def __init__(
        self,
        team_season_repository: TeamSeasonRepository,
        league_season_repository: LeagueSeasonRepository,
        league_repository: LeagueRepository,
        event_repository: EventRepository,
        match_repository: MatchRepository,
        game_result_repository: GameResultRepository,
        position_comparison_repository: PositionComparisonRepository,
        scoring_system_repository: ScoringSystemRepository,
        player_repository: PlayerRepository,
        team_repository: TeamRepository
    ):
        """
        Initialize handler with required repositories.
        
        Args:
            team_season_repository: Repository for TeamSeason entities
            league_season_repository: Repository for LeagueSeason entities
            league_repository: Repository for League entities
            event_repository: Repository for Event entities
            match_repository: Repository for Match entities
            game_result_repository: Repository for GameResult entities
            position_comparison_repository: Repository for PositionComparison entities
            scoring_system_repository: Repository for ScoringSystem entities
            player_repository: Repository for Player entities
            team_repository: Repository for Team entities
        """
        self._team_season_repo = team_season_repository
        self._league_season_repo = league_season_repository
        self._league_repo = league_repository
        self._event_repo = event_repository
        self._match_repo = match_repository
        self._game_result_repo = game_result_repository
        self._position_comparison_repo = position_comparison_repository
        self._scoring_system_repo = scoring_system_repository
        self._player_repo = player_repository
        self._team_repo = team_repository
    
    async def handle(self, query: GetTeamWeekDetailsQuery) -> TeamWeekDetailsDTO:
        """
        Handle GetTeamWeekDetailsQuery.
        
        Args:
            query: The query containing team_season_id and week
        
        Returns:
            TeamWeekDetailsDTO with week performance summary
        
        Raises:
            EntityNotFoundError: If team_season, league_season, or scoring system not found
        """
        # 1. Load team season
        team_season = await self._team_season_repo.get_by_id(query.team_season_id)
        if not team_season:
            raise EntityNotFoundError(f"TeamSeason {query.team_season_id} not found")
        
        # 2. Load league season
        league_season = await self._league_season_repo.get_by_id(team_season.league_season_id)
        if not league_season:
            raise EntityNotFoundError(f"LeagueSeason {team_season.league_season_id} not found")
        
        # 3. Load league for name
        league = await self._league_repo.get_by_id(league_season.league_id)
        if not league:
            raise EntityNotFoundError(f"League {league_season.league_id} not found")
        league_name = league.name
        
        # 4. Load scoring system
        scoring_system_id = UUID(league_season.scoring_system_id)
        scoring_system = await self._scoring_system_repo.get_by_id(scoring_system_id)
        if not scoring_system:
            raise EntityNotFoundError(
                f"ScoringSystem {scoring_system_id} not found for LeagueSeason {league_season.id}"
            )
        
        # 5. Get team name
        team = await self._team_repo.get_by_id(team_season.team_id)
        if not team:
            raise EntityNotFoundError(f"Team {team_season.team_id} not found")
        team_name = team.name
        
        # 6. Find event for this week
        events = await self._event_repo.get_by_league_season(league_season.id)
        week_events = [e for e in events if e.league_week == query.week]
        
        if not week_events:
            # Return empty result if no events for this week
            return TeamWeekDetailsDTO(
                team_season_id=query.team_season_id,
                team_name=team_name,
                league_season_id=league_season.id,
                league_name=league_name,
                season=str(league_season.season),
                week=query.week,
                matches=[],
                player_performances=[],
                total_team_score=0,
                total_team_match_points=0.0,
                total_individual_points=0.0,
                total_points=0.0,
                wins=0,
                losses=0,
                ties=0,
                average_score=0.0,
                number_of_matches=0
            )
        
        # 7. Load matches and build week summary
        match_summaries: List[MatchWeekSummaryDTO] = []
        player_performances: List[PlayerWeekPerformanceDTO] = []
        wins = 0
        losses = 0
        ties = 0
        total_team_score = 0
        total_team_match_points = 0.0
        total_individual_points = 0.0
        
        # Track player performances by match
        player_perf_by_match: Dict[UUID, List[PlayerWeekPerformanceDTO]] = {}
        
        for event in week_events:
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
                
                # Get team and opponent game results
                team_game_results = [gr for gr in game_results if gr.team_season_id == query.team_season_id]
                opponent_game_results = [gr for gr in game_results if gr.team_season_id == opponent_team_season_id]
                
                # Calculate team totals
                team_total_score = sum(int(gr.score) for gr in team_game_results)
                opponent_total_score = sum(int(gr.score) for gr in opponent_game_results)
                total_team_score += team_total_score
                
                # Determine match outcome and points
                if team_total_score > opponent_total_score:
                    team_match_points = scoring_system.points_per_team_match_win
                    opponent_match_points = scoring_system.points_per_team_match_loss
                    result = "win"
                    wins += 1
                elif opponent_total_score > team_total_score:
                    team_match_points = scoring_system.points_per_team_match_loss
                    opponent_match_points = scoring_system.points_per_team_match_win
                    result = "loss"
                    losses += 1
                else:
                    team_match_points = scoring_system.points_per_team_match_tie
                    opponent_match_points = scoring_system.points_per_team_match_tie
                    result = "tie"
                    ties += 1
                
                total_team_match_points += team_match_points
                
                # Build match summary
                match_summaries.append(MatchWeekSummaryDTO(
                    match_id=match.id,
                    opponent_team_season_id=opponent_team_season_id,
                    opponent_team_name=opponent_team_name,
                    team_total_score=team_total_score,
                    opponent_total_score=opponent_total_score,
                    team_match_points=team_match_points,
                    opponent_match_points=opponent_match_points,
                    result=result
                ))
                
                # Build player performances for this match
                match_player_perfs: List[PlayerWeekPerformanceDTO] = []
                for position in range(4):  # Positions 0-3
                    team_gr = next((gr for gr in team_game_results if gr.position == position), None)
                    opponent_gr = next((gr for gr in opponent_game_results if gr.position == position), None)
                    
                    if team_gr:
                        # Get player name
                        player = await self._player_repo.get_by_id(team_gr.player_id)
                        player_name = player.name if player else f"Player {team_gr.player_id}"
                        
                        # Get opponent player name if available
                        opponent_player_name = None
                        opponent_score = None
                        if opponent_gr:
                            opponent_player = await self._player_repo.get_by_id(opponent_gr.player_id)
                            opponent_player_name = opponent_player.name if opponent_player else None
                            opponent_score = int(opponent_gr.score)
                        
                        # Get points from position comparison
                        position_comparisons = await self._position_comparison_repo.get_by_match(match.id)
                        position_comp = next((pc for pc in position_comparisons if pc.position == position), None)
                        
                        # Calculate individual points based on outcome
                        if position_comp:
                            if is_team1:
                                # Team is team1 in comparison
                                if position_comp.outcome == ComparisonOutcome.TEAM1_WIN:
                                    points = scoring_system.points_per_individual_match_win
                                elif position_comp.outcome == ComparisonOutcome.TEAM2_WIN:
                                    points = scoring_system.points_per_individual_match_loss
                                else:  # TIE
                                    points = scoring_system.points_per_individual_match_tie
                            else:
                                # Team is team2 in comparison
                                if position_comp.outcome == ComparisonOutcome.TEAM1_WIN:
                                    points = scoring_system.points_per_individual_match_loss
                                elif position_comp.outcome == ComparisonOutcome.TEAM2_WIN:
                                    points = scoring_system.points_per_individual_match_win
                                else:  # TIE
                                    points = scoring_system.points_per_individual_match_tie
                        else:
                            points = 0.0
                        
                        total_individual_points += points
                        
                        player_perf = PlayerWeekPerformanceDTO(
                            player_id=team_gr.player_id,
                            player_name=player_name,
                            position=position,
                            score=int(team_gr.score),
                            points=points,
                            opponent_player_name=opponent_player_name,
                            opponent_score=opponent_score
                        )
                        match_player_perfs.append(player_perf)
                        player_performances.append(player_perf)
                
                player_perf_by_match[match.id] = match_player_perfs
        
        # Calculate totals
        total_points = total_team_match_points + total_individual_points
        number_of_matches = len(match_summaries)
        average_score = total_team_score / number_of_matches if number_of_matches > 0 else 0.0
        
        return TeamWeekDetailsDTO(
            team_season_id=query.team_season_id,
            team_name=team_name,
            league_season_id=league_season.id,
            league_name=league_name,
            season=str(league_season.season),
            week=query.week,
            matches=match_summaries,
            player_performances=player_performances,
            total_team_score=total_team_score,
            total_team_match_points=total_team_match_points,
            total_individual_points=total_individual_points,
            total_points=total_points,
            wins=wins,
            losses=losses,
            ties=ties,
            average_score=average_score,
            number_of_matches=number_of_matches
        )
