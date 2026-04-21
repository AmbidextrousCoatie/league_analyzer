"""
Get Team Statistics Handler.

Handler for GetTeamStatisticsQuery that retrieves comprehensive statistics for a team.
"""

from datetime import datetime
from typing import List
from uuid import UUID
from domain.repositories.team_repository import TeamRepository
from domain.repositories.club_repository import ClubRepository
from domain.repositories.team_season_repository import TeamSeasonRepository
from domain.repositories.league_season_repository import LeagueSeasonRepository
from domain.repositories.league_repository import LeagueRepository
from domain.repositories.event_repository import EventRepository
from domain.repositories.match_repository import MatchRepository
from domain.repositories.game_result_repository import GameResultRepository
from domain.repositories.position_comparison_repository import PositionComparisonRepository
from domain.repositories.scoring_system_repository import ScoringSystemRepository
from application.queries.league.get_team_statistics_query import GetTeamStatisticsQuery
from application.dto.team_statistics_dto import (
    TeamStatisticsDTO,
    SeasonProgressionDTO,
    SeasonStatisticsDTO,
    WeeklyPerformanceDTO,
    GameRecordDTO,
    ClutchPerformanceDTO,
    OpponentClutchSummaryDTO,
    PositionPerformanceDTO,
    RecentFormDTO
)
from application.exceptions import EntityNotFoundError
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class GetTeamStatisticsHandler:
    """
    Handler for GetTeamStatisticsQuery.
    
    Retrieves comprehensive statistics for a team including:
    - Overall statistics (games, scores, points, wins/losses/ties)
    - Season progression chart
    - Per-season breakdown with league averages
    - Weekly performance
    - Best/worst games and biggest wins/losses
    - Clutch performance (close matches)
    - Position performance
    - Recent form
    """
    
    def __init__(
        self,
        team_repository: TeamRepository,
        club_repository: ClubRepository,
        team_season_repository: TeamSeasonRepository,
        league_season_repository: LeagueSeasonRepository,
        league_repository: LeagueRepository,
        event_repository: EventRepository,
        match_repository: MatchRepository,
        game_result_repository: GameResultRepository,
        position_comparison_repository: PositionComparisonRepository,
        scoring_system_repository: ScoringSystemRepository
    ):
        """
        Initialize handler with required repositories.
        
        Args:
            team_repository: Repository for Team entities
            club_repository: Repository for Club entities
            team_season_repository: Repository for TeamSeason entities
            league_season_repository: Repository for LeagueSeason entities
            league_repository: Repository for League entities
            match_repository: Repository for Match entities
            game_result_repository: Repository for GameResult entities
            position_comparison_repository: Repository for PositionComparison entities
            scoring_system_repository: Repository for ScoringSystem entities
        """
        self._team_repo = team_repository
        self._club_repo = club_repository
        self._team_season_repo = team_season_repository
        self._league_season_repo = league_season_repository
        self._league_repo = league_repository
        self._event_repo = event_repository
        self._match_repo = match_repository
        self._game_result_repo = game_result_repository
        self._position_comparison_repo = position_comparison_repository
        self._scoring_system_repo = scoring_system_repository
    
    async def handle(self, query: GetTeamStatisticsQuery) -> TeamStatisticsDTO:
        """
        Handle GetTeamStatisticsQuery.
        
        Args:
            query: The query containing team_id and filter parameters
        
        Returns:
            TeamStatisticsDTO with comprehensive team statistics
        
        Raises:
            EntityNotFoundError: If team not found
        """
        # 1. Load team
        team = await self._team_repo.get_by_id(query.team_id)
        if not team:
            raise EntityNotFoundError(f"Team {query.team_id} not found")
        
        # 2. Load club
        club = await self._club_repo.get_by_id(team.club_id)
        if not club:
            raise EntityNotFoundError(f"Club {team.club_id} not found")
        
        # 3. Load team seasons (filtered by filter_type/season/week/league)
        team_seasons = await self._load_filtered_team_seasons(query)
        
        # 4. Initialize result DTO with basic information
        result = TeamStatisticsDTO(
            team_id=team.id,
            team_name=team.name,
            club_id=club.id,
            club_name=club.name,
            filter_type=query.filter_type,
            season=query.season,
            week=query.week,
            total_games_played=0,
            total_score=0,
            average_score=0.0,
            league_average_score=0.0,
            best_score=0,
            worst_score=0,
            total_points=0.0,
            average_points=0.0,
            total_wins=0,
            total_losses=0,
            total_ties=0,
            season_progression=[],
            season_statistics=[],
            weekly_performances=[],
            best_games=[],
            worst_games=[],
            biggest_wins=[],
            biggest_losses=[],
            clutch_performance=ClutchPerformanceDTO(
                total_close_matches=0,
                wins_in_close_matches=0,
                losses_in_close_matches=0,
                ties_in_close_matches=0,
                win_rate_in_close_matches=0.0,
                threshold=query.clutch_threshold,
                opponent_summaries=[]
            ),
            position_performance=[],
            recent_form=RecentFormDTO(
                last_n_matches=0,
                form_string="",
                matches=[],
                points_in_period=0.0,
                wins_in_period=0,
                losses_in_period=0,
                ties_in_period=0,
                win_rate_in_period=0.0
            ),
            calculated_at=datetime.utcnow()
        )
        
        # 5. Load and process matches for basic statistics
        if team_seasons:
            await self._calculate_basic_statistics(
                query, result, team_seasons
            )
        
        logger.info(
            f"Retrieved statistics for team {team.id} '{team.name}' "
            f"(filter_type={query.filter_type}, team_seasons={len(team_seasons)}, "
            f"games={result.total_games_played})"
        )
        
        return result
    
    async def _calculate_basic_statistics(
        self,
        query: GetTeamStatisticsQuery,
        result: TeamStatisticsDTO,
        team_seasons: List
    ) -> None:
        """
        Calculate basic statistics (games, scores, wins/losses/ties, points).
        
        Args:
            query: The query with filter parameters
            result: The result DTO to update
            team_seasons: List of TeamSeason entities to process
        """
        from domain.entities.position_comparison import ComparisonOutcome
        from domain.entities.match import MatchStatus
        
        total_games = 0
        total_score = 0
        total_points = 0.0
        wins = 0
        losses = 0
        ties = 0
        best_score = 0
        worst_score = float('inf')
        
        # Process each team season
        for team_season in team_seasons:
            # Load matches for this team season
            matches = await self._match_repo.get_by_team(team_season.id)
            
            # Load league season and scoring system
            league_season = await self._league_season_repo.get_by_id(team_season.league_season_id)
            if not league_season:
                continue
            
            scoring_system_id = UUID(league_season.scoring_system_id)
            scoring_system = await self._scoring_system_repo.get_by_id(scoring_system_id)
            if not scoring_system:
                continue
            
            # Process each match
            for match in matches:
                # Only process completed matches
                if match.status != MatchStatus.COMPLETED:
                    continue
                
                # Determine if team is team1 or team2
                is_team1 = match.team1_team_season_id == team_season.id
                if not (is_team1 or match.team2_team_season_id == team_season.id):
                    continue
                
                # Load game results for this match
                game_results = await self._game_result_repo.get_by_match(match.id)
                team_game_results = [gr for gr in game_results if gr.team_season_id == team_season.id]
                
                # Calculate team score from game results
                match_score = sum(int(gr.score) for gr in team_game_results)
                total_score += match_score
                total_games += 1
                
                # Track best/worst scores
                if match_score > best_score:
                    best_score = match_score
                if match_score < worst_score:
                    worst_score = match_score
                
                # Determine match outcome
                opponent_team_season_id = match.team2_team_season_id if is_team1 else match.team1_team_season_id
                opponent_game_results = [gr for gr in game_results if gr.team_season_id == opponent_team_season_id]
                opponent_score = sum(int(gr.score) for gr in opponent_game_results)
                
                # Calculate team match points
                if match_score > opponent_score:
                    team_match_points = scoring_system.points_per_team_match_win
                    wins += 1
                elif opponent_score > match_score:
                    team_match_points = scoring_system.points_per_team_match_loss
                    losses += 1
                else:
                    team_match_points = scoring_system.points_per_team_match_tie
                    ties += 1
                
                # Calculate individual points from position comparisons
                position_comparisons = await self._position_comparison_repo.get_by_match(match.id)
                individual_points = 0.0
                
                for pc in position_comparisons:
                    if is_team1:
                        if pc.outcome == ComparisonOutcome.TEAM1_WIN:
                            individual_points += scoring_system.points_per_individual_match_win
                        elif pc.outcome == ComparisonOutcome.TEAM2_WIN:
                            individual_points += scoring_system.points_per_individual_match_loss
                        else:  # TIE
                            individual_points += scoring_system.points_per_individual_match_tie
                    else:  # team2
                        if pc.outcome == ComparisonOutcome.TEAM1_WIN:
                            individual_points += scoring_system.points_per_individual_match_loss
                        elif pc.outcome == ComparisonOutcome.TEAM2_WIN:
                            individual_points += scoring_system.points_per_individual_match_win
                        else:  # TIE
                            individual_points += scoring_system.points_per_individual_match_tie
                
                total_points += team_match_points + individual_points
        
        # Update result DTO
        result.total_games_played = total_games
        result.total_score = total_score
        result.average_score = total_score / total_games if total_games > 0 else 0.0
        result.best_score = best_score if best_score > 0 else 0
        result.worst_score = int(worst_score) if worst_score != float('inf') else 0
        result.total_points = total_points
        result.average_points = total_points / total_games if total_games > 0 else 0.0
        result.total_wins = wins
        result.total_losses = losses
        result.total_ties = ties
    
    async def _load_filtered_team_seasons(
        self,
        query: GetTeamStatisticsQuery
    ) -> List:
        """
        Load team seasons filtered by query parameters.
        
        Args:
            query: The query with filter parameters
        
        Returns:
            List of TeamSeason entities matching the filter
        """
        # Get all team seasons for the team
        all_team_seasons = await self._team_season_repo.get_by_team(query.team_id)
        
        # Apply filters
        filtered = []
        for team_season in all_team_seasons:
            # Filter by league if specified
            if query.league_id:
                league_season = await self._league_season_repo.get_by_id(team_season.league_season_id)
                if not league_season or league_season.league_id != query.league_id:
                    continue
            
            # Filter by season if specified
            if query.filter_type in ("season", "season_week") and query.season:
                league_season = await self._league_season_repo.get_by_id(team_season.league_season_id)
                if not league_season or league_season.season != query.season:
                    continue
            
            # Filter by week if specified (requires loading events)
            if query.filter_type == "season_week" and query.week is not None:
                # TODO: Implement week filtering
                pass
            
            filtered.append(team_season)
        
        return filtered
