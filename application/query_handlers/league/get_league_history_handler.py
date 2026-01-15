"""
Get League History Handler.

Handler for GetLeagueHistoryQuery that retrieves historical data for a league
across all seasons, including season summaries, top performers, and all-time records.
"""

from typing import Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime
from domain.repositories.league_repository import LeagueRepository
from domain.repositories.league_season_repository import LeagueSeasonRepository
from domain.repositories.event_repository import EventRepository
from domain.repositories.match_repository import MatchRepository
from domain.repositories.game_result_repository import GameResultRepository
from domain.repositories.position_comparison_repository import PositionComparisonRepository
from domain.repositories.team_season_repository import TeamSeasonRepository
from domain.repositories.team_repository import TeamRepository
from domain.repositories.club_repository import ClubRepository
from domain.repositories.scoring_system_repository import ScoringSystemRepository
from domain.repositories.player_repository import PlayerRepository
from domain.entities.game import Game
from domain.entities.game_result import GameResult
from application.queries.league.get_league_history_query import GetLeagueHistoryQuery
from application.queries.league.get_league_standings_query import GetLeagueStandingsQuery
from application.query_handlers.league.get_league_standings_handler import GetLeagueStandingsHandler
from application.dto.league_dto import (
    LeagueHistoryDTO,
    SeasonSummaryDTO,
    TopThreeDTO,
    TeamStandingDTO,
    AllTimeRecordDTO
)
from application.exceptions import EntityNotFoundError


