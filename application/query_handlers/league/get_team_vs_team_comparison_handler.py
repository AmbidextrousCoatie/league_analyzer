"""
Get Team vs Team Comparison Handler.

Handler for GetTeamVsTeamComparisonQuery that retrieves head-to-head comparison
between two teams.
"""

from typing import Dict, List
from uuid import UUID
from datetime import datetime
from domain.repositories.league_repository import LeagueRepository
from domain.repositories.league_season_repository import LeagueSeasonRepository
from domain.repositories.team_season_repository import TeamSeasonRepository
from domain.repositories.event_repository import EventRepository
from domain.repositories.match_repository import MatchRepository
from domain.repositories.game_result_repository import GameResultRepository
from domain.repositories.position_comparison_repository import PositionComparisonRepository
from domain.repositories.scoring_system_repository import ScoringSystemRepository
from domain.repositories.team_repository import TeamRepository
from domain.repositories.match_scoring_repository import MatchScoringRepository
from application.queries.league.get_team_vs_team_comparison_query import GetTeamVsTeamComparisonQuery
from application.dto.team_vs_team_comparison_dto import (
    TeamVsTeamComparisonDTO,
    MatchComparisonDTO,
    PositionComparisonDTO
)
from domain.entities.position_comparison import ComparisonOutcome
from application.exceptions import EntityNotFoundError
from infrastructure.logging import get_logger

logger = get_logger(__name__)


