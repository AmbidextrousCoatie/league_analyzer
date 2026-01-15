"""
Get League Standings Handler.

Handler for GetLeagueStandingsQuery that orchestrates domain services and repositories
to calculate and return league standings.
"""

from typing import Dict, Optional
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
from domain.entities.game import Game
from domain.entities.team import Team
from domain.entities.position_comparison import ComparisonOutcome
from domain.domain_services.standings_calculator import StandingsCalculator
from domain.value_objects.standings_status import StandingsStatus
from application.queries.league.get_league_standings_query import GetLeagueStandingsQuery
from application.dto.league_dto import (
    LeagueStandingsDTO,
    TeamStandingDTO,
    WeeklyPerformanceDTO,
    WeeklyStandingsDTO
)
from application.exceptions import EntityNotFoundError


class GetLeagueStandingsHandler:
    """
    Handler for GetLeagueStandingsQuery.
    
    Orchestrates the retrieval of league data, games, teams, and calculates
    standings using the StandingsCalculator domain service.
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
        standings_calculator: StandingsCalculator
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
            standings_calculator: Domain service for calculating standings
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
        self._calculator = standings_calculator
    
    async def _process_games_for_week(
        self,
        events: list,
        event_to_week: Dict[UUID, int],
        scoring_system,
        week_filter: Optional[int] = None
    ) -> tuple[list[Game], Dict[UUID, tuple[int, int, int]]]:
        """
        Process games for events, optionally filtered by week.
        
        Args:
            events: List of Event entities
            event_to_week: Mapping of event_id to week number
            scoring_system: ScoringSystem entity
            week_filter: Optional week number to filter by (exact match)
        
        Returns:
            Tuple of (list of Game entities, match_outcomes dict)
        """
        match_outcomes: Dict[UUID, tuple[int, int, int]] = {}
        all_games = []
        
        for event in events:
            # Filter by week if specified - only include the exact week
            if week_filter is not None:
                event_week = event_to_week.get(event.id)
                if event_week is None or event_week != week_filter:
                    continue
            
            # Load matches for this event
            matches = await self._match_repo.get_by_event(event.id)
            
            for match in matches:
                # Load game results for this match
                game_results = await self._game_result_repo.get_by_match(match.id)
                
                # Load position comparisons for this match (to get points)
                position_comparisons = await self._position_comparison_repo.get_by_match(match.id)
                
                # Build a map: (position, player_id) -> points
                # Use scoring system points for individual match outcomes
                points_map: Dict[tuple[int, UUID], float] = {}
                for pc in position_comparisons:
                    if pc.outcome == ComparisonOutcome.TEAM1_WIN:
                        points_map[(pc.position, pc.team1_player_id)] = scoring_system.points_per_individual_match_win
                        points_map[(pc.position, pc.team2_player_id)] = scoring_system.points_per_individual_match_loss
                    elif pc.outcome == ComparisonOutcome.TEAM2_WIN:
                        points_map[(pc.position, pc.team1_player_id)] = scoring_system.points_per_individual_match_loss
                        points_map[(pc.position, pc.team2_player_id)] = scoring_system.points_per_individual_match_win
                    else:  # TIE
                        points_map[(pc.position, pc.team1_player_id)] = scoring_system.points_per_individual_match_tie
                        points_map[(pc.position, pc.team2_player_id)] = scoring_system.points_per_individual_match_tie
                
                # Convert GameResult to Game entities
                # Track games by team_season_id to add team match points later
                match_games_team1: list[Game] = []
                match_games_team2: list[Game] = []
                
                # Calculate team total scores from game results
                team1_total_score = 0.0
                team2_total_score = 0.0
                
                for game_result in game_results:
                    # Get points for this player at this position (individual match points)
                    individual_points = points_map.get((game_result.position, game_result.player_id), 0.0)
                    
                    # Create Game entity with individual points
                    # Convert score to int (bowling scores are integers)
                    game = Game(
                        event_id=event.id,
                        player_id=game_result.player_id,
                        team_season_id=game_result.team_season_id,
                        position=game_result.position,
                        match_number=match.match_number,
                        round_number=match.round_number,
                        score=int(game_result.score),  # Convert to int
                        points=individual_points,  # Will add team match points below
                        handicap=game_result.handicap,
                        is_disqualified=game_result.is_disqualified
                    )
                    
                    # Track which team this game belongs to and accumulate scores
                    if game_result.team_season_id == match.team1_team_season_id:
                        match_games_team1.append(game)
                        team1_total_score += game_result.score
                    elif game_result.team_season_id == match.team2_team_season_id:
                        match_games_team2.append(game)
                        team2_total_score += game_result.score
                    
                    all_games.append(game)
                
                # Add team match points based on match outcome
                # Determine match outcome from calculated team total scores
                # Track W-L-T for each team
                if team1_total_score > team2_total_score:
                    # Team1 wins
                    team1_points = scoring_system.points_per_team_match_win
                    team2_points = scoring_system.points_per_team_match_loss
                    # Update W-L-T
                    wins1, losses1, ties1 = match_outcomes.get(match.team1_team_season_id, (0, 0, 0))
                    match_outcomes[match.team1_team_season_id] = (wins1 + 1, losses1, ties1)
                    wins2, losses2, ties2 = match_outcomes.get(match.team2_team_season_id, (0, 0, 0))
                    match_outcomes[match.team2_team_season_id] = (wins2, losses2 + 1, ties2)
                elif team2_total_score > team1_total_score:
                    # Team2 wins
                    team1_points = scoring_system.points_per_team_match_loss
                    team2_points = scoring_system.points_per_team_match_win
                    # Update W-L-T
                    wins1, losses1, ties1 = match_outcomes.get(match.team1_team_season_id, (0, 0, 0))
                    match_outcomes[match.team1_team_season_id] = (wins1, losses1 + 1, ties1)
                    wins2, losses2, ties2 = match_outcomes.get(match.team2_team_season_id, (0, 0, 0))
                    match_outcomes[match.team2_team_season_id] = (wins2 + 1, losses2, ties2)
                else:
                    # Tie
                    team1_points = scoring_system.points_per_team_match_tie
                    team2_points = scoring_system.points_per_team_match_tie
                    # Update W-L-T
                    wins1, losses1, ties1 = match_outcomes.get(match.team1_team_season_id, (0, 0, 0))
                    match_outcomes[match.team1_team_season_id] = (wins1, losses1, ties1 + 1)
                    wins2, losses2, ties2 = match_outcomes.get(match.team2_team_season_id, (0, 0, 0))
                    match_outcomes[match.team2_team_season_id] = (wins2, losses2, ties2 + 1)
                
                # Add team match points to all games for each team
                # Divide by number of players so total = team_points (not team_points * num_players)
                num_players_team1 = len(match_games_team1)
                num_players_team2 = len(match_games_team2)
                
                if num_players_team1 > 0:
                    team1_points_per_player = team1_points / num_players_team1
                    for game in match_games_team1:
                        game.update_points(game.points + team1_points_per_player)
                
                if num_players_team2 > 0:
                    team2_points_per_player = team2_points / num_players_team2
                    for game in match_games_team2:
                        game.update_points(game.points + team2_points_per_player)
        
        return all_games, match_outcomes
    
    def _map_standings_to_dto(
        self,
        standings,
        team_season_to_team: Dict[UUID, UUID],
        match_outcomes: Dict[UUID, tuple[int, int, int]]
    ) -> list[TeamStandingDTO]:
        """
        Map domain Standings to DTO.
        
        Args:
            standings: Standings domain object
            team_season_to_team: Mapping of team_season_id to team_id
            match_outcomes: Mapping of team_season_id to (wins, losses, ties)
        
        Returns:
            List of TeamStandingDTO
        """
        standing_dtos = []
        for team_standing in standings.teams:
            weekly_perf_dtos = [
                WeeklyPerformanceDTO(
                    week=wp.week,
                    score=int(wp.score),  # Convert to int
                    points=wp.points,
                    number_of_games=wp.number_of_games
                )
                for wp in team_standing.weekly_performances
            ]
            
            # Calculate wins/losses/ties from match outcomes
            # Find team_season_id for this team_id
            team_season_id = None
            for ts_id, t_id in team_season_to_team.items():
                if t_id == team_standing.team_id:
                    team_season_id = ts_id
                    break
            
            wins, losses, ties = match_outcomes.get(team_season_id, (0, 0, 0)) if team_season_id else (0, 0, 0)
            games_played = sum(wp.number_of_games for wp in team_standing.weekly_performances)
            
            # Round average_score to 1 decimal place
            average_score_rounded = round(team_standing.average_score, 1)
            
            standing_dtos.append(TeamStandingDTO(
                team_id=team_standing.team_id,
                team_name=team_standing.team_name,
                position=team_standing.position,
                total_score=int(team_standing.total_score),  # Convert to int
                total_points=team_standing.total_points,
                average_score=average_score_rounded,
                games_played=games_played,
                wins=wins,
                losses=losses,
                ties=ties,
                weekly_performances=weekly_perf_dtos
            ))
        
        return standing_dtos
    
    async def handle(self, query: GetLeagueStandingsQuery) -> LeagueStandingsDTO:
        """
        Handle GetLeagueStandingsQuery.
        
        Args:
            query: The query containing league_id, optional league_season_id and week
        
        Returns:
            LeagueStandingsDTO with standings data
        
        Raises:
            EntityNotFoundError: If league or league_season not found
            ValueError: If query parameters are invalid
        """
        # 1. Load league
        league = await self._league_repo.get_by_id(query.league_id)
        if not league:
            raise EntityNotFoundError(f"League {query.league_id} not found")
        
        # 2. Load league season
        if query.league_season_id:
            league_season = await self._league_season_repo.get_by_id(query.league_season_id)
            if not league_season:
                raise EntityNotFoundError(f"LeagueSeason {query.league_season_id} not found")
        else:
            # Get latest league season for this league
            league_seasons = await self._league_season_repo.get_by_league(query.league_id)
            if not league_seasons:
                raise EntityNotFoundError(f"No league seasons found for league {query.league_id}")
            # Sort by season (assuming season is sortable) and get latest
            league_season = sorted(league_seasons, key=lambda ls: ls.season.value, reverse=True)[0]
        
        # 2.5. Load scoring system for the league season
        scoring_system_id = UUID(league_season.scoring_system_id)
        scoring_system = await self._scoring_system_repo.get_by_id(scoring_system_id)
        if not scoring_system:
            raise EntityNotFoundError(
                f"ScoringSystem {scoring_system_id} not found for LeagueSeason {league_season.id}"
            )
        
        # 3. Load events for the league season
        events = await self._event_repo.get_by_league_season(league_season.id)
        
        if not events:
            # No events found - return empty standings
            from infrastructure.logging import get_logger
            logger = get_logger(__name__)
            logger.warning(f"No events found for league season {league_season.id}")
            # Return empty standings
            return LeagueStandingsDTO(
                league_id=league.id,
                league_name=league.name,
                league_season_id=league_season.id,
                season=league_season.season.value,
                week=query.week,
                standings=[],
                weekly_standings=[],
                status="provisional",
                calculated_at=datetime.utcnow()
            )
        
        # Build event_to_week mapping (from event.league_week)
        event_to_week: Dict[UUID, int] = {}
        for event in events:
            # Use event.league_week if available, otherwise default to 1
            week = event.league_week if event.league_week is not None else 1
            event_to_week[event.id] = week
        
        # 4. Load team seasons and build team mapping (needed for standings calculation)
        team_seasons = await self._team_season_repo.get_by_league_season(league_season.id)
        
        if not team_seasons:
            # No teams found - return empty standings
            from infrastructure.logging import get_logger
            logger = get_logger(__name__)
            logger.warning(f"No team seasons found for league season {league_season.id}")
            return LeagueStandingsDTO(
                league_id=league.id,
                league_name=league.name,
                league_season_id=league_season.id,
                season=league_season.season.value,
                week=query.week,
                standings=[],
                weekly_standings=[],
                status="provisional",
                calculated_at=datetime.utcnow()
            )
        
        # Build team_season_id to team_id mapping
        team_season_to_team: Dict[UUID, UUID] = {}
        teams: Dict[UUID, Team] = {}
        
        for team_season in team_seasons:
            # Get team from team_id
            team = await self._team_repo.get_by_id(team_season.team_id)
            if team:
                team_season_to_team[team_season.id] = team.id
                teams[team.id] = team
            else:
                from infrastructure.logging import get_logger
                logger = get_logger(__name__)
                logger.warning(f"Team {team_season.team_id} not found for team season {team_season.id}")
        
        # Ensure we have at least one valid team
        if not teams:
            from infrastructure.logging import get_logger
            logger = get_logger(__name__)
            logger.warning(f"No valid teams found for league season {league_season.id}")
            return LeagueStandingsDTO(
                league_id=league.id,
                league_name=league.name,
                league_season_id=league_season.id,
                season=league_season.season.value,
                week=query.week,
                standings=[],
                weekly_standings=[],
                status="provisional",
                calculated_at=datetime.utcnow()
            )
        
        # 5. Process games and calculate standings
        # If week is specified, only process that week; otherwise process all weeks
        if query.week is not None:
            # Single week: process games for that week only
            all_games, match_outcomes = await self._process_games_for_week(
                events, event_to_week, scoring_system, week_filter=query.week
            )
            
            # Calculate standings for this week
            standings = self._calculator.calculate_standings(
                games=all_games,
                teams=teams,
                league_season_id=league_season.id,
                up_to_week=query.week,
                team_season_to_team=team_season_to_team,
                event_to_week=event_to_week,
                status=StandingsStatus.PROVISIONAL
            )
            
            # Map to DTO
            standing_dtos = self._map_standings_to_dto(
                standings, team_season_to_team, match_outcomes
            )
            
            weekly_standings = []
        else:
            # All weeks: process all games and calculate overall standings
            all_games, match_outcomes = await self._process_games_for_week(
                events, event_to_week, scoring_system, week_filter=None
            )
            
            # Calculate overall standings
            standings = self._calculator.calculate_standings(
                games=all_games,
                teams=teams,
                league_season_id=league_season.id,
                up_to_week=None,
                team_season_to_team=team_season_to_team,
                event_to_week=event_to_week,
                status=StandingsStatus.PROVISIONAL
            )
            
            # Map overall standings to DTO
            standing_dtos = self._map_standings_to_dto(
                standings, team_season_to_team, match_outcomes
            )
            
            # Calculate weekly standings
            weekly_standings = []
            # Get all unique weeks
            unique_weeks = sorted(set(event_to_week.values()))
            
            for week in unique_weeks:
                # Process games for this week
                week_games, week_match_outcomes = await self._process_games_for_week(
                    events, event_to_week, scoring_system, week_filter=week
                )
                
                # Calculate standings for this week
                week_standings = self._calculator.calculate_standings(
                    games=week_games,
                    teams=teams,
                    league_season_id=league_season.id,
                    up_to_week=week,
                    team_season_to_team=team_season_to_team,
                    event_to_week=event_to_week,
                    status=StandingsStatus.PROVISIONAL
                )
                
                # Map to DTO
                week_standing_dtos = self._map_standings_to_dto(
                    week_standings, team_season_to_team, week_match_outcomes
                )
                
                weekly_standings.append(WeeklyStandingsDTO(
                    week=week,
                    standings=week_standing_dtos
                ))
        
        # 6. Return DTO
        return LeagueStandingsDTO(
            league_id=league.id,
            league_name=league.name,
            league_season_id=league_season.id,
            season=league_season.season.value,
            week=query.week,
            standings=standing_dtos,
            weekly_standings=weekly_standings,
            status=standings.status.value,
            calculated_at=standings.calculated_at
        )