class GetLeagueHistoryHandler:
    """
    Handler for GetLeagueHistoryQuery.
    
    Orchestrates the retrieval of historical league data across all seasons,
    including season summaries, top performers, and all-time records.
    """
    
    def __init__(
        self,
        league_repository: LeagueRepository,
        league_season_repository: LeagueSeasonRepository,
        event_repository: EventRepository,
        match_repository: MatchRepository,
        game_result_repository: GameResultRepository,
        position_comparison_repository: PositionComparisonRepository,
        team_season_repository: TeamSeasonRepository,
        team_repository: TeamRepository,
        club_repository: ClubRepository,
        scoring_system_repository: ScoringSystemRepository,
        player_repository: PlayerRepository,
        standings_handler: GetLeagueStandingsHandler
    ):
        """
        Initialize handler with required repositories and services.
        
        Args:
            league_repository: Repository for League entities
            league_season_repository: Repository for LeagueSeason entities
            event_repository: Repository for Event entities
            match_repository: Repository for Match entities
            game_result_repository: Repository for GameResult entities
            position_comparison_repository: Repository for PositionComparison entities
            team_season_repository: Repository for TeamSeason entities
            team_repository: Repository for Team entities
            club_repository: Repository for Club entities
            scoring_system_repository: Repository for ScoringSystem entities
            player_repository: Repository for Player entities
            standings_handler: Handler for calculating standings (reused for each season)
        """
        self._league_repo = league_repository
        self._league_season_repo = league_season_repository
        self._event_repo = event_repository
        self._match_repo = match_repository
        self._game_result_repo = game_result_repository
        self._position_comparison_repo = position_comparison_repository
        self._team_season_repo = team_season_repository
        self._team_repo = team_repository
        self._club_repo = club_repository
        self._scoring_system_repo = scoring_system_repository
        self._player_repo = player_repository
        self._standings_handler = standings_handler
    
    async def handle(self, query: GetLeagueHistoryQuery) -> LeagueHistoryDTO:
        """
        Handle GetLeagueHistoryQuery.
        
        Args:
            query: The query containing league_id
        
        Returns:
            LeagueHistoryDTO with historical data
        
        Raises:
            EntityNotFoundError: If league not found
        """
        # 1. Load league
        league = await self._league_repo.get_by_id(query.league_id)
        if not league:
            raise EntityNotFoundError(f"League with id {query.league_id} not found")
        
        # 2. Get all league seasons for this league
        league_seasons = await self._league_season_repo.get_by_league(query.league_id)
        if not league_seasons:
            # Return empty history if no seasons found
            return LeagueHistoryDTO(
                league_id=query.league_id,
                league_name=league.name,
                first_season=None,
                most_recent_season=None,
                total_seasons=0,
                season_summaries=[],
                league_average_trend=[],
                all_time_records=[],
                calculated_at=datetime.utcnow()
            )
        
        # Sort league seasons by season (oldest first)
        league_seasons.sort(key=lambda ls: (
            ls.season.get_start_year() or 0,
            ls.season.get_end_year() or 0
        ))
        
        # 3. Process each season to get summaries
        season_summaries: List[SeasonSummaryDTO] = []
        league_average_trend: List[float] = []
        all_time_records: Dict[str, List[AllTimeRecordDTO]] = {}  # Track top 10 records per category
        
        for league_season in league_seasons:
            summary = await self._process_season(league_season, query.league_id)
            if summary:
                season_summaries.append(summary)
                league_average_trend.append(summary.league_average)
                
                # Update all-time records from this season
                await self._update_all_time_records(
                    league_season, summary, all_time_records
                )
        
        # 4. Determine first and most recent seasons
        first_season = str(league_seasons[0].season) if league_seasons else None
        most_recent_season = str(league_seasons[-1].season) if league_seasons else None
        
        # 5. Sort and limit to top 10 per category
        sorted_records: List[AllTimeRecordDTO] = []
        for record_key in sorted(all_time_records.keys()):  # Sort categories alphabetically
            records = all_time_records[record_key]
            # Sort by value descending and take top 10
            sorted_category = sorted(records, key=lambda r: r.value, reverse=True)[:10]
            sorted_records.extend(sorted_category)
        
        return LeagueHistoryDTO(
            league_id=query.league_id,
            league_name=league.name,
            first_season=first_season,
            most_recent_season=most_recent_season,
            total_seasons=len(season_summaries),
            season_summaries=season_summaries,
            league_average_trend=league_average_trend,
            all_time_records=sorted_records,
            calculated_at=datetime.utcnow()
        )
    
    async def _process_season(
        self,
        league_season,
        league_id: UUID
    ) -> Optional[SeasonSummaryDTO]:
        """
        Process a single season to get summary data.
        
        Args:
            league_season: LeagueSeason entity
            league_id: UUID of the league
        
        Returns:
            SeasonSummaryDTO or None if season has no data
        """
        # Use standings handler to get standings for this season
        standings_query = GetLeagueStandingsQuery(
            league_id=league_id,
            league_season_id=league_season.id,
            week=None  # Get all weeks
        )
        
        try:
            standings_dto = await self._standings_handler.handle(standings_query)
        except Exception:
            # If we can't get standings for this season, skip it
            return None
        
        if not standings_dto.standings:
            return None
        
        # Extract top 3 teams
        sorted_standings = sorted(
            standings_dto.standings,
            key=lambda s: (s.total_points, s.total_score),
            reverse=True
        )
        
        top_three = TopThreeDTO(
            first_place=sorted_standings[0] if len(sorted_standings) > 0 else None,
            second_place=sorted_standings[1] if len(sorted_standings) > 1 else None,
            third_place=sorted_standings[2] if len(sorted_standings) > 2 else None
        )
        
        # Calculate league-wide average
        total_score = sum(s.total_score for s in standings_dto.standings)
        total_games = sum(s.games_played for s in standings_dto.standings)
        league_average = total_score / total_games if total_games > 0 else 0.0
        
        # Count number of weeks (from weekly_standings)
        number_of_weeks = len(standings_dto.weekly_standings) if standings_dto.weekly_standings else 0
        
        return SeasonSummaryDTO(
            season=standings_dto.season,
            year=league_season.season.get_start_year() or 0,
            league_season_id=league_season.id,
            top_three=top_three,
            league_average=round(league_average, 1),
            number_of_teams=len(standings_dto.standings),
            number_of_weeks=number_of_weeks,
            number_of_games=total_games
        )
    
    async def _update_all_time_records(
        self,
        league_season,
        season_summary: SeasonSummaryDTO,
        all_time_records: Dict[str, List[AllTimeRecordDTO]]
    ) -> None:
        """
        Update all-time records based on this season's data.
        
        Args:
            league_season: LeagueSeason entity
            season_summary: SeasonSummaryDTO for this season
            all_time_records: Dictionary to update with new records
        """
        # 1. Team season average (highest average_score from top teams)
        if season_summary.top_three.first_place:
            record_key = "team_season_avg"
            if record_key not in all_time_records:
                all_time_records[record_key] = []
            all_time_records[record_key].append(AllTimeRecordDTO(
                record_type=record_key,
                value=season_summary.top_three.first_place.average_score,
                holder_id=season_summary.top_three.first_place.team_id,
                holder_name=season_summary.top_three.first_place.team_name,
                season=season_summary.season,
                league_season_id=league_season.id,
                date=None,
                week=None
            ))
        
        # 2. Team game (highest single game/event score) - check weekly performances
        await self._update_team_game_record(
            league_season, season_summary, all_time_records
        )
        
        # 3-5. Individual records - process games for this season
        await self._update_individual_records(
            league_season, season_summary, all_time_records
        )
    
    async def _update_team_game_record(
        self,
        league_season,
        season_summary: SeasonSummaryDTO,
        all_time_records: Dict[str, List[AllTimeRecordDTO]]
    ) -> None:
        """
        Update team game record (highest single event/match score per team).
        
        Args:
            league_season: LeagueSeason entity
            season_summary: SeasonSummaryDTO for this season
            all_time_records: Dictionary to update with new records
        """
        # Get all events for this league season
        events = await self._event_repo.get_by_league_season(league_season.id)
        if not events:
            return
        
        record_key = "team_game"
        if record_key not in all_time_records:
            all_time_records[record_key] = []
        
        # Track team scores per event/match
        team_event_scores: List[Tuple[UUID, str, float, float, int, Optional[datetime]]] = []
        # (team_id, team_name, total_score, avg_score, week, event_date)
        
        for event in events:
            # Get matches for this event
            matches = await self._match_repo.get_by_event(event.id)
            
            for match in matches:
                # Get game results for this match
                game_results = await self._game_result_repo.get_by_match(match.id)
                
                # Group by team_season_id
                team_scores: Dict[UUID, List[float]] = {}
                team_season_to_team: Dict[UUID, UUID] = {}
                
                for game_result in game_results:
                    ts_id = game_result.team_season_id
                    if ts_id not in team_scores:
                        team_scores[ts_id] = []
                        # Get team_id from team_season
                        team_season = await self._team_season_repo.get_by_id(ts_id)
                        if team_season:
                            team_season_to_team[ts_id] = team_season.team_id
                    team_scores[ts_id].append(game_result.score)
                
                # Calculate total and average per team for this match
                for ts_id, scores in team_scores.items():
                    if ts_id in team_season_to_team:
                        team_id = team_season_to_team[ts_id]
                        team = await self._team_repo.get_by_id(team_id)
                        team_name = team.name if team else "Unknown"
                        total_score = sum(scores)
                        avg_score = total_score / len(scores) if scores else 0.0
                        
                        team_event_scores.append((
                            team_id,
                            team_name,
                            total_score,
                            avg_score,
                            event.league_week,
                            event.date
                        ))
        
        # Add all team event scores to records (convert total_score to int)
        for team_id, team_name, total_score, avg_score, week, event_date in team_event_scores:
            all_time_records[record_key].append(AllTimeRecordDTO(
                record_type=record_key,
                value=float(int(total_score)),  # Convert to int, then back to float for DTO
                holder_id=team_id,
                holder_name=team_name,
                season=season_summary.season,
                league_season_id=league_season.id,
                date=event_date,
                week=week,
                average_score=avg_score
            ))
    
    async def _update_individual_records(
        self,
        league_season,
        season_summary: SeasonSummaryDTO,
        all_time_records: Dict[str, List[AllTimeRecordDTO]]
    ) -> None:
        """
        Update individual player records.
        
        Args:
            league_season: LeagueSeason entity
            season_summary: SeasonSummaryDTO for this season
            all_time_records: Dictionary to update with new records
        """
        # Get all events for this league season
        events = await self._event_repo.get_by_league_season(league_season.id)
        if not events:
            return
        
        # Get all game results for these events (via matches)
        # Use GameResultRepository instead of GameRepository (which accesses outdated game.csv)
        all_game_results: List[GameResult] = []
        
        for event in events:
            # Get matches for this event
            matches = await self._match_repo.get_by_event(event.id)
            for match in matches:
                # Get game results for this match
                match_game_results = await self._game_result_repo.get_by_match(match.id)
                all_game_results.extend(match_game_results)
        
        if not all_game_results:
            return
        
        # Process game results by player
        player_stats: Dict[UUID, Dict[str, float]] = {}  # player_id -> stats
        player_names: Dict[UUID, str] = {}  # player_id -> name
        player_weekly_stats: Dict[UUID, Dict[int, List[float]]] = {}  # player_id -> week -> scores
        
        for game_result in all_game_results:
            player_id = game_result.player_id
            if not player_id:
                continue
            
            # Get player name
            if player_id not in player_names:
                player = await self._player_repo.get_by_id(player_id)
                player_names[player_id] = player.name if player else "Unknown"
            
            # Initialize player stats if needed
            if player_id not in player_stats:
                player_stats[player_id] = {
                    'total_score': 0.0,
                    'games': 0,
                    'max_score': 0.0
                }
                player_weekly_stats[player_id] = {}
            
            stats = player_stats[player_id]
            stats['total_score'] += game_result.score
            stats['games'] += 1
            stats['max_score'] = max(stats['max_score'], game_result.score)
            
            # Track weekly scores (simplified - would need proper week mapping from event)
            # For now, we'll extract week from event if available
            # This is a placeholder - proper implementation would need event.week or similar
        
        # Update individual season average record
        record_key = "individual_season_avg"
        if record_key not in all_time_records:
            all_time_records[record_key] = []
        
        for player_id, stats in player_stats.items():
            if stats['games'] > 0:
                avg_score = stats['total_score'] / stats['games']
                all_time_records[record_key].append(AllTimeRecordDTO(
                    record_type=record_key,
                    value=round(avg_score, 1),
                    holder_id=player_id,
                    holder_name=player_names.get(player_id, "Unknown"),
                    season=season_summary.season,
                    league_season_id=league_season.id,
                    date=None,
                    week=None,
                    average_score=None
                ))
        
        # Update individual game record (convert to int)
        record_key = "individual_game"
        if record_key not in all_time_records:
            all_time_records[record_key] = []
        
        for player_id, stats in player_stats.items():
            all_time_records[record_key].append(AllTimeRecordDTO(
                record_type=record_key,
                value=float(int(stats['max_score'])),  # Convert to int, then back to float for DTO
                holder_id=player_id,
                holder_name=player_names.get(player_id, "Unknown"),
                season=season_summary.season,
                league_season_id=league_season.id,
                date=None,
                week=None,
                average_score=None
            ))
        
        # Note: Individual week average would require proper week tracking from events
        # This is deferred until we have proper week information in events