class GetTeamVsTeamComparisonHandler:
    """
    Handler for GetTeamVsTeamComparisonQuery.
    
    Retrieves head-to-head comparison between two teams including:
    - Overall record (wins, losses, ties)
    - Total and average scores
    - Match-by-match breakdown
    - Position-by-position statistics
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
        team_repository: TeamRepository,
        match_scoring_repository: MatchScoringRepository
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
            team_repository: Repository for Team entities
            match_scoring_repository: Repository for MatchScoring entities
        """
        self._team_season_repo = team_season_repository
        self._league_season_repo = league_season_repository
        self._league_repo = league_repository
        self._event_repo = event_repository
        self._match_repo = match_repository
        self._game_result_repo = game_result_repository
        self._position_comparison_repo = position_comparison_repository
        self._scoring_system_repo = scoring_system_repository
        self._team_repo = team_repository
        self._match_scoring_repo = match_scoring_repository
    
    async def handle(self, query: GetTeamVsTeamComparisonQuery) -> TeamVsTeamComparisonDTO:
        """
        Handle GetTeamVsTeamComparisonQuery.
        
        Args:
            query: The query containing team1_season_id and team2_season_id
        
        Returns:
            TeamVsTeamComparisonDTO with head-to-head comparison
        
        Raises:
            EntityNotFoundError: If team seasons, league season, or scoring system not found
        """
        # 1. Load both team seasons
        team1_season = await self._team_season_repo.get_by_id(query.team1_season_id)
        if not team1_season:
            raise EntityNotFoundError(f"TeamSeason {query.team1_season_id} not found")
        
        team2_season = await self._team_season_repo.get_by_id(query.team2_season_id)
        if not team2_season:
            raise EntityNotFoundError(f"TeamSeason {query.team2_season_id} not found")
        
        # 2. Verify they're in the same league season
        if team1_season.league_season_id != team2_season.league_season_id:
            raise EntityNotFoundError(
                f"Teams must be in the same league season. "
                f"Team1: {team1_season.league_season_id}, Team2: {team2_season.league_season_id}"
            )
        
        league_season_id = team1_season.league_season_id
        
        # 3. Load league season and league
        league_season = await self._league_season_repo.get_by_id(league_season_id)
        if not league_season:
            raise EntityNotFoundError(f"LeagueSeason {league_season_id} not found")
        
        league = await self._league_repo.get_by_id(league_season.league_id)
        if not league:
            raise EntityNotFoundError(f"League {league_season.league_id} not found")
        
        # 4. Load scoring system
        scoring_system_id = UUID(league_season.scoring_system_id)
        scoring_system = await self._scoring_system_repo.get_by_id(scoring_system_id)
        if not scoring_system:
            raise EntityNotFoundError(
                f"ScoringSystem {scoring_system_id} not found for LeagueSeason {league_season_id}"
            )
        
        # 5. Get team names
        team1 = await self._team_repo.get_by_id(team1_season.team_id)
        if not team1:
            raise EntityNotFoundError(f"Team {team1_season.team_id} not found")
        team1_name = team1.name
        
        team2 = await self._team_repo.get_by_id(team2_season.team_id)
        if not team2:
            raise EntityNotFoundError(f"Team {team2_season.team_id} not found")
        team2_name = team2.name
        
        # 6. Find all matches between these two teams
        # Load all events for this league season
        events = await self._event_repo.get_by_league_season(league_season_id)
        event_ids = [e.id for e in events]
        
        # Find matches where these teams played each other
        head_to_head_matches = []
        for event_id in event_ids:
            matches = await self._match_repo.get_by_event(event_id)
            for match in matches:
                # Check if this match is between the two teams (in either order)
                if ((match.team1_team_season_id == query.team1_season_id and 
                     match.team2_team_season_id == query.team2_season_id) or
                    (match.team1_team_season_id == query.team2_season_id and 
                     match.team2_team_season_id == query.team1_season_id)):
                    head_to_head_matches.append(match)
        
        # Sort matches by event, round, and match number
        event_dict = {e.id: e for e in events}
        head_to_head_matches.sort(
            key=lambda m: (
                event_dict.get(m.event_id, events[0]).league_week or 0,
                m.round_number,
                m.match_number
            )
        )
        
        # 7. Process each match and calculate statistics
        match_comparisons: List[MatchComparisonDTO] = []
        team1_wins = 0
        team2_wins = 0
        ties = 0
        team1_total_score = 0
        team2_total_score = 0
        team1_total_match_points = 0.0
        team2_total_match_points = 0.0
        team1_total_individual_points = 0.0
        team2_total_individual_points = 0.0
        
        # Position-by-position tracking
        position_stats: Dict[int, Dict[str, int]] = {}
        for pos in range(4):
            position_stats[pos] = {
                'team1_wins': 0,
                'team2_wins': 0,
                'ties': 0,
                'team1_total_score': 0,
                'team2_total_score': 0,
                'team1_total_points': 0.0,
                'team2_total_points': 0.0,
                'team1_count': 0,
                'team2_count': 0
            }
        
        for match in head_to_head_matches:
            # Determine which team is team1 and which is team2 in this match
            is_team1_first = match.team1_team_season_id == query.team1_season_id
            
            # Load game results
            game_results = await self._game_result_repo.get_by_match(match.id)
            team1_results = [gr for gr in game_results if gr.team_season_id == query.team1_season_id]
            team2_results = [gr for gr in game_results if gr.team_season_id == query.team2_season_id]
            
            # Calculate team totals
            team1_match_score = sum(int(gr.score) for gr in team1_results)
            team2_match_score = sum(int(gr.score) for gr in team2_results)
            team1_total_score += team1_match_score
            team2_total_score += team2_match_score
            
            # Determine match outcome
            if team1_match_score > team2_match_score:
                team1_match_points = scoring_system.points_per_team_match_win
                team2_match_points = scoring_system.points_per_team_match_loss
                result = "team1_win"
                team1_wins += 1
            elif team2_match_score > team1_match_score:
                team1_match_points = scoring_system.points_per_team_match_loss
                team2_match_points = scoring_system.points_per_team_match_win
                result = "team2_win"
                team2_wins += 1
            else:
                team1_match_points = scoring_system.points_per_team_match_tie
                team2_match_points = scoring_system.points_per_team_match_tie
                result = "tie"
                ties += 1
            
            team1_total_match_points += team1_match_points
            team2_total_match_points += team2_match_points
            
            # Calculate individual points from position comparisons
            position_comparisons = await self._position_comparison_repo.get_by_match(match.id)
            team1_individual_points = 0.0
            team2_individual_points = 0.0
            
            for pos_comp in position_comparisons:
                if is_team1_first:
                    # Team1 is team1 in the match, team2 is team2
                    if pos_comp.outcome == ComparisonOutcome.TEAM1_WIN:
                        team1_individual_points += scoring_system.points_per_individual_match_win
                        team2_individual_points += scoring_system.points_per_individual_match_loss
                    elif pos_comp.outcome == ComparisonOutcome.TEAM2_WIN:
                        team1_individual_points += scoring_system.points_per_individual_match_loss
                        team2_individual_points += scoring_system.points_per_individual_match_win
                    else:  # TIE
                        team1_individual_points += scoring_system.points_per_individual_match_tie
                        team2_individual_points += scoring_system.points_per_individual_match_tie
                else:
                    # Teams are swapped in the match
                    if pos_comp.outcome == ComparisonOutcome.TEAM1_WIN:
                        team2_individual_points += scoring_system.points_per_individual_match_win
                        team1_individual_points += scoring_system.points_per_individual_match_loss
                    elif pos_comp.outcome == ComparisonOutcome.TEAM2_WIN:
                        team2_individual_points += scoring_system.points_per_individual_match_loss
                        team1_individual_points += scoring_system.points_per_individual_match_win
                    else:  # TIE
                        team1_individual_points += scoring_system.points_per_individual_match_tie
                        team2_individual_points += scoring_system.points_per_individual_match_tie
            
            team1_total_individual_points += team1_individual_points
            team2_total_individual_points += team2_individual_points
            
            # Get event for league week
            event = event_dict.get(match.event_id)
            league_week = event.league_week if event else None
            
            # Build match comparison DTO
            match_comparisons.append(MatchComparisonDTO(
                match_id=match.id,
                event_id=match.event_id,
                league_week=league_week,
                round_number=match.round_number,
                match_number=match.match_number,
                team1_total_score=team1_match_score,
                team2_total_score=team2_match_score,
                team1_match_points=team1_match_points,
                team2_match_points=team2_match_points,
                team1_individual_points=team1_individual_points,
                team2_individual_points=team2_individual_points,
                team1_total_points=team1_match_points + team1_individual_points,
                team2_total_points=team2_match_points + team2_individual_points,
                result=result,
                date=event.date if event else None
            ))
            
            # Process position-by-position statistics (position_comparisons already loaded above)
            for position in range(4):
                team1_gr = next((gr for gr in team1_results if gr.position == position), None)
                team2_gr = next((gr for gr in team2_results if gr.position == position), None)
                
                if team1_gr:
                    position_stats[position]['team1_total_score'] += int(team1_gr.score)
                    position_stats[position]['team1_count'] += 1
                
                if team2_gr:
                    position_stats[position]['team2_total_score'] += int(team2_gr.score)
                    position_stats[position]['team2_count'] += 1
                
                # Find position comparison
                pos_comp = next((pc for pc in position_comparisons if pc.position == position), None)
                if pos_comp:
                    # Determine which team won based on match order
                    if is_team1_first:
                        if pos_comp.outcome == ComparisonOutcome.TEAM1_WIN:
                            position_stats[position]['team1_wins'] += 1
                            position_stats[position]['team1_total_points'] += scoring_system.points_per_individual_match_win
                            position_stats[position]['team2_total_points'] += scoring_system.points_per_individual_match_loss
                        elif pos_comp.outcome == ComparisonOutcome.TEAM2_WIN:
                            position_stats[position]['team2_wins'] += 1
                            position_stats[position]['team1_total_points'] += scoring_system.points_per_individual_match_loss
                            position_stats[position]['team2_total_points'] += scoring_system.points_per_individual_match_win
                        else:  # TIE
                            position_stats[position]['ties'] += 1
                            position_stats[position]['team1_total_points'] += scoring_system.points_per_individual_match_tie
                            position_stats[position]['team2_total_points'] += scoring_system.points_per_individual_match_tie
                    else:
                        # Teams are swapped
                        if pos_comp.outcome == ComparisonOutcome.TEAM1_WIN:
                            position_stats[position]['team2_wins'] += 1
                            position_stats[position]['team1_total_points'] += scoring_system.points_per_individual_match_loss
                            position_stats[position]['team2_total_points'] += scoring_system.points_per_individual_match_win
                        elif pos_comp.outcome == ComparisonOutcome.TEAM2_WIN:
                            position_stats[position]['team1_wins'] += 1
                            position_stats[position]['team1_total_points'] += scoring_system.points_per_individual_match_win
                            position_stats[position]['team2_total_points'] += scoring_system.points_per_individual_match_loss
                        else:  # TIE
                            position_stats[position]['ties'] += 1
                            position_stats[position]['team1_total_points'] += scoring_system.points_per_individual_match_tie
                            position_stats[position]['team2_total_points'] += scoring_system.points_per_individual_match_tie
        
        # Build position comparison DTOs
        position_comparisons_dto: List[PositionComparisonDTO] = []
        for position in range(4):
            stats = position_stats[position]
            team1_avg = stats['team1_total_score'] / stats['team1_count'] if stats['team1_count'] > 0 else 0.0
            team2_avg = stats['team2_total_score'] / stats['team2_count'] if stats['team2_count'] > 0 else 0.0
            
            position_comparisons_dto.append(PositionComparisonDTO(
                position=position,
                team1_wins=stats['team1_wins'],
                team2_wins=stats['team2_wins'],
                ties=stats['ties'],
                team1_total_score=stats['team1_total_score'],
                team2_total_score=stats['team2_total_score'],
                team1_average_score=team1_avg,
                team2_average_score=team2_avg,
                team1_total_points=stats['team1_total_points'],
                team2_total_points=stats['team2_total_points']
            ))
        
        # Calculate averages
        matches_played = len(head_to_head_matches)
        team1_avg_score = team1_total_score / matches_played if matches_played > 0 else 0.0
        team2_avg_score = team2_total_score / matches_played if matches_played > 0 else 0.0
        
        # Build final DTO
        return TeamVsTeamComparisonDTO(
            team1_season_id=query.team1_season_id,
            team1_name=team1_name,
            team2_season_id=query.team2_season_id,
            team2_name=team2_name,
            league_season_id=league_season_id,
            league_name=league.name,
            season=str(league_season.season),
            matches_played=matches_played,
            team1_wins=team1_wins,
            team2_wins=team2_wins,
            ties=ties,
            team1_total_score=team1_total_score,
            team2_total_score=team2_total_score,
            team1_average_score=team1_avg_score,
            team2_average_score=team2_avg_score,
            team1_total_match_points=team1_total_match_points,
            team2_total_match_points=team2_total_match_points,
            team1_total_individual_points=team1_total_individual_points,
            team2_total_individual_points=team2_total_individual_points,
            team1_total_points=team1_total_match_points + team1_total_individual_points,
            team2_total_points=team2_total_match_points + team2_total_individual_points,
            matches=match_comparisons,
            position_comparisons=position_comparisons_dto,
            calculated_at=datetime.utcnow()
        )
