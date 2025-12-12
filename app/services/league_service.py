from typing import List, Dict, Any, Optional, Union
import datetime
import pandas as pd

from data_access.adapters.data_adapter_factory import DataAdapterFactory, DataAdapterSelector
from data_access.models.league_models import LeagueQuery, TeamSeasonPerformance, LeagueStandings, TeamWeeklyPerformance
from app.services.i18n_service import i18n_service
from app.models.table_data import TableData, ColumnGroup, Column, PlotData, TileData
from app.services.statistics_service import StatisticsService
from app.models.statistics_models import LeagueStatistics, LeagueResults
from app.models.series_data import SeriesData
from data_access.schema import Columns
from itertools import accumulate
from app.config.debug_config import debug_config
from app.utils.color_constants import get_theme_color, get_heat_map_color
from app.utils.league_utils import (
    format_float_one_decimal,
    get_league_level,
    convert_to_simple_types,
    apply_heat_map_to_columns
)
# from data_access.series_data import calculate_series_data, get_player_series_data, get_team_series_data


class LeagueService:
    def __init__(self, adapter_type=DataAdapterSelector.PANDAS, database: str = None):
        self.database = database
        self.adapter = DataAdapterFactory.create_adapter(adapter_type, database=database)
        self.stats_service = StatisticsService(database=database)
        
        # Register this adapter with DataManager for automatic refresh
        try:
            from app.services.data_manager import DataManager
            data_manager = DataManager()
            data_manager.register_server_instance(self)
        except ImportError:
            # DataManager not available, continue without registration
            pass

    def refresh_data_adapter(self, database: str = None):
        """Refresh the data adapter with the current data source"""
        if database:
            self.database = database
        debug_config.log_service('LeagueService', 'refresh_adapter', f"database={self.database}")
        self.adapter = DataAdapterFactory.create_adapter(DataAdapterSelector.PANDAS, database=self.database)

    def get_available_weeks(self, season: str, league: str) -> List[int]:
        """Get available weeks for a season and league"""
        return self.adapter.get_weeks(season, league)
    
    def get_latest_week(self, season: str, league: str) -> int:
        """Get the latest week number for a season and league"""
        weeks = self.get_available_weeks(season, league)
        return max(weeks) if weeks else 1
    
    def get_seasons(self, league_name: str=None, team_name: str=None) -> List[str]:
        """Get all available seasons"""
        # print(f"####################### Getting seasons for league_name: {league_name} and team_name: {team_name}")
        return self.adapter.get_seasons(league_name=league_name, team_name=team_name)

    def get_leagues(self) -> List[str]:
        """Get all available leagues for a season"""
        return self.adapter.get_leagues()
    
    def get_available_rounds(self, season: str, league: str, week: int) -> List[int]:
        """Get available rounds (games) for a season, league, and week"""
        filters = {
            Columns.season: {'value': season, 'operator': 'eq'},
            Columns.league_name: {'value': league, 'operator': 'eq'},
            Columns.week: {'value': week, 'operator': 'eq'}
        }
        
        data = self.adapter.get_filtered_data(filters=filters)
        
        if data.empty or Columns.round_number not in data.columns:
            return []
        
        # Get unique round numbers, filter out empty/NaN values, and sort
        rounds_series = data[Columns.round_number].dropna()
        # Filter out empty strings and convert to int
        rounds = []
        for r in rounds_series.unique():
            try:
                r_str = str(r).strip()
                if r_str != '' and r_str.lower() != 'nan':
                    rounds.append(int(float(r_str)))  # Use float first to handle "1.0" strings
            except (ValueError, TypeError):
                continue
        
        return sorted(set(rounds))  # Remove duplicates and sort

    def get_game_overview_data(self, season: str, league: str, week: int, round_number: int) -> TableData:
        """
        Get game overview data for a specific round.
        Shows all matches with team vs opponent: team name, team pins, team points | opponent points, opponent pins, opponent name
        
        Args:
            season: Season identifier
            league: League name
            week: Week number
            round_number: Round/Game number
            
        Returns:
            TableData with column groups for Team and Opponent
        """
        try:
            # Get team totals for this round
            filters = {
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.week: {'value': week, 'operator': 'eq'},
                Columns.round_number: {'value': round_number, 'operator': 'eq'},
                Columns.computed_data: {'value': True, 'operator': 'eq'}  # Team totals
            }
            
            team_totals = self.adapter.get_filtered_data(filters=filters)
            
            if team_totals.empty:
                return TableData(
                    columns=[],
                    data=[],
                    title=f"{i18n_service.get_text('no_data_available')} - {i18n_service.get_text('game')} {round_number}"
                )
            
            # Get league standings to determine team positions
            standings = self.get_league_standings(season, league, week)
            team_positions = {}
            if standings and standings.teams:
                for team in standings.teams:
                    team_positions[team.team_name] = team.position
            
            # Create column groups
            columns = [
                ColumnGroup(
                    title=i18n_service.get_text("team"),
                    frozen="left",
                    style={"backgroundColor": get_theme_color("background")},
                    columns=[
                        Column(title=i18n_service.get_text("position"), field="team_position", width="60px", align="center", tooltip=i18n_service.get_text("position"), decimal_places=0),
                        Column(title=i18n_service.get_text("team"), field="team_name", width="200px", align="left"),
                        Column(title=i18n_service.get_text("pins"), field="team_pins", width="80px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("points"), field="team_points", width="80px", align="center", decimal_places=0)
                    ]
                ),
                ColumnGroup(
                    title=i18n_service.get_text("opponent"),
                    style={"backgroundColor": get_theme_color("surface_light")},
                    columns=[
                        Column(title=i18n_service.get_text("points"), field="opponent_points", width="80px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("pins"), field="opponent_pins", width="80px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("position"), field="opponent_position", width="60px", align="center", tooltip=i18n_service.get_text("position"), decimal_places=0),
                        Column(title=i18n_service.get_text("opponent"), field="opponent_name", width="200px", align="left")
                    ]
                )
            ]
            
            # Get individual player points for this round to add to team points
            individual_filters = {
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.week: {'value': week, 'operator': 'eq'},
                Columns.round_number: {'value': round_number, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}  # Individual player data
            }
            
            individual_data = self.adapter.get_filtered_data(filters=individual_filters)
            
            # Calculate individual points per team
            individual_points_by_team = {}
            if not individual_data.empty:
                for team in individual_data[Columns.team_name].unique():
                    team_individual = individual_data[individual_data[Columns.team_name] == team]
                    individual_points_by_team[team] = float(team_individual[Columns.points].sum()) if pd.notna(team_individual[Columns.points].sum()) else 0.0
            
            # Build data rows - group by team to find their opponent
            data = []
            processed_teams = set()
            
            for _, row in team_totals.iterrows():
                team_name = row[Columns.team_name]
                if team_name in processed_teams:
                    continue
                    
                opponent_name = row[Columns.team_name_opponent]
                team_pins = int(row[Columns.score]) if pd.notna(row[Columns.score]) else 0
                team_points = float(row[Columns.points]) if pd.notna(row[Columns.points]) else 0.0
                
                # Add individual points to team points
                individual_points = individual_points_by_team.get(team_name, 0.0)
                total_team_points = team_points + individual_points
                
                # Find opponent's totals
                opponent_row = team_totals[
                    (team_totals[Columns.team_name] == opponent_name) &
                    (team_totals[Columns.team_name_opponent] == team_name)
                ]
                
                if not opponent_row.empty:
                    opponent_pins = int(opponent_row[Columns.score].iloc[0]) if pd.notna(opponent_row[Columns.score].iloc[0]) else 0
                    opponent_team_points = float(opponent_row[Columns.points].iloc[0]) if pd.notna(opponent_row[Columns.points].iloc[0]) else 0.0
                    # Add opponent individual points
                    opponent_individual_points = individual_points_by_team.get(opponent_name, 0.0)
                    total_opponent_points = opponent_team_points + opponent_individual_points
                else:
                    opponent_pins = 0
                    total_opponent_points = 0.0
                
                # Get positions for both teams
                team_position = team_positions.get(team_name, None)
                opponent_position = team_positions.get(opponent_name, None)
                
                data.append([
                    team_position if team_position is not None else '',
                    team_name,
                    team_pins,
                    total_team_points,
                    total_opponent_points,
                    opponent_pins,
                    opponent_position if opponent_position is not None else '',
                    opponent_name
                ])
                
                processed_teams.add(team_name)
                processed_teams.add(opponent_name)
            
            # Heatmap coloring is now handled in the frontend
            return TableData(
                columns=columns,
                data=data,
                title=f"{league} - {i18n_service.get_text('week')} {week}, {i18n_service.get_text('game')} {round_number}",
                description=f"{i18n_service.get_text('match_results')} {season}",
                config={
                    "stickyHeader": True,
                    "striped": True,
                    "hover": True,
                    "responsive": True,
                    "compact": False,
                    "stripedColGroups": True
                }
            )
            
        except Exception as e:
            print(f"Error in get_game_overview_data: {e}")
            import traceback
            traceback.print_exc()
            return TableData(
                columns=[],
                data=[],
                title=f"Error loading game overview data"
            )

    def get_game_team_details_data(self, season: str, league: str, week: int, team: str, round_number: int) -> TableData:
        """
        Get game team details data for a specific team in a specific round.
        Shows individual player scores: Points, Player Name, Player Pins, Opponent Pins, Opponent Name
        Last row contains accumulated totals.
        
        Args:
            season: Season identifier
            league: League name
            week: Week number
            team: Team name
            round_number: Round/Game number
            
        Returns:
            TableData with player rows and totals row
        """
        try:
            print(f"get_game_team_details_data: season={season}, league={league}, week={week}, team={team}, round={round_number}")
            # Get individual player data for this team and round
            player_filters = {
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.week: {'value': week, 'operator': 'eq'},
                Columns.team_name: {'value': team, 'operator': 'eq'},
                Columns.round_number: {'value': round_number, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}  # Individual player data
            }
            
            player_data = self.adapter.get_filtered_data(filters=player_filters)
            print(f"get_game_team_details_data: Found {len(player_data)} player rows")
            
            if player_data.empty:
                print(f"get_game_team_details_data: No player data found")
                return TableData(
                    columns=[],
                    data=[],
                    title=f"{i18n_service.get_text('no_data_available')} - {team}, {i18n_service.get_text('game')} {round_number}"
                )
            
            # Get opponent team name from first row
            if Columns.team_name_opponent not in player_data.columns:
                print(f"get_game_team_details_data: Column {Columns.team_name_opponent} not found in player_data")
                return TableData(
                    columns=[],
                    data=[],
                    title=f"{i18n_service.get_text('no_data_available')} - {team}, {i18n_service.get_text('game')} {round_number} (missing opponent column)"
                )
            
            # Extract opponent name and handle various edge cases
            opponent_name_raw = player_data[Columns.team_name_opponent].iloc[0] if not player_data.empty else ""
            # Convert to string and handle NaN/None values
            if pd.isna(opponent_name_raw) or opponent_name_raw is None:
                opponent_name = ""
            else:
                opponent_name = str(opponent_name_raw).strip()
            
            print(f"get_game_team_details_data: Opponent name = '{opponent_name}' (raw: {opponent_name_raw}, type: {type(opponent_name_raw)})")
            
            if not opponent_name or opponent_name == '' or opponent_name.lower() == 'nan':
                print(f"get_game_team_details_data: No opponent name found")
                return TableData(
                    columns=[],
                    data=[],
                    title=f"{i18n_service.get_text('no_data_available')} - {team}, {i18n_service.get_text('game')} {round_number} (no opponent found)"
                )
            
            # Get opponent player data
            opponent_filters = {
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.week: {'value': week, 'operator': 'eq'},
                Columns.team_name: {'value': opponent_name, 'operator': 'eq'},
                Columns.round_number: {'value': round_number, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}
            }
            
            print(f"get_game_team_details_data: Fetching opponent data for '{opponent_name}'")
            opponent_data = self.adapter.get_filtered_data(filters=opponent_filters)
            print(f"get_game_team_details_data: Found {len(opponent_data)} opponent rows")
            
            # Get team match points (Team Total row)
            team_total_filters = {
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.week: {'value': week, 'operator': 'eq'},
                Columns.team_name: {'value': team, 'operator': 'eq'},
                Columns.round_number: {'value': round_number, 'operator': 'eq'},
                Columns.computed_data: {'value': True, 'operator': 'eq'}  # Team totals
            }
            team_total_data = self.adapter.get_filtered_data(filters=team_total_filters)
            team_match_points = 0.0
            if not team_total_data.empty and Columns.points in team_total_data.columns:
                team_match_points = float(team_total_data[Columns.points].iloc[0]) if pd.notna(team_total_data[Columns.points].iloc[0]) else 0.0
            
            # Get opponent team match points
            opponent_total_filters = {
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.week: {'value': week, 'operator': 'eq'},
                Columns.team_name: {'value': opponent_name, 'operator': 'eq'},
                Columns.round_number: {'value': round_number, 'operator': 'eq'},
                Columns.computed_data: {'value': True, 'operator': 'eq'}  # Team totals
            }
            opponent_total_data = self.adapter.get_filtered_data(filters=opponent_total_filters)
            opponent_match_points = 0.0
            if not opponent_total_data.empty and Columns.points in opponent_total_data.columns:
                opponent_match_points = float(opponent_total_data[Columns.points].iloc[0]) if pd.notna(opponent_total_data[Columns.points].iloc[0]) else 0.0
            
            # Create columns - two column groups: selected team and opposing team
            # Order: Player name, Pins, Points | Points, Pins, Player name
            columns = [
                ColumnGroup(
                    title=team,  # Selected team name
                    frozen="left",
                    style={"backgroundColor": get_theme_color("background")},
                    columns=[
                        Column(title=i18n_service.get_text("player"), field="player_name", width="200px", align="left"),
                        Column(title=i18n_service.get_text("pins"), field="player_pins", width="80px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("points"), field="points", width="80px", align="center", decimal_places=0)
                    ]
                ),
                ColumnGroup(
                    title=opponent_name,  # Opposing team name
                    style={"backgroundColor": get_theme_color("surface_light")},
                    columns=[
                        Column(title=i18n_service.get_text("points"), field="opponent_points", width="80px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("pins"), field="opponent_pins", width="80px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("player"), field="opponent_player_name", width="200px", align="left")
                    ]
                )
            ]
            
            # Build data rows - sort by position
            data = []
            if Columns.position not in player_data.columns:
                print(f"get_game_team_details_data: Column {Columns.position} not found in player_data")
                return TableData(
                    columns=[],
                    data=[],
                    title=f"{i18n_service.get_text('no_data_available')} - {team}, {i18n_service.get_text('game')} {round_number} (missing position column)"
                )
            
            player_data_sorted = player_data.sort_values(by=Columns.position)
            
            total_points = 0.0
            total_player_pins = 0
            total_opponent_pins = 0
            
            total_opponent_points = 0.0
            
            for _, row in player_data_sorted.iterrows():
                try:
                    player_name = str(row[Columns.player_name]) if pd.notna(row[Columns.player_name]) else ""
                    player_pins = int(row[Columns.score]) if pd.notna(row[Columns.score]) else 0
                    points = float(row[Columns.points]) if pd.notna(row[Columns.points]) else 0.0
                    position = int(row[Columns.position]) if pd.notna(row[Columns.position]) else 0
                    
                    # Find opponent player at same position
                    opponent_pins = 0
                    opponent_player_name = ""
                    opponent_points = 0.0
                    if not opponent_data.empty and Columns.position in opponent_data.columns:
                        opponent_player = opponent_data[opponent_data[Columns.position] == position]
                        if not opponent_player.empty:
                            try:
                                if Columns.score in opponent_player.columns:
                                    opponent_pins = int(opponent_player[Columns.score].iloc[0]) if pd.notna(opponent_player[Columns.score].iloc[0]) else 0
                                if Columns.player_name in opponent_player.columns:
                                    opponent_player_name = str(opponent_player[Columns.player_name].iloc[0]) if pd.notna(opponent_player[Columns.player_name].iloc[0]) else ""
                                if Columns.points in opponent_player.columns:
                                    opponent_points = float(opponent_player[Columns.points].iloc[0]) if pd.notna(opponent_player[Columns.points].iloc[0]) else 0.0
                            except (IndexError, KeyError, ValueError) as e:
                                print(f"get_game_team_details_data: Error getting opponent data for position {position}: {e}")
                    
                    data.append([
                        player_name,
                        player_pins,
                        points,
                        opponent_points,
                        opponent_pins,
                        opponent_player_name
                    ])
                    
                    total_points += points
                    total_player_pins += player_pins
                    total_opponent_pins += opponent_pins
                    total_opponent_points += opponent_points
                except Exception as e:
                    print(f"get_game_team_details_data: Error processing player row: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Add team totals row (shows team name and team match points)
            data.append([
                team,  # Team name instead of "Total"
                total_player_pins,
                team_match_points,  # Team match points (0/3)
                opponent_match_points,  # Opponent team match points
                total_opponent_pins,
                opponent_name  # Opponent team name
            ])
            
            # Add final row with sum of all points (individual + team) for both teams
            total_all_points_team = total_points + team_match_points
            total_all_points_opponent = total_opponent_points + opponent_match_points
            data.append([
                "",  # Empty (player name column)
                "",  # Empty (pins column)
                total_all_points_team,  # Sum of individual + team points for team
                total_all_points_opponent,  # Sum of individual + team points for opponent
                "",  # Empty (pins column)
                ""  # Empty (player name column)
            ])
            
            return TableData(
                columns=columns,
                data=data,
                title=f"{team} - {i18n_service.get_text('week')} {week}, {i18n_service.get_text('game')} {round_number}",
                description=f"{i18n_service.get_text('individual_scores')} vs {opponent_name}",
                config={
                    "stickyHeader": True,
                    "striped": True,
                    "hover": True,
                    "responsive": True,
                    "compact": False,
                    "highlightLastRow": True
                }
            )
            
        except Exception as e:
            print(f"Error in get_game_team_details_data: {e}")
            import traceback
            traceback.print_exc()
            return TableData(
                columns=[],
                data=[],
                title=f"Error loading game team details data"
            )

    def get_league_standings(self, season: str, league: str, week: Optional[int] = None) -> LeagueStandings:
        """
        Get league standings for a specific season, league, and week.
        
        Args:
            season: The season identifier
            league: The league name
            week: The week number (if None, gets the latest week)
            
        Returns:
            LeagueStandings object with team performances
        """
        # If week is not specified, get the latest week
        if week is None:
            week = self.get_latest_week(season, league)
        
        print("week: ", week)

        # Get league statistics
        stats = self.stats_service.get_league_statistics(league, season)
        if not stats:
            return LeagueStandings(
                season=season,
                league_name=league,
                week=week,
                teams=[],
                last_updated=datetime.datetime.now().isoformat()
            )
        
        # Convert statistics to team performances
        team_performances = []
        for team_name, team_stats in stats.team_stats.items():
            # Get the latest weekly performance
            latest_week = max(team_stats.weekly_performances.keys())
            week_perf = team_stats.weekly_performances[latest_week]
            
            # Create weekly performances list
            weekly_performances = []
            for week_num, perf in team_stats.weekly_performances.items():
                weekly_performances.append(
                    TeamWeeklyPerformance(
                        team_id=perf.team_id,
                        team_name=perf.team_name,
                        week=week_num,
                        score=perf.total_score,
                        number_of_games=perf.number_of_games,
                        points=perf.points
                    )
                )
            
            # Sort weekly performances by week
            weekly_performances.sort(key=lambda x: x.week)
            
            # Create team performance
            team_performances.append(
                TeamSeasonPerformance(
                    team_id=week_perf.team_id,
                    team_name=team_name,
                    total_score=team_stats.season_summary.total_score,
                    total_points=team_stats.season_summary.total_points,
                    average=team_stats.season_summary.average_score,
                    weekly_performances=weekly_performances
                )
            )
        
        # Sort by total points (descending) and assign positions
        team_performances.sort(key=lambda x: (x.total_points, x.total_score), reverse=True)
        for i, perf in enumerate(team_performances, 1):
            perf.position = i
        
        # Create and return the LeagueStandings
        return LeagueStandings(
            season=season,
            league_name=league,
            week=week,
            teams=team_performances,
            last_updated=datetime.datetime.now().isoformat()
        )

    def _get_league_level(self, league: str) -> int:
        """Get the level of a league (delegates to utility function)"""
        return get_league_level(league)

    def get_league_performance_chart(self, season: str, league: str, team_id: Optional[str] = None) -> PlotData:
        """
        Get a chart showing team performance over time.
        
        Args:
            season: The season identifier
            league: The league name
            team_id: Optional team ID to highlight (if None, shows all teams)
            
        Returns:
            PlotData object with team performance data
        """
        # Get league standings
        standings = self.get_league_standings(season, league)
        
        if not standings.teams:
            return PlotData(
                title=f"{i18n_service.get_text('no_data_available_for')} {league} - {season}",
                series=[]
            )
        
        # Get all weeks in the season
        weeks = sorted(set(
            perf.week for team in standings.teams 
            for perf in team.weekly_performances
        ))
        
        # Prepare series data for each team
        series = []
        for team in standings.teams:
            # Skip teams that aren't the highlighted team (if specified)
            if team_id and team.team_id != team_id:
                continue
                
            # Create a map of week to points for this team
            week_to_points = {p.week: p.points for p in team.weekly_performances}
            
            # Calculate cumulative points for each week
            cumulative_points = []
            total = 0
            for week in weeks:
                total += week_to_points.get(week, 0)
                cumulative_points.append(total)
            
            # Add this team's series
            series.append({
                "name": team.team_name,
                "data": cumulative_points
            })
        
        # Create and return the PlotData
        return PlotData(
            title=f"{league} {i18n_service.get_text('team_performance')} - {season}",
            series=series,
            x_axis=weeks,
            y_axis_label=i18n_service.get_text("cumulative_points"),
            x_axis_label=i18n_service.get_text("week"),
            plot_type="line"
        )
    
    def get_league_summary_tiles(self, season: str, league: str) -> List[TileData]:
        """
        Get summary tiles for a league dashboard.
        
        Args:
            season: The season identifier
            league: The league name
            
        Returns:
            List of TileData objects with league summary information
        """
        # Get league standings
        standings = self.get_league_standings(season, league)
        
        if not standings.teams:
            return [
                TileData(
                    title=i18n_service.get_text("no_data"),
                    value=i18n_service.get_text("no_league_data_available"),
                    type="info"
                )
            ]
        
        # Create tiles
        tiles = []
        
        # League leader tile
        if standings.teams:
            leader = standings.teams[0]  # First team (highest points)
            tiles.append(
                TileData(
                    title=i18n_service.get_text("league_leader"),
                    value=leader.team_name,
                    subtitle=f"{leader.total_points} {i18n_service.get_text('points')}",
                    type="stat",
                    color="#28a745"  # Green
                )
            )
        
        # Average score tile
        if standings.teams:
            all_averages = [team.average for team in standings.teams]
            league_avg = sum(all_averages) / len(all_averages) if all_averages else 0
            tiles.append(
                TileData(
                    title=i18n_service.get_text("league_average"),
                    value=f"{league_avg:.1f}",
                    subtitle=i18n_service.get_text("pins_per_game"),
                    type="stat"
                )
            )
        
        # Weeks completed tile
        if standings.teams and standings.teams[0].weekly_performances:
            completed_weeks = len(set(p.week for p in standings.teams[0].weekly_performances))
            tiles.append(
                TileData(
                    title=i18n_service.get_text("weeks_completed"),
                    value=str(completed_weeks),
                    subtitle=f"of {completed_weeks + 2}",  # Assuming 2 more weeks to go
                    type="progress",
                    chart_data=[completed_weeks, completed_weeks + 2]
                )
            )
        
        return tiles
    
    def get_latest_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the latest league events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        # Import Columns dataclass
        from data_access.schema import Columns
        
        # Get all events from the adapter
        events_df = self.adapter.get_filtered_data(
            filters={},
            columns=[Columns.season, Columns.league_name, Columns.week, Columns.date]
        )
        
        # If no events, return empty list
        if events_df.empty:
            return []
        
        # Group by league, season, and week to get unique events
        # Take the first occurrence of each group (which will have the date)
        unique_events_df = events_df.groupby([Columns.league_name, Columns.season, Columns.week]).first().reset_index()
        
        # Sort by date (descending) to get the latest events
        unique_events_df = unique_events_df.sort_values(by=Columns.date, ascending=False)
        
        # Limit the results
        if limit is not None and limit > 0:
            unique_events_df = unique_events_df.head(limit)
        
        # Convert to list of dictionaries
        events = []
        for _, row in unique_events_df.iterrows():
            event = {
                "Season": row[Columns.season],
                "League": row[Columns.league_name],
                "Week": row[Columns.week],
                "Date": row[Columns.date]
            }
            events.append(event)
        
        return events

    def get_weeks(self, league_name: str = None, season: str = None) -> List[int]:
        """Get available weeks for a league and season"""
        #if not league_name or not season:
            # Return empty list if parameters are missing
        #    return []
        return self.adapter.get_weeks(season, league_name)

    def get_teams_in_league_season(self, league: str, season: str) -> List[str]:
        """Get teams in a specific league and season"""
        # Create a query to get all teams in this league and season
        query = LeagueQuery(season=season, league=league)
        
        # Get the data
        league_data = self.adapter.get_filtered_data(query.to_filter_dict())
        
        if league_data.empty:
            return []
        
        # Extract unique team names
        if 'Team' in league_data.columns:
            teams = sorted(league_data['Team'].unique().tolist())
            return teams
        
        return []

    def get_team_week_details_table_data(self, league: str, season: str, team: str, week: int) -> TableData:
        """Get team week details as a TableData object for rendering"""
        try:
            # Get individual player results for the team
            player_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.team_name: {'value': team, 'operator': 'eq'},
                Columns.week: {'value': week, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}
            }
            
            player_data = self.adapter.get_filtered_data(filters=player_filters)
            
            if player_data.empty:
                return TableData(
                    columns=[],
                    data=[],
                    title=f"{i18n_service.get_text('no_data_available_for_team_week')} {team} - {i18n_service.get_text('week')} {week}"
                )
            
            # Get team totals (computed data)
            team_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.team_name: {'value': team, 'operator': 'eq'},
                Columns.week: {'value': week, 'operator': 'eq'},
                Columns.computed_data: {'value': True, 'operator': 'eq'}
            }
            
            team_data = self.adapter.get_filtered_data(filters=team_filters)
            
            # Get opponent team totals
            opponent_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.team_name_opponent: {'value': team, 'operator': 'eq'},
                Columns.week: {'value': week, 'operator': 'eq'},
                Columns.computed_data: {'value': True, 'operator': 'eq'}
            }
            
            opponent_data = self.adapter.get_filtered_data(filters=opponent_filters)
            
            # Get individual opponent data to calculate average based on individual results
            opponent_individual_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.team_name_opponent: {'value': team, 'operator': 'eq'},
                Columns.week: {'value': week, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}  # Individual data, not computed
            }
            
            opponent_individual_data = self.adapter.get_filtered_data(filters=opponent_individual_filters)
            
            # Get unique games (round_number) for this team and map to opponent names
            games = sorted(player_data[Columns.round_number].unique())
            
            # Create a mapping of round_number to opponent team name
            game_to_opponent = {}
            for game in games:
                game_data = player_data[player_data[Columns.round_number] == game]
                if not game_data.empty:
                    opponent_name = game_data[Columns.team_name_opponent].iloc[0]
                    game_to_opponent[game] = opponent_name
            
            # Create column groups
            columns = [
                ColumnGroup(
                    title=i18n_service.get_text("player"),
                    frozen="left",
                    style={"backgroundColor": get_theme_color("background")},
                    columns=[
                        Column(title=i18n_service.get_text("position"), field="position", width="50px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("name"), field="name", width="200px", align="left")
                    ]
                )
            ]
            
            # Add game column groups with opponent team names
            for game in games:
                opponent_name = game_to_opponent.get(game, f"{i18n_service.get_text('game')} {game}")
                columns.append(
                    ColumnGroup(
                        title=opponent_name,
                        columns=[
                            Column(title=i18n_service.get_text("pins"), field=f"game{game}_score", width="80px", align="center", decimal_places=0),
                            Column(title=i18n_service.get_text("points"), field=f"game{game}_points", width="60px", align="center", decimal_places=0)
                        ]
                    )
                )
            
            # Add totals column group
            columns.append(
                ColumnGroup(
                    title=i18n_service.get_text("total"),
                    style={"backgroundColor": get_theme_color("surface_alt")},
                    header_style={"fontWeight": "bold"},
                    columns=[
                        Column(title=i18n_service.get_text("points"), field="total_points", width="80px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("score"), field="total_score", width="80px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("avg"), field="average", width="80px", align="center", decimal_places=1)
                    ]
                )
            )
            
            # Prepare data rows with merged position cells
            data = []
            row_metadata = []
            
            # Get all unique players who played in this event (same logic as New view)
            player_identifiers = []
            for _, row in player_data.iterrows():
                player_id = row[Columns.player_id] if not pd.isnull(row[Columns.player_id]) else row[Columns.player_name]
                player_name = row[Columns.player_name]
                # Create a unique identifier combining ID and name
                identifier = f"{player_id}_{player_name}"
                if identifier not in [p['identifier'] for p in player_identifiers]:
                    player_identifiers.append({
                        'identifier': identifier,
                        'player_id': player_id,
                        'player_name': player_name
                    })
            
            # Create player-position combinations
            player_position_combinations = []
            for player_info in player_identifiers:
                # Find all rows for this player
                player_rows = player_data[
                    (player_data[Columns.player_id] == player_info['player_id']) | 
                    (player_data[Columns.player_name] == player_info['player_name'])
                ]
                
                # Get all positions this player played
                positions = sorted(player_rows[Columns.position].dropna().unique())
                
                for position in positions:
                    player_position_combinations.append({
                        'player_info': player_info,
                        'position': position,
                        'player_rows': player_rows[player_rows[Columns.position] == position]
                    })
            
            # Sort by position first, then by player name
            player_position_combinations.sort(key=lambda x: (x['position'], x['player_info']['player_name']))
            
            # Group by position for merging
            position_groups = {}
            for combo in player_position_combinations:
                position = combo['position']
                if position not in position_groups:
                    position_groups[position] = []
                position_groups[position].append(combo)
            
            # Create merged data structure
            for position in sorted(position_groups.keys()):
                position_combos = position_groups[position]
                
                # Add first row of this position group with position number
                first_combo = position_combos[0]
                player_info = first_combo['player_info']
                player_rows = first_combo['player_rows']
                
                # Start with position and name
                row = [int(position + 1), player_info['player_name']]
                
                # Add game data - only fill if player participated in this position
                for game in games:
                    game_data = player_rows[player_rows[Columns.round_number] == game]
                    
                    if not game_data.empty:
                        row.append(int(game_data[Columns.score].iloc[0]))
                        row.append(round(float(game_data[Columns.points].iloc[0]), 1))
                    else:
                        row.append("")
                        row.append("")
                
                # Calculate totals for this player-position combination
                total_points = int(player_rows[Columns.points].sum()) if not player_rows.empty else 0
                total_score = int(player_rows[Columns.score].sum()) if not player_rows.empty else 0
                average = round(float(player_rows[Columns.score].mean()), 1) if not player_rows.empty and len(player_rows) > 0 else 0
                
                row.extend([total_points, total_score, average])
                
                # Add metadata for styling
                row_metadata.append({
                    'rowType': 'player',
                    'styling': {},
                    'position': int(position),
                    'isFirstInPosition': True,
                    'positionRowspan': len(position_combos)
                })
                
                data.append(row)
                
                # Add remaining rows for this position (without position number)
                for combo in position_combos[1:]:
                    player_info = combo['player_info']
                    player_rows = combo['player_rows']
                    
                    # Start with empty position and name
                    row = ["", player_info['player_name']]
                    
                    # Add game data - only fill if player participated in this position
                    for game in games:
                        game_data = player_rows[player_rows[Columns.round_number] == game]
                        
                        if not game_data.empty:
                            row.append(int(game_data[Columns.score].iloc[0]))
                            row.append(round(float(game_data[Columns.points].iloc[0]), 1))
                        else:
                            row.append("")
                            row.append("")
                    
                    # Calculate totals for this player-position combination
                    total_points = int(player_rows[Columns.points].sum()) if not player_rows.empty else 0
                    total_score = int(player_rows[Columns.score].sum()) if not player_rows.empty else 0
                    average = round(float(player_rows[Columns.score].mean()), 1) if not player_rows.empty and len(player_rows) > 0 else 0
                    
                    row.extend([total_points, total_score, average])
                    
                    # Add metadata for styling
                    row_metadata.append({
                        'rowType': 'player',
                        'styling': {},
                        'position': int(position),
                        'isFirstInPosition': False
                    })
                    
                    data.append(row)
            
            # Add team total row
            if not team_data.empty:
                # Start with position and name
                team_row = ["Team", team]
                
                # Add game data for team
                for game in games:
                    game_data = team_data[team_data[Columns.round_number] == game]
                    if not game_data.empty:
                        team_row.append(int(game_data[Columns.score].iloc[0]))
                        team_row.append(round(float(game_data[Columns.points].iloc[0]), 1))
                    else:
                        team_row.append(0)
                        team_row.append(0)
                
                # Calculate team totals
                team_row.append(int(team_data[Columns.points].sum()))
                team_row.append(int(team_data[Columns.score].sum()))
                team_row.append(round(float(player_data[Columns.score].mean()), 1) if len(player_data) > 0 else 0)
                
                # Add metadata for styling
                row_metadata.append({
                    'rowType': 'team',
                    'styling': {
                        'fontWeight': 'bold',
                        'borderTop': '2px solid #000000'
                    }
                })
                
                data.append(team_row)
            
            # Add opponent total row right after team row
            if not opponent_data.empty:
                # Start with position and name
                opponent_row = ["Team", "Opponents"]
                
                # Add game data for opponents
                for game in games:
                    game_data = opponent_data[opponent_data[Columns.round_number] == game]
                    if not game_data.empty:
                        opponent_row.append(int(game_data[Columns.score].iloc[0]))
                        opponent_row.append("")  # Replace opponent points with empty string
                    else:
                        opponent_row.append(0)
                        opponent_row.append("")
                
                # Calculate opponent totals
                opponent_row.append("")  # Replace opponent total points with empty string
                opponent_row.append(int(opponent_data[Columns.score].sum()))
                
                # Calculate opponent average based on individual results
                if not opponent_individual_data.empty:
                    opponent_average = round(float(opponent_individual_data[Columns.score].mean()), 1)
                else:
                    opponent_average = 0
                
                opponent_row.append(opponent_average)
                
                # Add metadata for styling
                row_metadata.append({
                    'rowType': 'opponents',
                    'styling': {}
                })
                
                data.append(opponent_row)
            
            # Add Total row that sums all points (individual + team)
            total_row = ["Total", "Points"]
            
            # Calculate total points for each game (individual + team)
            for game in games:
                game_player_data = player_data[player_data[Columns.round_number] == game]
                game_team_data = team_data[team_data[Columns.round_number] == game] if not team_data.empty else None
                
                # Individual points for this game
                game_points_total = round(float(game_player_data[Columns.points].sum()), 1) if not game_player_data.empty else 0
                
                # Add team points for this game if available
                if game_team_data is not None and not game_team_data.empty:
                    game_points_total += round(float(game_team_data[Columns.points].iloc[0]), 1)
                
                # Add empty string for score and points for this game
                total_row.extend(["", game_points_total])
            
            # Calculate overall totals (individual + team)
            total_points = int(player_data[Columns.points].sum())
            if not team_data.empty:
                total_points += int(team_data[Columns.points].sum())
            
            total_row.extend([total_points, "", ""])  # Replace score and average with empty strings
            
            # Add metadata for styling
            row_metadata.append({
                'rowType': 'total',
                'styling': {
                    'fontWeight': 'bold',
                    'borderTop': '2px solid #000000',
                    'borderBottom': '2px solid #000000'
                }
            })
            
            data.append(total_row)
            
            return TableData(
                columns=columns,
                data=data,
                row_metadata=row_metadata,
            title=f"{team} - {i18n_service.get_text('match_day')} {week}",
            description=f"{i18n_service.get_text('score_sheet_for')} {team} in {league} - {season}",
                config={
                    "stickyHeader": True,
                    "striped": True,
                    "hover": True,
                    "responsive": True,
                    "compact": False
                }
            )
            
        except Exception as e:
            print(f"Error in get_team_week_details_table_data: {e}")
            return TableData(
                columns=[],
                data=[],
                title=f"{i18n_service.get_text('error_loading_data_for')} {team} - {i18n_service.get_text('week')} {week}"
            )

    def get_team_averages_during_season(self, league_name: str, season: str) -> Dict[str, Any]:
        """Get team averages throughout a season"""
        # Get all teams and their performances
        standings = self.get_league_standings(season, league_name)
        
        if not standings.teams:
            return SeriesData().to_dict()
        
        series_data = SeriesData(label_x_axis="Spieltag", label_y_axis="Durchschnitt", name="Durchschnitt im Saisonverlauf", 
                                 query_params={"season": season, "league": league_name})
        
        for team in standings.teams:
            # Calculate average for each week
            averages = []
            for perf in team.weekly_performances:
                if perf.score > 0 and perf.number_of_games > 0:
                    # Calculate team average: total pins divided by number of games
                    # perf.score is the total pins of all players on the team for this week
                    # perf.number_of_games is the number of games played by all players on the team for this week
                    avg = perf.score / perf.number_of_games
                    averages.append(round(avg, 2))
                else:
                    averages.append(0)
            
            series_data.add_data(team.team_name, averages)

        return series_data.to_dict()

    def get_team_positions_during_season(self, league_name: str, season: str) -> Dict[str, List[int]]:
        """Get team positions throughout a season"""
        # Get all teams and their performances
        standings = self.get_league_standings(season, league_name)
        
        if not standings.teams:
            return {}
        
        # Get all weeks in the season
        all_weeks = sorted(set(
            perf.week for team in standings.teams 
            for perf in team.weekly_performances
        ))

        series_data = SeriesData(label_x_axis="Spieltag", label_y_axis="Position", name="Position im Saisonverlauf", 
                                 query_params={"season": season, "league": league_name})
        points_per_team = {}
        points_per_team_accumulated = {}
        for team in standings.teams:
            points_per_team[team.team_name] = [p.points for p in team.weekly_performances]
            points_per_team_accumulated[team.team_name] = list(accumulate(points_per_team[team.team_name]))
        

        position_per_week = {team_name: [] for team_name in points_per_team.keys()}
        position_per_week_accumulated = {team_name: [] for team_name in points_per_team.keys()}
        # create a tuple of team name and points per week and sort it by points

        for week in all_weeks:
            week = week - 1

            # create a tuple of team name and points per week
            team_points_week = [(team_name, points_per_team[team_name][week]) for team_name in points_per_team.keys()]
            # sort it by points
            team_points_week.sort(key=lambda x: x[1], reverse=True)

            # create a tuple of team name and points accumulated per week
            team_points_week_accumulated = [(team_name, points_per_team_accumulated[team_name][week]) for team_name in points_per_team.keys()]
            # sort it by points
            team_points_week_accumulated.sort(key=lambda x: x[1], reverse=True)

            # position per week
            for idx, team_n_points in enumerate(team_points_week):
                # find position of team_name in points_per_team[team_name]

                position_per_week[team_n_points[0]].append(idx+1)

            for idx, team_n_points in enumerate(team_points_week_accumulated):
                # position per week accumulated
                # find position of team_name in points_per_team_accumulated[team_name]
                #position_accumulated = team_points_week_accumulated.index(team_name) + 1
                position_per_week_accumulated[team_n_points[0]].append(idx+1)

            # position per week accumulated

        # add the data to the series data
        for team in standings.teams:
            series_data.add_data(team.team_name, position_per_week[team.team_name])
            # replace auto generated accumulated data             
            series_data.data_accumulated[team.team_name] = position_per_week_accumulated[team.team_name]

        return series_data.to_dict()


    
        # Calculate positions for each week
        positions = {}
        
        for week in all_weeks:
            # Get performances for this week
            week_performances = []
            for team in standings.teams:
                perf = next((p for p in team.weekly_performances if p.week == week), None)
                if perf:
                    week_performances.append({
                        "team": team.team_name,
                        "points": perf.points,
                        "score": perf.score
                    })
            
            # Sort by points (and score as tiebreaker)
            week_performances.sort(key=lambda x: (x["points"], x["score"]), reverse=True)
            
            # Assign positions
            for i, perf in enumerate(week_performances, 1):
                team_name = perf["team"]
                if team_name not in positions:
                    positions[team_name] = [0] * len(all_weeks)
                
                # Find the index for this week
                week_index = all_weeks.index(week)
                positions[team_name][week_index] = i
        
        return positions

    def get_honor_scores(self, league: str, season: str, week: int, 
                        number_of_individual_scores: int = 3, number_of_team_scores: int = 3,
                        number_of_individual_averages: int = 3, number_of_team_averages: int = 3) -> Dict[str, Any]:
        """Get honor scores for a specific week"""
        # Create a query for this league, season, and week
        query_individual = LeagueQuery(season=season, league=league, week=week, computed_data=False)
        query_team = LeagueQuery(season=season, league=league, week=week, computed_data=True)
        

        # Get the data
        league_data_individual = self.adapter.get_filtered_data(query_individual.to_filter_dict())
        league_data_team = self.adapter.get_filtered_data(query_team.to_filter_dict())
        
        if league_data_individual.empty:
            return {
                "individual_scores": [],
                "team_scores": [],
                "individual_averages": [],
                "team_averages": []
            }
        
        # Process individual scores
        individual_scores_list = []
        if Columns.player_name in league_data_individual.columns and Columns.score in league_data_individual.columns:
            player_scores = league_data_individual.sort_values(Columns.score, ascending=False).head(number_of_individual_scores)

            for _, row in player_scores.iterrows():
                individual_scores_list.append({
                    "player": row[Columns.player_name] + " (" + row[Columns.team_name] + ")",
                    "score": row[Columns.score]
                })

        # Process team scores
        team_scores_list = []
        if Columns.team_name in league_data_team.columns and Columns.score in league_data_team.columns:
            team_scores = league_data_team.sort_values(Columns.score, ascending=False).head(number_of_team_scores)
            
            for _, row in team_scores.iterrows():
                team_scores_list.append({
                    "team": row[Columns.team_name],
                    "score": row[Columns.score]
                })
        
        # Process individual averages
        individual_averages_list = []
        if Columns.player_name in league_data_individual.columns and Columns.score in league_data_individual.columns:
            player_averages = league_data_individual.groupby([Columns.player_name, Columns.team_name])[Columns.score].mean().reset_index()
            player_averages = player_averages.sort_values(Columns.score, ascending=False).head(number_of_individual_averages)
            
            for _, row in player_averages.iterrows():
                individual_averages_list.append({
                    "player": row[Columns.player_name] + " (" + row[Columns.team_name] + ")",
                    "average": round(row[Columns.score], 2)
                })

        # Process team averages
        team_averages_list = []
        if Columns.team_name in league_data_team.columns and Columns.score in league_data_team.columns:
            team_averages = league_data_team.groupby([Columns.team_name, Columns.players_per_team])[Columns.score].mean().reset_index()
            team_averages = team_averages.sort_values(Columns.score, ascending=False).head(number_of_team_averages)
            
            for _, row in team_averages.iterrows():
                team_averages_list.append({
                    "team": row[Columns.team_name],
                    "average": round(row[Columns.score]/row[Columns.players_per_team], 2)
                })

        return {
            "individual_scores": individual_scores_list,
            "team_scores": team_scores_list,
            "individual_averages": individual_averages_list,
            "team_averages": team_averages_list
        }

    def get_league_history_table_data(self, league_name: str, season: str, week: Optional[int] = None) -> TableData:
        """
        Get league history as a TableData object for rendering.
        
        Args:
            league_name: The league name
            season: The season identifier
            week: The week number (if None, gets the latest)
            
        Returns:
            TableData object with the league history
        """
        return self.get_league_table_simple(season=season, league=league_name, week=week, include_history=True)

    def get_team_averages_simple(self, league_name: str, season: str) -> Dict[str, Any]:
        """Get team averages throughout a season - simple direct query approach"""
        try:
            # Direct query to get team data for the league and season
            filters = {
                Columns.league_name: {'value': league_name, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'},

            }
            
            # Get all team data for this league and season
            team_data = self.adapter.get_filtered_data(filters=filters)
            
            if team_data.empty:
                return SeriesData(
                    label_x_axis="Spieltag", 
                    label_y_axis="Durchschnitt", 
                    name="Durchschnitt im Saisonverlauf", 
                    query_params={"season": season, "league": league_name, "computed_data": False}
                ).to_dict()
            
            # Group by team and week to calculate averages
            series_data = SeriesData(
                label_x_axis="Spieltag", 
                label_y_axis="Durchschnitt", 
                name="Durchschnitt im Saisonverlauf", 
                query_params={"season": season, "league": league_name}
            )
            
            # Get all teams and weeks
            teams = team_data[Columns.team_name].unique()
            weeks = sorted(team_data[Columns.week].unique())
            
            for team in teams:
                team_week_data = team_data[team_data[Columns.team_name] == team]
                averages = []
                
                for week in weeks:
                    week_data = team_week_data[team_week_data[Columns.week] == week]
                    
                    if not week_data.empty:
                        averages.append(round(float(week_data[Columns.score].mean()), 2))
                    else:
                        averages.append(0)
                
                series_data.add_data(team, averages)
            
            return series_data.to_dict()
            
        except Exception as e:
            print(f"Error in get_team_averages_simple: {e}")
            return SeriesData(
                label_x_axis="Spieltag", 
                label_y_axis="Durchschnitt", 
                name="Durchschnitt im Saisonverlauf", 
                query_params={"season": season, "league": league_name}
            ).to_dict()

    def get_league_week_table_simple(self, season: str, league: str, week: Optional[int] = None) -> TableData:
        """
        Get a simplified league week table with direct data query.
        
        Args:
            season: The season identifier
            league: The league name
            week: The current week (if None, gets the latest)
            
        Returns:
            TableData object with the league standings
        """
        return self.get_league_table_simple(season=season, league=league, week=week, include_history=False)

    def get_league_table_simple(self, season: str, league: str, week: Optional[int] = None, include_history: bool = False) -> TableData:
        """
        Get a simplified league table with direct data query.
        Can handle both single week and multiple weeks (history).
        
        Args:
            season: The season identifier
            league: The league name
            week: The current week (if None, gets the latest)
            include_history: If True, shows all weeks up to the selected week
            
        Returns:
            TableData object with the league standings
        """
        try:
            # If week is not specified, get the latest week
            if week is None:
                week = self.get_latest_week(season, league)
            
            # Direct query to get all data for this league and season (both individual and team points)
            # Get individual player data (for scores and averages)
            individual_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}
            }
            
            individual_data = self.adapter.get_filtered_data(filters=individual_filters)
            
            # Get team bonus data (for team points)
            team_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.computed_data: {'value': True, 'operator': 'eq'}
            }
            
            team_bonus_data = self.adapter.get_filtered_data(filters=team_filters)
            
            # Ensure team_bonus_data is a DataFrame
            if team_bonus_data is None:
                team_bonus_data = pd.DataFrame()
            
            # Use individual data for the main league data (scores and averages)
            league_data = individual_data
            
            if league_data.empty:
                return TableData(
                    columns=[],
                    data=[],
                    title=f"{i18n_service.get_text('no_data_available_for')} {league} - {season}"
                )
            
            # Get als and weeks
            teams = league_data[Columns.team_name].unique()
            all_weeks = sorted(league_data[Columns.week].unique())
            
            # Determine which weeks to show
            if include_history:
                weeks_to_show = [w for w in all_weeks if w <= week]
            else:
                weeks_to_show = [week]
            
            # Calculate data for each team
            team_data = {}
            
            for team in teams:
                team_data[team] = {
                    'weekly_data': {},
                    'season_score': 0,
                    'season_points': 0,
                    'season_avg': 0
                }
                
                # Initialize variables to avoid "referenced before assignment" errors
                team_bonus_team_data = pd.DataFrame()
                
                # Get individual player data for this team (for scores and averages)
                team_individual_data = individual_data[individual_data[Columns.team_name] == team]
                
                # Get team bonus data for this team (for team points only)
                if Columns.team_name in team_bonus_data.columns:
                    team_bonus_team_data = team_bonus_data[team_bonus_data[Columns.team_name] == team]
                else:
                    team_bonus_team_data = pd.DataFrame()
                
                # Calculate season totals (accumulated up to selected week)
                if not team_individual_data.empty:
                    # Filter individual data up to selected week
                    team_individual_until_week = team_individual_data[team_individual_data[Columns.week] <= week]
                    team_data[team]['season_score'] = int(team_individual_until_week[Columns.score].sum())
                    team_data[team]['season_points'] = float(team_individual_until_week[Columns.points].sum())
                    
                    # Calculate season average based on individual scores
                    if len(team_individual_until_week) > 0:
                        team_data[team]['season_avg'] = round(float(team_individual_until_week[Columns.score].mean()), 1)
                
                # Add team bonus points to season total (up to selected week)
                if not team_bonus_team_data.empty:
                    team_bonus_until_week = team_bonus_team_data[team_bonus_team_data[Columns.week] <= week]
                    team_data[team]['season_points'] += float(team_bonus_until_week[Columns.points].sum())
                
                # Calculate weekly data
                for w in weeks_to_show:
                    team_week_individual = team_individual_data[team_individual_data[Columns.week] == w]
                    team_week_bonus = team_bonus_team_data[team_bonus_team_data[Columns.week] == w]
                    
                    if not team_week_individual.empty:
                        week_score = int(team_week_individual[Columns.score].sum())
                        week_points = float(team_week_individual[Columns.points].sum())
                        week_avg = week_score / len(team_week_individual) if len(team_week_individual) > 0 else 0
                        
                        # Add team bonus points for this week
                        if not team_week_bonus.empty:
                            week_points += float(team_week_bonus[Columns.points].sum())
                        
                        team_data[team]['weekly_data'][w] = {
                            'points': format_float_one_decimal(week_points),
                            'score': week_score,
                            'avg': round(week_avg, 1)
                        }
                    else:
                        team_data[team]['weekly_data'][w] = {
                            'points': 0,
                            'score': 0,
                            'avg': 0
                        }
            
            # Sort teams based on context
            if include_history:
                # For history mode: sort by total accumulated points (descending), then by total accumulated score (descending)
                sorted_teams = sorted(
                    teams,
                    key=lambda t: (
                        team_data[t]['season_points'],
                        team_data[t]['season_score']
                    ),
                    reverse=True
                )
            else:
                # For single week: sort by points earned in the selected week (descending), then by score in the selected week (descending)
                sorted_teams = sorted(
                    teams,
                    key=lambda t: (
                        team_data[t]['weekly_data'].get(week, {}).get('points', 0),
                        team_data[t]['weekly_data'].get(week, {}).get('score', 0)
                    ),
                    reverse=True
                )
            
            # Create column groups
            columns = [
                ColumnGroup(
                    title=i18n_service.get_text("ranking"),
                    frozen="left",
                    style={"backgroundColor": get_theme_color("background")},
                    columns=[
                        Column(title="#", field="pos", width="50px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("team"), field="team", width="200px", align="left")
                    ]
                )
            ]
            
            # Add totals column group first (after ranking) - matches data order
            columns.append(
                ColumnGroup(
                    title="Total",
                    style={"backgroundColor": get_theme_color("surface_alt")},
                    header_style={"fontWeight": "bold"},
                    highlighted=True,  # Highlight the Total group
                    columns=[
                        Column(title=i18n_service.get_text("points"), field="season_points", format="{:,}", width="75px", decimal_places=0),
                        Column(title=i18n_service.get_text("pins"), field="season_score", format="{:,}", width="75px", decimal_places=0),
                        Column(title=i18n_service.get_text("average"), field="season_avg", format="{:.1f}", width="75px", decimal_places=1)
                    ]
                )
            )

            # Add weekly column groups after totals
            for w in weeks_to_show:
                columns.append(
                    ColumnGroup(
                        title=f"{i18n_service.get_text('week')} {w}",
                        columns=[
                            Column(title=i18n_service.get_text("points"), field=f"week{w}_points", format="{:.1f}", width="75px", decimal_places=1),
                            Column(title=i18n_service.get_text("score"), field=f"week{w}_score", format="{:,}", width="75px", decimal_places=0),
                            Column(title=i18n_service.get_text("average"), field=f"week{w}_avg", format="{:.1f}", width="75px", decimal_places=1)
                        ]
                    )
                )

            
            # Prepare the data rows
            data = []
            for i, team in enumerate(sorted_teams, 1):
                team_info = team_data[team]
                
                # Start with position and team name
                row = [i, team]
                
                # Add season totals first (matches column order: Ranking -> Totals -> Weeks)
                row.extend([
                    format_float_one_decimal(team_info['season_points']),
                    team_info['season_score'],
                    format_float_one_decimal(team_info['season_avg'])
                ])
                
                # Add weekly data after totals
                for w in weeks_to_show:
                    week_info = team_info['weekly_data'][w]
                    row.extend([
                        format_float_one_decimal(week_info['points']),
                        week_info['score'],
                        format_float_one_decimal(week_info['avg'])
                    ])
                
                data.append(row)
            
            # Create and return the TableData
            if include_history:
                title = f"{league} {i18n_service.get_text('league_history')} - {season}"
                description = f"{i18n_service.get_text('through_week')} {week}"
            else:
                title = f"{league} {i18n_service.get_text('league_standings')} - {season}"
                description = f"{i18n_service.get_text('week_results')}"
            
            return TableData(
                columns=columns,
                data=data,
                title=title,
                description=description,
                config={
                    "stickyHeader": True,
                    "striped": True,
                    "hover": True,
                    "responsive": True,
                    "compact": True,
                    "stripedColGroups": True
                }
            )
            
        except Exception as e:
            print(f"Error in get_league_table_simple: {e}")
            return TableData(
                columns=[],
                data=[],
                title=f"Error loading data for {league} - {season}"
            )

    def get_team_positions_simple(self, league_name: str, season: str) -> Dict[str, Any]:
        """Get team positions throughout a season using direct data adapter queries"""
        # Get weekly points from get_team_points_simple
        points_data = self.get_team_points_simple(league_name, season)
        
        if not points_data or 'data' not in points_data:
            return SeriesData(
                label_x_axis="Spieltag", 
                label_y_axis="Position", 
                name="Position im Saisonverlauf", 
                query_params={"season": season, "league": league_name}
            ).to_dict()
        
        # Extract weekly points from the SeriesData
        weekly_points = points_data.get('data', {})
        all_teams = list(weekly_points.keys())
        all_weeks = list(range(1, len(next(iter(weekly_points.values()), [])) + 1)) if weekly_points else []
        
        if not all_teams:
            return SeriesData(
                label_x_axis="Spieltag", 
                label_y_axis="Position", 
                name="Position im Saisonverlauf", 
                query_params={"season": season, "league": league_name}
            ).to_dict()
        
        # Create SeriesData for positions
        series_data = SeriesData(
            label_x_axis="Spieltag", 
            label_y_axis="Position", 
            name="Position im Saisonverlauf", 
            query_params={"season": season, "league": league_name}
        )
        
        # Calculate positions for each week
        positions_per_team = {team: [] for team in all_teams}
        
        for week_idx, week in enumerate(all_weeks):
            # Get accumulated points up to this week for each team
            accumulated_points = {}
            for team in all_teams:
                accumulated_points[team] = sum(weekly_points[team][:week_idx + 1])
            
            # Sort teams by accumulated points (descending) for this week
            sorted_teams = sorted(accumulated_points.items(), key=lambda x: x[1], reverse=True)
            
            # Create a mapping of team to position for this week
            week_positions = {}
            for pos, (team, _) in enumerate(sorted_teams, 1):
                week_positions[team] = pos
            
            # Add the position for this week to each team's list
            for team in all_teams:
                positions_per_team[team].append(week_positions[team])
        
        # Add data for each team using the proper add_data method
        for team in all_teams:
            series_data.add_data(team, positions_per_team[team])
        
        return series_data.to_dict()

    def get_team_points_simple(self, league_name: str, season: str) -> Dict[str, Any]:
        """Get team points throughout a season using direct data adapter queries"""
        # Get individual player data
        individual_filters = {
            Columns.league_name: {'value': league_name, 'operator': 'eq'},
            Columns.season: {'value': season, 'operator': 'eq'},
            Columns.computed_data: {'value': False, 'operator': 'eq'}
        }
        individual_data = self.adapter.get_filtered_data(filters=individual_filters)
        
        # Get team bonus data
        team_filters = {
            Columns.league_name: {'value': league_name, 'operator': 'eq'},
            Columns.season: {'value': season, 'operator': 'eq'},
            Columns.computed_data: {'value': True, 'operator': 'eq'}
        }
        team_data = self.adapter.get_filtered_data(filters=team_filters)
        
        if individual_data.empty and team_data.empty:
            return SeriesData(
                label_x_axis="Spieltag", 
                label_y_axis="Punkte", 
                name="Punkte im Saisonverlauf", 
                query_params={"season": season, "league": league_name}
            ).to_dict()
        
        # Get all weeks and teams (from individual data for weeks, from both for teams)
        all_weeks = sorted(individual_data[Columns.week].unique()) if not individual_data.empty else []
        all_teams_individual = set(individual_data[Columns.team_name].unique()) if not individual_data.empty else set()
        all_teams_team = set(team_data[Columns.team_name].unique()) if not team_data.empty else set()
        all_teams = sorted(all_teams_individual | all_teams_team)
        
        # Calculate weekly points for each team (individual + team points)
        weekly_points = {}
        for team in all_teams:
            weekly_points[team] = []
            for week in all_weeks:
                # Get individual player points for this team and week
                individual_week_data = individual_data[(individual_data[Columns.team_name] == team) & (individual_data[Columns.week] == week)]
                individual_points = individual_week_data[Columns.points].sum() if not individual_week_data.empty else 0
                
                # Get team bonus points for this team and week
                team_week_data = team_data[(team_data[Columns.team_name] == team) & (team_data[Columns.week] == week)]
                team_points = team_week_data[Columns.points].sum() if not team_week_data.empty else 0
                
                # Total points = individual + team bonus
                total_week_points = individual_points + team_points
                weekly_points[team].append(total_week_points)
        
        # Create SeriesData
        series_data = SeriesData(
            label_x_axis="Spieltag", 
            label_y_axis="Punkte", 
            name="Punkte im Saisonverlauf", 
            query_params={"season": season, "league": league_name}
        )
        
        # Add data for each team
        for team in all_teams:
            series_data.add_data(team, weekly_points[team])
        
        return series_data.to_dict()

    def get_team_week_head_to_head_table_data(self, league: str, season: str, team: str, week: int, view_mode: str = 'own_team') -> TableData:
        """
        Get head-to-head comparison table data for a team vs their opponents in a specific week.
        view_mode: 'own_team' (default), 'opponents', 'full'
        """
        try:
            # Get all matches for the team in this week
            team_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.team_name: {'value': team, 'operator': 'eq'},
                Columns.week: {'value': week, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}
            }
            team_data = self.adapter.get_filtered_data(filters=team_filters)
            if team_data.empty:
                return TableData(
                    columns=[],
                    data=[],
                    title=f"{i18n_service.get_text('no_data_available_for_team_week')} {team} - {i18n_service.get_text('week')} {week}"
                )
            
            # Get all matches for the opponent teams in this week
            opponent_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.team_name_opponent: {'value': team, 'operator': 'eq'},
                Columns.week: {'value': week, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}
            }
            opponent_data = self.adapter.get_filtered_data(filters=opponent_filters)
            
            # Get unique round numbers (matches)
            all_rounds = sorted(set(team_data[Columns.round_number].unique()) | set(opponent_data[Columns.round_number].unique()))

            # --- Determine which players to show ---
            show_own = view_mode in ('own_team', 'full')
            show_opp = view_mode in ('opponents', 'full')

            # Get unique players for each side
            own_players = team_data[Columns.player_name].unique() if show_own else []
            opp_players = opponent_data[Columns.player_name].unique() if show_opp else []

            # Build player participation map: {player: {round: row(s)}}
            def build_participation_map(df):
                part_map = {}
                for player in df[Columns.player_name].unique():
                    player_rows = df[df[Columns.player_name] == player]
                    part_map[player] = {}
                    for rnd in player_rows[Columns.round_number].unique():
                        part_map[player][rnd] = player_rows[player_rows[Columns.round_number] == rnd].iloc[0]
                return part_map
            own_part_map = build_participation_map(team_data) if show_own else {}
            opp_part_map = build_participation_map(opponent_data) if show_opp else {}

            # --- Build columns ---
            columns = [
                ColumnGroup(
                    title=i18n_service.get_text("match_info"),
                    style={"backgroundColor": get_theme_color("background")},
                    columns=[
                        Column(title=i18n_service.get_text("round"), field="round_number", width="60px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("opponent"), field="opponent_name", width="120px", align="left"),
                    ]
                )
            ]

            # Helper to build player col group
            def player_col_group(player, prefix):
                return ColumnGroup(
                    title=player,
                        columns=[
                        Column(title=i18n_service.get_text("position"), field=f"{prefix}{player}_pos", width="50px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("score"), field=f"{prefix}{player}_score", width="80px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("points"), field=f"{prefix}{player}_points", width="60px", align="center", decimal_places=0),
                    ]
                )

            # Add own team player columns
            for player in own_players:
                columns.append(player_col_group(player, "own_"))
            # Add opponent player columns
            for player in opp_players:
                columns.append(player_col_group(player, "opp_"))

            # Add team column group
            columns.append(
                ColumnGroup(
                    title=i18n_service.get_text("team"),
                    style={"backgroundColor": get_theme_color("surface_alt")},
                    header_style={"fontWeight": "bold"},
                    columns=[
                        Column(title=i18n_service.get_text("score"), field="team_score", width="80px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("points"), field="team_points", width="80px", align="center", decimal_places=0)
                    ]
                )
            )
            
            # --- Build data rows ---
            if view_mode == 'own_team':
                # Build main data rows (one per round)
                data = []
                for rnd in all_rounds:
                    # Get opponent team name for this round (from own or opponent data)
                    if rnd in team_data[Columns.round_number].values:
                        opponent_team = team_data[team_data[Columns.round_number] == rnd][Columns.team_name_opponent].iloc[0]
                    elif rnd in opponent_data[Columns.round_number].values:
                        opponent_team = opponent_data[opponent_data[Columns.round_number] == rnd][Columns.team_name].iloc[0]
                    else:
                        opponent_team = ""
                    row = [int(rnd), opponent_team]
                    # For each player, always output pos, score, points (blank if not played)
                    for player in own_players:
                        if rnd in own_part_map[player]:
                            row_data = own_part_map[player][rnd]
                            row.append(int(row_data[Columns.position] + 1) if not pd.isnull(row_data[Columns.position]) else "")
                            row.append(int(row_data[Columns.score]) if not pd.isnull(row_data[Columns.score]) else "")
                            row.append(float(row_data[Columns.points]) if not pd.isnull(row_data[Columns.points]) else "")
                        else:
                            row.extend(["", "", ""])
                    # Team totals for this round (if available)
                    team_totals = team_data[(team_data[Columns.round_number] == rnd) & (team_data[Columns.computed_data] == True)]
                    if not team_totals.empty:
                        row.append(int(team_totals[Columns.score].iloc[0]))
                        row.append(int(team_totals[Columns.points].iloc[0]))
                    else:
                        row.extend(["", ""])
                    data.append(row)
                # Add team totals row at the end
                team_total_row = ["Team", ""]
                for player in own_players:
                    # Sum score and points for this player across all rounds
                    player_rows = [own_part_map[player][rnd] for rnd in own_part_map[player] if not pd.isnull(own_part_map[player][rnd][Columns.score])]
                    if player_rows:
                        total_score = sum(int(row[Columns.score]) for row in player_rows if not pd.isnull(row[Columns.score]))
                        total_points = sum(float(row[Columns.points]) for row in player_rows if not pd.isnull(row[Columns.points]))
                        team_total_row.extend(["", total_score, total_points])
                    else:
                        team_total_row.extend(["", "", ""])
                # Team total score/points for all rounds
                team_score_total = team_data[team_data[Columns.computed_data] == True][Columns.score].sum() if not team_data.empty else ""
                team_points_total = team_data[team_data[Columns.computed_data] == True][Columns.points].sum() if not team_data.empty else ""
                team_total_row.append(int(team_score_total) if team_score_total != "" else "")
                team_total_row.append(int(team_points_total) if team_points_total != "" else "")
                data.append(team_total_row)
                # Debug print for non-serializable values
                for i, row in enumerate(data):
                    for j, cell in enumerate(row):
                        if hasattr(cell, 'dtype') or type(cell).__module__ == 'numpy':
                            print(f"Non-serializable value at row {i}, col {j}: {cell} ({type(cell)})")
                return TableData(
                    columns=columns,
                    data=data,
                    title=f"{team} - Head-to-Head (Week {week}) [own_team]",
                    description=f"Head-to-Head table for {team} in {league} - {season} (view: own_team)",
                    config={
                        "stickyHeader": True,
                        "striped": True,
                        "hover": True,
                        "responsive": True,
                        "compact": False
                    }
                )
            else: # view_mode in ('opponents', 'full')
                # --- Own team row ---
                if show_own:
                    row = [int(rnd), opponent_team]
                    # Own players
                    for player in own_players:
                        if rnd in own_part_map[player]:
                            row_data = own_part_map[player][rnd]
                            row.append(int(row_data[Columns.position] + 1) if not pd.isnull(row_data[Columns.position]) else "")
                            row.append(int(row_data[Columns.score]) if not pd.isnull(row_data[Columns.score]) else "")
                            row.append(float(row_data[Columns.points]) if not pd.isnull(row_data[Columns.points]) else "")
                        else:
                            row.extend(["", "", ""])
                    # Opponent players (blank)
                    for player in opp_players:
                        row.extend(["", "", ""])
                    # Team totals (if available)
                    team_totals = team_data[(team_data[Columns.round_number] == rnd) & (team_data[Columns.computed_data] == True)]
                    if not team_totals.empty:
                        row.append(int(team_totals[Columns.score].iloc[0]))
                        row.append(int(team_totals[Columns.points].iloc[0]))
                    else:
                        row.extend(["", ""])
                    data.append(row)

                # --- Opponent team row (only in 'full' or 'opponents' mode) ---
                if show_opp:
                    row = [int(rnd), team]  # Opponent's view: their opponent is 'team'
                    # Own players (blank)
                    for player in own_players:
                        row.extend(["", "", ""])
                    # Opponent players
                    for player in opp_players:
                        if rnd in opp_part_map[player]:
                            row_data = opp_part_map[player][rnd]
                            row.append(int(row_data[Columns.position] + 1) if not pd.isnull(row_data[Columns.position]) else "")
                            row.append(int(row_data[Columns.score]) if not pd.isnull(row_data[Columns.score]) else "")
                            row.append(float(row_data[Columns.points]) if not pd.isnull(row_data[Columns.points]) else "")
                        else:
                            row.extend(["", "", ""])
                    # Team totals (if available)
                    opp_totals = opponent_data[(opponent_data[Columns.round_number] == rnd) & (opponent_data[Columns.computed_data] == True)]
                    if not opp_totals.empty:
                        row.append(int(opp_totals[Columns.score].iloc[0]))
                        row.append(int(opp_totals[Columns.points].iloc[0]))
                    else:
                        row.extend(["", ""])
                    data.append(row)

                for i, row in enumerate(data):
                    for j, cell in enumerate(row):
                        if hasattr(cell, 'dtype') or type(cell).__module__ == 'numpy':
                            print(f"Non-serializable value at row {i}, col {j}: {cell} ({type(cell)})")

                return TableData(
                    columns=columns,
                    data=data,
                    title=f"{team} - Head-to-Head (Week {week}) [{view_mode}]",
                    description=f"Head-to-Head table for {team} in {league} - {season} (view: {view_mode})",
                    config={
                        "stickyHeader": True,
                        "striped": True,
                        "hover": True,
                        "responsive": True,
                        "compact": False
                    }
                )
        except Exception as e:
            print(f"Error in get_team_week_head_to_head_table_data: {e}")
            return TableData(
                columns=[],
                data=[],
                title=f"{i18n_service.get_text('error_loading_data_for')} {team} - {i18n_service.get_text('week')} {week}"
            )

    def get_team_individual_scores_table(self, league: str, season: str, team: str, week: int) -> TableData:
        """
        Returns a table with all individual scores of each player of the selected team at the given event (league, season, week).
        - Col group 'Opponents': Name (opponent name)
        - Col group with team name: Score, Points, Total Points (sum of all individual points + team points for the match)
        - One col group per player who played: Pos, Score, Points
        - Each row is a match (round) for the team in that week
        - Summary row at the end: sum of all individual scores and points per player, sum of team totals
        - hbar above the final row, final row bold
        """
        import pandas as pd
        from app.models.table_data import TableData, ColumnGroup, Column
        from data_access.schema import Columns

        # Get all individual player results for the team in this event
        player_filters = {
            Columns.league_name: {'value': league, 'operator': 'eq'},
            Columns.season: {'value': season, 'operator': 'eq'},
            Columns.team_name: {'value': team, 'operator': 'eq'},
            Columns.week: {'value': week, 'operator': 'eq'},
            Columns.computed_data: {'value': False, 'operator': 'eq'}
        }
        player_data = self.adapter.get_filtered_data(filters=player_filters)
        if player_data.empty:
            return TableData(columns=[], data=[], title=f"No data available for {team} - Week {week}")

        # Get team totals (computed data)
        team_filters = {
            Columns.league_name: {'value': league, 'operator': 'eq'},
            Columns.season: {'value': season, 'operator': 'eq'},
            Columns.team_name: {'value': team, 'operator': 'eq'},
            Columns.week: {'value': week, 'operator': 'eq'},
            Columns.computed_data: {'value': True, 'operator': 'eq'}
        }
        team_data = self.adapter.get_filtered_data(filters=team_filters)

        # Get all rounds (matches) for this team in this event
        rounds = sorted(player_data[Columns.round_number].unique())
        
        # Get all unique players who played in this event
        # Use player_id as primary identifier, fallback to player_name
        player_identifiers = []
        for _, row in player_data.iterrows():
            player_id = row[Columns.player_id] if not pd.isnull(row[Columns.player_id]) else row[Columns.player_name]
            player_name = row[Columns.player_name]
            # Create a unique identifier combining ID and name
            identifier = f"{player_id}_{player_name}"
            if identifier not in [p['identifier'] for p in player_identifiers]:
                player_identifiers.append({
                    'identifier': identifier,
                    'player_id': player_id,
                    'player_name': player_name
                })
        
        players = [p['identifier'] for p in player_identifiers]

        # Build columns
        columns = [
            ColumnGroup(
                title=i18n_service.get_text("match"),
                columns=[
                    Column(title=i18n_service.get_text("opponent"), field="opponent", width="120px", align="left", sortable=False),
                    Column(title=i18n_service.get_text("total_points"), field="team_total_points", width="100px", align="center", sortable=False,
                           style={"fontWeight": "bold"}, decimal_places=0),
                ]
                #style={"borderRight": "2px solid #264653"}  # Vertical bar after Opponents group (same color as other borders)
            ),
            ColumnGroup(
                title=team,
                columns=[
                    Column(title=i18n_service.get_text("pins"), field="team_score", width="80px", align="center", sortable=False, decimal_places=0),
                    Column(title=i18n_service.get_text("points"), field="team_points", width="80px", align="center", sortable=False, decimal_places=0),
                      # Make Total Points column bold
                ]
            )
        ]
        for player_info in player_identifiers:
            player_name = player_info['player_name']
            columns.append(
                ColumnGroup(
                    title=player_name,
                    columns=[
                        Column(title=i18n_service.get_text("pins"), field=f"{player_info['identifier']}_score", width="80px", align="center", sortable=False, decimal_places=0),
                        Column(title=i18n_service.get_text("points"), field=f"{player_info['identifier']}_points", width="50px", align="center", sortable=False, decimal_places=0),
                        Column(title=i18n_service.get_text("position"), field=f"{player_info['identifier']}_pos", width="50px", align="center", sortable=False, decimal_places=0),
                        
                    ]
                )
            )

        # Build data rows (one per round)
        data = []
        row_metadata = []
        for rnd in rounds:
            row = []
            # Opponent name for this round
            round_data = player_data[player_data[Columns.round_number] == rnd]
            opponent = round_data[Columns.team_name_opponent].iloc[0] if not round_data.empty else ""
            row.append(str(opponent))
            # Team totals for this round
            team_row = team_data[team_data[Columns.round_number] == rnd] if not team_data.empty else pd.DataFrame()
            team_score = int(team_row[Columns.score].iloc[0]) if not team_row.empty else 0
            team_points = float(team_row[Columns.points].iloc[0]) if not team_row.empty else 0.0
            # Total Points = sum of all individual points + team points
            indiv_points = float(round_data[Columns.points].sum()) if not round_data.empty else 0.0
            total_points = indiv_points + team_points
            row.append(total_points)
            row.append(team_score)
            row.append(team_points)
            
            # For each player, get their data for this round
            for player_info in player_identifiers:
                # Find all rows for this player in this round
                pdata = round_data[
                    (round_data[Columns.player_id] == player_info['player_id']) | 
                    (round_data[Columns.player_name] == player_info['player_name'])
                ]
                
                if not pdata.empty:
                    # If player played multiple positions, aggregate the data
                    total_score = int(pdata[Columns.score].sum()) if not pdata.empty else ""
                    total_points = float(pdata[Columns.points].sum()) if not pdata.empty else ""
                    
                    # For position, show all positions played (e.g., "0,1" if played both positions)
                    positions = sorted(pdata[Columns.position].dropna().unique())
                    pos_str = ",".join([str(int(pos + 1)) for pos in positions]) if len(positions) > 0 else ""
                    
                    row.extend([total_score, total_points, pos_str])
                else:
                    row.extend(["", "", ""])
            
            data.append(row)
            row_metadata.append({'rowType': 'match', 'styling': {}})

        # Add summary row
        summary_row = ["Total", 0, 0.0, 0.0]
        for player_info in player_identifiers:
            # Find all rows for this player in the entire event
            player_rows = player_data[
                (player_data[Columns.player_id] == player_info['player_id']) | 
                (player_data[Columns.player_name] == player_info['player_name'])
            ]
            total_score = int(player_rows[Columns.score].sum()) if not player_rows.empty else 0
            total_points = float(player_rows[Columns.points].sum()) if not player_rows.empty else 0.0
            summary_row.extend([total_score, total_points, ""])
        # Team total score/points for all rounds
        team_score_total = int(team_data[Columns.score].sum()) if not team_data.empty else 0
        team_points_total = float(team_data[Columns.points].sum()) if not team_data.empty else 0.0
        indiv_points_total = float(player_data[Columns.points].sum()) if not player_data.empty else 0.0
        team_total_points_total = indiv_points_total + team_points_total
        summary_row[1] = team_total_points_total
        summary_row[2] = team_score_total
        summary_row[3] = team_points_total
        data.append(summary_row)
        row_metadata.append({'rowType': 'summary', 'styling': {'fontWeight': 'bold', 'borderTop': '2px solid #000000'}})
            
        return TableData(
                columns=columns,
                data=data,
            row_metadata=row_metadata,
            title=f"{team} - Individual Scores (Week {week})",
            description=f"All individual scores for {team} in {league} - {season}, week {week}",
                config={
                    "stickyHeader": True,
                    "striped": True,
                    "hover": True,
                    "responsive": True,
                    "compact": False
            }
        )

    # ==========================================
    # AGGREGATION ENDPOINTS (League-wide over time)
    # ==========================================

    def get_league_averages_history(self, league: str, debug: bool = False) -> Dict[str, Any]:
        """Get league average scores across all seasons"""
        try:
            seasons = self.get_seasons()
            
            # Get league averages for each season
            season_averages = {}
            valid_seasons = []
            
            for season in seasons:
                try:
                    # Use existing team averages method and calculate league average
                    team_averages = self.get_team_averages_simple(league, season)
                    
                    if team_averages and 'data' in team_averages:
                        # Calculate overall league average for the season
                        all_averages = []
                        for team_name, team_data in team_averages['data'].items():
                            if isinstance(team_data, list) and team_data:
                                # Get final average (last value in the series)
                                final_avg = team_data[-1] if team_data[-1] is not None else 0
                                all_averages.append(final_avg)
                        
                        if all_averages:
                            league_avg = sum(all_averages) / len(all_averages)
                            season_averages[season] = league_avg
                            valid_seasons.append(season)
                            
                except Exception as e:
                    print(f"ERROR calculating average for {league} {season}: {e}")
                    continue
            
            # Prepare data for line chart
            result = {
                'data': {'League Average': [season_averages.get(season, 0) for season in valid_seasons]},
                'seasons': valid_seasons,
                'labels': valid_seasons,
                'title': f'{league} - Average Scores by Season',
                'y_axis_title': 'Average Score'
            }
            return result
            
        except Exception as e:
            print(f"ERROR in get_league_averages_history: {e}")
            return {'data': {}, 'seasons': [], 'labels': []}

    def get_points_to_win_history(self, league: str, debug: bool = False) -> Dict[str, Any]:
        """Get total league points earned by the winning team across seasons"""
        try:
            seasons = self.get_seasons()
            
            season_points = {}
            valid_seasons = []
            
            for season in seasons:
                try:
                    
                    # Filter data for league + season
                    filters = {
                        Columns.league_name: {'value': league, 'operator': 'eq'},
                        Columns.season: {'value': season, 'operator': 'eq'}
                    }
                    
                    season_data = self.adapter.get_filtered_data(filters=filters)
                    
                    if not season_data.empty:
                        # Group by team_name and sum Columns.points
                        team_totals = season_data.groupby(Columns.team_name)[Columns.points].sum().reset_index()
                        
                        if not team_totals.empty:
                            # Sort by sum of points (descending) and take top entry
                            team_totals = team_totals.sort_values(by=Columns.points, ascending=False)
                            winning_team_points = team_totals.iloc[0][Columns.points]
                            winning_team_name = team_totals.iloc[0][Columns.team_name]
                            
                            season_points[season] = winning_team_points
                            valid_seasons.append(season)
                                
                except Exception as e:
                    print(f"ERROR getting winning team league points for {league} {season}: {e}")
                    continue
            
            result = {
                'data': {'League Points to Win': [season_points.get(season, 0) for season in valid_seasons]},
                'seasons': valid_seasons,
                'labels': valid_seasons,
                'title': f'{league} - League Points Needed to Win by Season',
                'y_axis_title': 'Total League Points'
            }
            return result
            
        except Exception as e:
            print(f"ERROR in get_points_to_win_history: {e}")
            return {'data': {}, 'seasons': [], 'labels': []}

    def get_top_team_performances(self, league: str) -> TableData:
        """Get top team performances across all seasons based on team averages"""
        try:
            seasons = self.get_seasons()
            all_performances = []
            
            for season in seasons:
                try:
                    # Get team averages for the season
                    team_averages_data = self.get_team_averages_simple(league, season)
                    
                    if team_averages_data and 'data' in team_averages_data:
                        # Extract team averages (final values from the season)
                        for team_name, avg_series in team_averages_data['data'].items():
                            if isinstance(avg_series, list) and avg_series:
                                # Get final average (last value in the series)
                                final_average = avg_series[-1] if avg_series[-1] is not None else 0
                                
                                all_performances.append([
                                    team_name,
                                    format_float_one_decimal(final_average),
                                    season,
                                    league  # Add league as second-to-last
                                ])
                                
                except Exception as e:
                    print(f"Error processing season {season}: {e}")
                    continue
            
            # Sort by average descending (now index 3)
            all_performances.sort(key=lambda x: x[3] if isinstance(x[3], (int, float)) else 0, reverse=True)
            
            # Create table structure - remove ColumnGroup title (use empty string)
            columns = [
                ColumnGroup(
                    title="",  # Empty title since it's shown in card header
                    columns=[
                        Column(title=i18n_service.get_text("team"), field="team", width="180px", align="left"),
                        Column(title=i18n_service.get_text("average"), field="average", width="90px", align="center", decimal_places=1),
                        Column(title=i18n_service.get_text("season"), field="season", width="90px", align="center"),
                        Column(title=i18n_service.get_text("league"), field="league", width="90px", align="left")
                    ]
                )
            ]
            
            return TableData(
                columns=columns,
                data=all_performances[:20],  # Top 20 performances by average
                title=f"{league} - Top Team Performances",
                description="Best team season averages across all years",
                default_sort={"field": "average", "dir": "desc"}  # Sort by average descending
            )
            
        except Exception as e:
            print(f"Error in get_top_team_performances: {e}")
            return TableData(columns=[], data=[], title=i18n_service.get_text("error_loading_data"))

    def get_season_timetable(self, league: str, season: str) -> TableData:
        """Get season timetable with match day schedule as structured table data"""
        try:
            # Get available weeks for the season
            available_weeks = self.get_available_weeks(season, league)
            
            if not available_weeks:
                return TableData(
                    columns=[],
                    data=[],
                    title=f"No timetable available for {league} - {season}"
                )
            
            latest_week = self.get_latest_week(season, league)
            
            # Get actual week data with dates and locations from the database
            filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.computed_data: {'value': True, 'operator': 'eq'}  # Get team summary data
            }
            
            week_data = self.adapter.get_filtered_data(filters=filters)
    
            
            # Group data by week to get unique week info
            week_info = {}
            for _, row in week_data.iterrows():
                week_num = row[Columns.week]
                if week_num not in week_info:
                    week_info[week_num] = {
                        'date': row.get(Columns.date, 'TBD'),
                        'location': row.get(Columns.location, f"{league} Venue"),
                        'has_data': True
                    }
            
            # Create table data only for existing weeks
            table_data = []
            for week_num in sorted(available_weeks):
                is_completed = week_num <= latest_week
                
                # Get real data if available
                if week_num in week_info:
                    date = week_info[week_num]['date']
                    location = week_info[week_num]['location']
                else:
                    date = "TBD"
                    location = f"{league} Venue"
                
                # Determine status
                if is_completed:
                    status = "✅ Completed"
                elif week_num in available_weeks:
                    status = "📊 Data Available"
                else:
                    status = "⏳ Pending"
                
                table_data.append([
                    week_num,
                    date if date and str(date) != 'nan' else "TBD",
                    location if location and str(location) != 'nan' else f"{league} Venue",
                    status
                ])
            
            # Create table structure - can pass bare Columns directly, no need for ColumnGroup wrapper
            columns = [
                Column(title=i18n_service.get_text("week"), field="week", width="100px", align="center", decimal_places=0),
                Column(title=i18n_service.get_text("date"), field="date", width="120px", align="center"),
                Column(title=i18n_service.get_text("location"), field="location", width="200px", align="left"),
                Column(title=i18n_service.get_text("status"), field="status", width="150px", align="center")
            ]
            
            return TableData(
                columns=columns,
                data=table_data,
                title=f"{league} {season} - Match Schedule",
                description="Season timetable and completion status"
            )
            
        except Exception as e:
            print(f"Error in get_season_timetable: {e}")
            return TableData(columns=[], data=[], title=i18n_service.get_text("error_loading_timetable"))

    def get_individual_averages(self, league: str, season: str, week: int = None, team: str = None) -> TableData:
        """Get individual player averages for a season, optionally filtered by week and/or team, sorted by performance"""
        try:
            filter_text = ""
            if week is not None:
                filter_text += f" for week {week}"
            if team is not None:
                filter_text += f" for team {team}"
    
            
            # Get all player data for the league/season (and optionally week/team)
            filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}  # Individual players only
            }
            if isinstance(week, str) and week.isdigit():
                week = int(week)
            
            # Add week filter if specified
            if week is not None:
                filters[Columns.week] = {'value': week, 'operator': 'eq'}
                
            # Add team filter if specified
            if team is not None:
                filters[Columns.team_name] = {'value': team, 'operator': 'eq'}
    
            
            player_data = self.adapter.get_filtered_data(filters=filters)

            
            if player_data.empty:
                return TableData(
                    columns=[],
                    data=[],
                    title=f"No individual data available for {league} - {season}"
                )
            

            
            # Calculate averages per player
            player_stats = {}
            
            for _, row in player_data.iterrows():
                player_name = row[Columns.player_name]
                team_name = row[Columns.team_name]
                score = row[Columns.score]
                
                # Skip rows with missing essential data
                if pd.isna(player_name) or pd.isna(team_name):
                    continue
                
                # Create unique player identifier
                player_key = f"{player_name}|{team_name}"
                
                if player_key not in player_stats:
                    player_stats[player_key] = {
                        'player_name': player_name,
                        'team_name': team_name,
                        'scores': [],
                        'games': 0
                    }
                
                # Count all games, even if score is missing (DNP, etc.)
                player_stats[player_key]['games'] += 1
                
                # Only add valid scores to the calculation
                if pd.notna(score) and isinstance(score, (int, float)):
                    player_stats[player_key]['scores'].append(score)
            
    
            
            # Calculate averages and prepare table data
            table_data = []
            for player_key, stats in player_stats.items():
                if stats['games'] > 0:
                    # Handle players with no valid scores (DNP, etc.)
                    if len(stats['scores']) > 0:
                        average = sum(stats['scores']) / len(stats['scores'])
                        total_points = sum(stats['scores'])
                        high_game = max(stats['scores'])
                    else:
                        # Player has games but no valid scores
                        average = 0.0
                        total_points = 0.0
                        high_game = 0.0
                    
                    table_data.append([
                        stats['player_name'],
                        stats['team_name'],
                        stats['games'],
                        round(total_points, 1),
                        round(average, 1),
                        round(high_game, 1)
                    ])
            
    
            
            # Sort by average descending (index 4 now contains average)
            table_data.sort(key=lambda x: x[4], reverse=True)
            
            # Create table structure
            columns = [
                Column(title=i18n_service.get_text("player"), field="player", width="180px", align="left"),
                Column(title=i18n_service.get_text("team"), field="team", width="130px", align="left"),
                Column(title=i18n_service.get_text("games"), field="games", width="70px", align="center", decimal_places=0),
                Column(title=i18n_service.get_text("total_points"), field="total_points", width="100px", align="center", decimal_places=0),
                Column(title=i18n_service.get_text("average"), field="average", width="90px", align="center", decimal_places=1),
                Column(title=i18n_service.get_text("high_game"), field="high_game", width="90px", align="center", decimal_places=0)
            ]
                
            
            # Build title with i18n and article_male + season/week logic (description content moved to title)
            if week is not None:
                title = f"{i18n_service.get_text('individual_performance')} {i18n_service.get_text('week')} {week}"
            else:
                title = f"{i18n_service.get_text('individual_performance')} {i18n_service.get_text('article_male')} {i18n_service.get_text('season')}"
            
            if team is not None:
                # Add team info if specified
                title += f" - {team}"
            
            return TableData(
                columns=columns,
                data=table_data,
                title=title,
                description=None
            )
            
        except Exception as e:
            print(f"ERROR in get_individual_averages: {e}")
            import traceback
            print(f"TRACEBACK: {traceback.format_exc()}")
            return TableData(columns=[], data=[], title=i18n_service.get_text("error_loading_individual_averages"))

    def get_top_individual_performances(self, league: str) -> TableData:
        """Get top individual performances across all seasons"""
        try:
            seasons = self.get_seasons()
            
            # Also check what leagues exist in the data
            league_filters = {}
            all_league_data = self.adapter.get_filtered_data(filters=league_filters)
            unique_leagues = all_league_data[Columns.league_name].unique() if not all_league_data.empty else []
            
            all_performances = []
            
            for season in seasons:
                try:
                    
                    # First check if any data exists for this league/season combination
                    basic_filters = {
                        Columns.league_name: {'value': league, 'operator': 'eq'},
                        Columns.season: {'value': season, 'operator': 'eq'}
                    }
                    basic_data = self.adapter.get_filtered_data(filters=basic_filters)
                    
                    if not basic_data.empty:
                        computed_data_values = basic_data[Columns.computed_data].unique()
                        individual_rows = basic_data[basic_data[Columns.computed_data] == False]
                        team_rows = basic_data[basic_data[Columns.computed_data] == True]
                    
                    # Get individual averages for each season
                    individual_data = self.get_individual_averages(league, season)
                    
                    if individual_data and individual_data.data:
                        # Take top 5 from each season
                        for row in individual_data.data[:5]:
                            # New individual_averages structure: [player_name, team_name, games, total_points, average, high_game]
                            if len(row) >= 6:
                                performance_entry = [
                                    row[0],  # player_name
                                    format_float_one_decimal(row[4]),  # average (index 4 in the new structure)
                                    season,
                                    league,   # Add league as second-to-last
                                    row[1]   # team_name
                                ]
                                all_performances.append(performance_entry)
                                
                except Exception as e:
                    print(f"ERROR: processing individual data for season {season}: {e}")
                    import traceback
                    print(f"TRACEBACK: {traceback.format_exc()}")
                    continue
            

            
            # Sort by average descending (now index 4 since we added league)
            all_performances.sort(key=lambda x: x[4] if isinstance(x[4], (int, float)) else 0, reverse=True)
            
            # Create table structure - remove ColumnGroup title (use empty string)
            columns = [
                ColumnGroup(
                    title="",  # Empty title since it's shown in card header
                    columns=[
                        Column(title=i18n_service.get_text("player"), field="player", width="180px", align="left"),
                        Column(title=i18n_service.get_text("average"), field="average", width="90px", align="center", decimal_places=1),
                        Column(title=i18n_service.get_text("season"), field="season", width="90px", align="center"),
                        Column(title=i18n_service.get_text("league"), field="league", width="90px", align="left"),
                        Column(title=i18n_service.get_text("team"), field="team", width="180px", align="left")                        
                    ]
                )
            ]
            
            result_data = all_performances[:30]  # Top 30 individual performances

            
            return TableData(
                columns=columns,
                data=result_data,
                title=f"{league} - Top Individual Performances",
                description="Best individual averages across all seasons",
                default_sort={"field": "average", "dir": "desc"}  # Sort by average descending
            )
            
        except Exception as e:
            print(f"ERROR in get_top_individual_performances: {e}")
            import traceback
            print(f"TRACEBACK: {traceback.format_exc()}")
            return TableData(columns=[], data=[], title=i18n_service.get_text("error_loading_data"))

    def get_record_individual_games(self, league: str) -> TableData:
        """Get record individual games (highest scoring individual performances)"""
        try:
            seasons = self.get_seasons()
            record_games = []
            
            for season in seasons:
                try:
                    # Get all individual data for the season to find high scores
                    filters = {
                        Columns.league_name: {'value': league, 'operator': 'eq'},
                        Columns.season: {'value': season, 'operator': 'eq'},
                        Columns.computed_data: {'value': False, 'operator': 'eq'}
                    }
                    
                    player_data = self.adapter.get_filtered_data(filters=filters)
                    
                    if not player_data.empty:
                        # Find highest individual games (top 3 per season)
                        highest_individual = player_data.nlargest(3, Columns.score)
                        
                        for _, row in highest_individual.iterrows():
                            record_games.append([
                                row[Columns.player_name],
                                row[Columns.score],
                                season,
                                league,   # Add league as second-to-last
                                row[Columns.team_name],
                                row[Columns.week] if Columns.week in row else ''
                            ])
                            
                except Exception as e:
                    print(f"Error processing individual record games for season {season}: {e}")
                    continue
            
            # Sort by score descending (now index 5)
            record_games.sort(key=lambda x: x[5] if isinstance(x[5], (int, float)) else 0, reverse=True)
            
            # Create table structure - remove ColumnGroup title (use empty string)
            columns = [
                ColumnGroup(
                    title="",  # Empty title since it's shown in card header
                    columns=[
                        Column(title=i18n_service.get_text("player"), field="player", width="180px", align="left"),
                        Column(title=i18n_service.get_text("score"), field="score", width="90px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("season"), field="season", width="90px", align="center"),
                        Column(title=i18n_service.get_text("league"), field="league", width="90px", align="left"),
                        Column(title=i18n_service.get_text("team"), field="team", width="180px", align="left"),
                        Column(title=i18n_service.get_text("week"), field="week", width="90px", align="center", decimal_places=0)
                    ]
                )
            ]
            
            return TableData(
                columns=columns,
                data=record_games[:15],  # Top 15 individual record games
                title=f"{league} - Record Individual Games",
                description="Highest scoring individual performances across all seasons",
                default_sort={"field": "score", "dir": "desc"}  # Sort by score descending
            )
            
        except Exception as e:
            print(f"Error in get_record_individual_games: {e}")
            return TableData(columns=[], data=[], title=i18n_service.get_text("error_loading_individual_record_games"))

    def get_record_team_games(self, league: str) -> TableData:
        """Get record team games (highest scoring team performances)"""
        try:
            seasons = self.get_seasons()
            record_games = []
            
            for season in seasons:
                try:
                    # Get team totals for the season
                    team_filters = {
                        Columns.league_name: {'value': league, 'operator': 'eq'},
                        Columns.season: {'value': season, 'operator': 'eq'},
                        Columns.computed_data: {'value': True, 'operator': 'eq'}
                    }
                    
                    team_data = self.adapter.get_filtered_data(filters=team_filters)
                    
                    if not team_data.empty:
                        # Find highest team games (top 2 per season)
                        highest_team = team_data.nlargest(2, Columns.score)
                        
                        for _, row in highest_team.iterrows():
                            record_games.append([
                                row[Columns.team_name],
                                row[Columns.score],
                                season,
                                league,  # Add league as second-to-last
                                row[Columns.week] if Columns.week in row else ''
                            ])
                            
                except Exception as e:
                    print(f"Error processing team record games for season {season}: {e}")
                    continue
            
            # Sort by score descending (now index 4)
            record_games.sort(key=lambda x: x[4] if isinstance(x[4], (int, float)) else 0, reverse=True)
            
            # Create table structure - remove ColumnGroup title (use empty string)
            columns = [
                ColumnGroup(
                    title="",  # Empty title since it's shown in card header
                    columns=[
                        Column(title=i18n_service.get_text("team"), field="team", width="180px", align="left"),
                        Column(title=i18n_service.get_text("score"), field="score", width="90px", align="center", decimal_places=0),
                        Column(title=i18n_service.get_text("season"), field="season", width="90px", align="center"),
                        Column(title=i18n_service.get_text("league"), field="league", width="90px", align="left"),
                        Column(title=i18n_service.get_text("week"), field="week", width="90px", align="center", decimal_places=0),
                    ]
                        
                )
            ]
            
            return TableData(
                columns=columns,
                data=record_games[:15],  # Top 15 team record games
                title=f"{league} - Record Team Games",
                description="Highest scoring team performances across all seasons",
                default_sort={"field": "score", "dir": "desc"}  # Sort by score descending

            )
            
        except Exception as e:
            print(f"Error in get_record_team_games: {e}")
            return TableData(columns=[], data=[], title=i18n_service.get_text("error_loading_team_record_games"))

    def _convert_to_simple_types(self, data):
        """Convert numpy types to simple Python types for JSON serialization (delegates to utility function)"""
        return convert_to_simple_types(data)

    def get_team_analysis(self, league: str, season: str, team: str) -> Dict[str, Any]:
        """Get detailed team analysis including individual player performance and win percentages"""
        try:
            # Get all player data for the team in the specified season and league
            # EXCLUDE team totals - only get individual player records
            player_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.team_name: {'value': team, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}  # Individual players only
            }
            
            player_data = self.adapter.get_filtered_data(filters=player_filters)
            
            if not player_data.empty:
                # Filter out team totals - only keep individual player records
                # Team totals typically have "Team Total" or similar in the Player column
                player_data = player_data[player_data[Columns.player_name] != 'Team Total']
                player_data = player_data[player_data[Columns.player_name] != 'team_total']
                player_data = player_data[player_data[Columns.player_name] != 'TEAM TOTAL']
                
                # Also filter out any records where Player ID is NaN (these are usually team totals)
                player_data = player_data.dropna(subset=[Columns.player_id])
            
            if player_data.empty:
                return {
                    'error': f'No individual player data found for team {team} in {league} {season}',
                    'performance_data': [],
                    'win_percentage_data': [],
                    'weeks': [],
                    'players': []
                }
            
            # Get unique weeks and players
            weeks = sorted(player_data[Columns.week].unique())
            players = sorted(player_data[Columns.player_name].unique())
            
            # Get individual player matches for PvP win calculation
            individual_matches = self.get_individual_matches(team=team, season=season, league=league)
            
            # Get team matches for team win percentage
            team_matches = self.adapter.get_matches(team=team, season=season, league=league)
            
            # Create SeriesData objects for charts
            performance_series = SeriesData(
                label_x_axis="Spieltag",
                label_y_axis="Durchschnittliche Punkte",
                name=f"Leistung {team}",
                query_params={'league': league, 'season': season, 'team': team}
            )
            
            win_percentage_series = SeriesData(
                label_x_axis="Spieltag", 
                label_y_axis="Siegquote (%)",
                name=f"Siegquote {team}",
                query_params={'league': league, 'season': season, 'team': team}
            )
            
            # Add individual player data to performance series
            for player in players:
                player_week_scores = []
                player_total_score = 0
                player_total_games = 0
                
                for week in weeks:
                    week_data = player_data[
                        (player_data[Columns.player_name] == player) & 
                        (player_data[Columns.week] == week)
                    ]
                    
                    if not week_data.empty:
                        # Calculate average score per game for this player in this week
                        week_total_score = float(week_data[Columns.score].sum())
                        week_games = len(week_data)
                        week_avg_score = round(week_total_score / week_games, 2) if week_games > 0 else 0
                        player_week_scores.append(week_avg_score)
                        
                        # Accumulate totals for correct calculation
                        player_total_score += week_total_score
                        player_total_games += week_games
                        
                    else:
                        player_week_scores.append(None)  # Use None for missing data
                
                # Add data to series
                performance_series.add_data(player, player_week_scores)
                
                # Override the incorrect totals with correct ones
                performance_series.total[player] = round(player_total_score, 2)
                performance_series.average[player] = round(player_total_score / player_total_games, 2) if player_total_games > 0 else 0
                
                # Store count of valid data points for frontend use
                performance_series.counts[player] = player_total_games
                
            
            # Add team average to performance series
            team_week_scores = []
            team_total_score = 0
            team_total_games = 0
            
            for week in weeks:
                week_data = player_data[player_data[Columns.week] == week]
                if not week_data.empty:
                    # Calculate team average per person per game for this week
                    week_total_score = float(week_data[Columns.score].sum())
                    week_games = len(week_data)
                    week_avg_score = round(week_total_score / week_games, 2) if week_games > 0 else 0
                    team_week_scores.append(week_avg_score)
                    
                    # Accumulate totals for correct calculation
                    team_total_score += week_total_score
                    team_total_games += week_games
                else:
                    team_week_scores.append(None)  # Use None for missing data
            
            # Add data to series
            performance_series.add_data(f"{team}", team_week_scores)
            
            # Override the incorrect totals with correct ones
            performance_series.total[f"{team}"] = round(team_total_score, 2)
            performance_series.average[f"{team}"] = round(team_total_score / team_total_games, 2) if team_total_games > 0 else 0
            
            # Store count of valid data points for frontend use
            performance_series.counts[f"{team}"] = team_total_games
            
            # Add individual player win percentage data
            for player in players:
                player_week_wins = []
                player_total_wins = 0
                player_total_matches = 0
                
                for week in weeks:
                    if not individual_matches.empty:
                        # Get individual matches for this player in this week
                        week_matches = individual_matches[
                            (individual_matches['player_name'] == player) & 
                            (individual_matches['week'] == week)
                        ]
                        
                        if not week_matches.empty:
                            # Count PvP wins for this player in this week
                            week_wins = int(week_matches['is_win'].sum())
                            week_matches_count = len(week_matches)
                            week_win_pct = round((week_wins / week_matches_count) * 100, 1) if week_matches_count > 0 else 0
                            player_week_wins.append(week_win_pct)
                            
                            # Accumulate totals for correct calculation
                            player_total_wins += week_wins
                            player_total_matches += week_matches_count
                        else:
                            player_week_wins.append(None)  # Use None for missing data
                    else:
                        player_week_wins.append(None)  # Use None for missing data
                
                # Add data to series
                win_percentage_series.add_data(player, player_week_wins)
                
                # Override the incorrect totals with correct ones
                win_percentage_series.total[player] = player_total_wins
                win_percentage_series.average[player] = round((player_total_wins / player_total_matches) * 100, 1) if player_total_matches > 0 else 0
                
                # Store count of valid data points for frontend use
                win_percentage_series.counts[player] = player_total_matches
            
            # Add team win percentage
            team_week_wins = []
            team_total_wins = 0
            team_total_matches = 0
            
            for week in weeks:
                week_matches = team_matches[team_matches[Columns.week] == week]
                week_wins = 0
                week_matches_count = 0
                
                for _, match in week_matches.iterrows():
                    team_score = match[Columns.score]
                    opponent_score = match['opponent_score']
                    
                    if team_score > opponent_score:
                        week_wins += 1
                    week_matches_count += 1
                
                if week_matches_count > 0:
                    week_win_pct = round((week_wins / week_matches_count) * 100, 1)
                    team_week_wins.append(week_win_pct)
                else:
                    team_week_wins.append(None)  # Use None for missing data
                
                # Accumulate totals for correct calculation
                team_total_wins += week_wins
                team_total_matches += week_matches_count
            
            # Add data to series
            win_percentage_series.add_data(f"{team}", team_week_wins)
            
            # Override the incorrect totals with correct ones
            win_percentage_series.total[f"{team}"] = team_total_wins
            win_percentage_series.average[f"{team}"] = round((team_total_wins / team_total_matches) * 100, 1) if team_total_matches > 0 else 0
            
            # Store count of valid data points for frontend use
            win_percentage_series.counts[f"{team}"] = team_total_matches
            
            # Return data using existing SeriesData interface
            return {
                'performance_data': performance_series.to_dict(),
                'win_percentage_data': win_percentage_series.to_dict(),
                'weeks': [f'Week {int(w)}' for w in weeks],
                'players': [str(p) for p in players],
                'team': str(team),
                'league': str(league),
                'season': str(season)
            }
            
        except Exception as e:
            print(f"Error in get_team_analysis: {e}")
            return {
                'error': f'Error analyzing team data: {str(e)}',
                'performance_data': [],
                'win_percentage_data': [],
                'weeks': [],
                'players': []
            }

    def get_team_performance_table_data(self, league: str, season: str, team: str) -> TableData:
        """Get team performance table as TableData - can be passed directly to createTableTabulator"""
        try:
            # Reuse the data collection logic from get_team_analysis
            analysis_data = self.get_team_analysis(league=league, season=season, team=team)
            
            if 'error' in analysis_data:
                return TableData(
                    columns=[],
                    data=[],
                    title=f"Error: {analysis_data['error']}"
                )
            
            performance_data = analysis_data.get('performance_data', {})
            # weeks comes as list of strings like ['Week 1', 'Week 2', ...], extract count
            weeks_list = analysis_data.get('weeks', [])
            num_weeks = len(weeks_list) if weeks_list else 0
            team_name = analysis_data.get('team', team)
            teamAverageKey = f"{team_name}"
            
            # Debug: Check if we have data
            if num_weeks == 0:
                print(f"WARNING: No weeks data in get_team_performance_table_data for {team} in {league} {season}")
                print(f"analysis_data keys: {list(analysis_data.keys())}")
                print(f"performance_data keys: {list(performance_data.keys()) if isinstance(performance_data, dict) else type(performance_data)}")
            
            # Build columns
            columns = [
                ColumnGroup(
                    title=i18n_service.get_text('player'),
                    columns=[
                        Column(title='', field='player_initials', width='50px', align='center'),
                        Column(title=i18n_service.get_text('player'), field='player_name', width='180px', align="left")
                    ]
                )
            ]
            
            # Add week columns
            week_columns = []
            for idx in range(num_weeks):
                week_columns.append(
                    Column(
                        title=f"{idx + 1}",
                        field=f'week_{idx + 1}',
                        width='80px',
                        align='center',
                        tooltip=i18n_service.get_text('match_day_label') + ' ' + str(idx + 1),
                        decimal_places=1  # Weekly averages typically have 1 decimal place
                    )
                )
            if week_columns:
                columns.append(ColumnGroup(
                    title=i18n_service.get_text('ui.team_performance.weekly_avg_game'),
                    columns=week_columns
                ))
            
            # Add totals columns
            columns.append(ColumnGroup(
                title=i18n_service.get_text('ui.win_percentage.totals'),
                columns=[
                    Column(title=i18n_service.get_text('ui.team_performance.total_score'), field='total_score', width='100px', align='center', decimal_places=0),
                    Column(title=i18n_service.get_text('games'), field='total_games', width='80px', align='center', decimal_places=0),
                    Column(title=i18n_service.get_text('ui.team_performance.avg_per_game'), field='avg_per_game', width='100px', align='center', decimal_places=1)
                ]
            ))
            
            # Build data rows
            table_data = []
            data_dict = performance_data.get('data', {})
            total_dict = performance_data.get('total', {})
            average_dict = performance_data.get('average', {})
            counts_dict = performance_data.get('counts', {})
            
            # Process individual players first
            for playerName in sorted(data_dict.keys()):
                if playerName == teamAverageKey:
                    continue
                
                playerData = data_dict[playerName]
                row = {
                    'player_initials': playerName[0].upper() if playerName else '',
                    'player_name': playerName
                }
                
                # Add week data
                for idx in range(num_weeks):
                    weekValue = playerData[idx] if idx < len(playerData) else None
                    row[f'week_{idx + 1}'] = weekValue
                
                # Add totals
                row['total_score'] = round(total_dict.get(playerName, 0) * 100) / 100
                row['total_games'] = counts_dict.get(playerName, 0)
                row['avg_per_game'] = round(average_dict.get(playerName, 0) * 100) / 100
                
                table_data.append(row)
            
            # Add team average as last row
            if teamAverageKey in data_dict:
                teamData = data_dict[teamAverageKey]
                row = {
                    'player_initials': 'T',
                    'player_name': teamAverageKey
                }
                
                for idx in range(num_weeks):
                    weekValue = teamData[idx] if idx < len(teamData) else None
                    row[f'week_{idx + 1}'] = weekValue
                
                row['total_score'] = round(total_dict.get(teamAverageKey, 0) * 100) / 100
                row['total_games'] = counts_dict.get(teamAverageKey, 0)
                row['avg_per_game'] = round(average_dict.get(teamAverageKey, 0) * 100) / 100
                
                table_data.append(row)
            
            # Row metadata for team average row (bold)
            row_metadata = []
            for idx, row in enumerate(table_data):
                if row['player_name'] == teamAverageKey:
                    row_metadata.append({
                        'styling': {
                            'fontWeight': 'bold',
                            'backgroundColor': get_theme_color('background') or '#f8f9fa'
                        }
                    })
                else:
                    row_metadata.append({})
            
            result = TableData(
                columns=columns,
                data=table_data,
                title=f"{team_name} - {i18n_service.get_text('ui.team_performance.player_performance')}",
                description=i18n_service.get_text('ui.team_performance.player_perf_desc'),
                row_metadata=row_metadata,
                config={
                    'striped': True,
                    'hover': True,
                    'compact': True,
                    'stickyHeader': True,
                    'numberOfdecimalplaces': 1
                }
            )
            
            return result
            
        except Exception as e:
            print(f"Error in get_team_performance_table_data: {e}")
            return TableData(
                columns=[],
                data=[],
                title=f"Error: {str(e)}"
            )
    
    def get_team_win_percentage_table_data(self, league: str, season: str, team: str) -> TableData:
        """Get team win percentage table as TableData - can be passed directly to createTableTabulator"""
        try:
            # Reuse the data collection logic from get_team_analysis
            analysis_data = self.get_team_analysis(league=league, season=season, team=team)
            
            if 'error' in analysis_data:
                return TableData(
                    columns=[],
                    data=[],
                    title=f"Error: {analysis_data['error']}"
                )
            
            win_percentage_data = analysis_data.get('win_percentage_data', {})
            # weeks comes as list of strings like ['Week 1', 'Week 2', ...], extract count
            weeks_list = analysis_data.get('weeks', [])
            num_weeks = len(weeks_list) if weeks_list else 0
            team_name = analysis_data.get('team', team)
            teamKey = f"{team_name}"
            
            # Debug: Check if we have data
            if num_weeks == 0:
                print(f"WARNING: No weeks data in get_team_win_percentage_table_data for {team} in {league} {season}")
                print(f"analysis_data keys: {list(analysis_data.keys())}")
                print(f"win_percentage_data keys: {list(win_percentage_data.keys()) if isinstance(win_percentage_data, dict) else type(win_percentage_data)}")
            
            # Build columns
            columns = [
                ColumnGroup(
                    title=i18n_service.get_text('player'),
                    columns=[
                        Column(title='', field='player_initials', width='50px', align='center'),
                        Column(title=i18n_service.get_text('ui.win_percentage.player'), field='player_name', width='180px', align='left')
                    ]
                )
            ]
            
            # Add week columns
            week_columns = []
            for idx in range(num_weeks):
                week_columns.append(
                    Column(
                        title=f"{idx + 1}",
                        field=f'week_{idx + 1}',
                        width='80px',
                        align='center',
                        tooltip=f"{i18n_service.get_text('week')} {idx + 1}",
                        decimal_places=1  # Win percentages typically have 1 decimal place
                    )
                )
            if week_columns:
                columns.append(ColumnGroup(
                    title=i18n_service.get_text('ui.win_percentage.weekly'),
                    columns=week_columns
                ))
            
            # Add totals columns
            columns.append(ColumnGroup(
                title=i18n_service.get_text('ui.win_percentage.totals'),
                columns=[
                    Column(title=i18n_service.get_text('ui.win_percentage.total_wins'), field='total_wins', width='100px', align='center', decimal_places=0),
                    Column(title=i18n_service.get_text('ui.win_percentage.total_matches'), field='total_matches', width='100px', align='center', decimal_places=0),
                    Column(title=i18n_service.get_text('ui.win_percentage.win_percentage'), field='win_percentage', width='80px', align='center', decimal_places=1)
                ]
            ))
            
            # Build data rows
            table_data = []
            data_dict = win_percentage_data.get('data', {})
            total_dict = win_percentage_data.get('total', {})
            average_dict = win_percentage_data.get('average', {})
            counts_dict = win_percentage_data.get('counts', {})
            
            # Process individual players first
            for playerName in sorted(data_dict.keys()):
                if playerName == teamKey:
                    continue
                
                playerData = data_dict[playerName]
                row = {
                    'player_initials': playerName[0].upper() if playerName else '',
                    'player_name': playerName
                }
                
                # Add week data
                for idx in range(num_weeks):
                    weekValue = playerData[idx] if idx < len(playerData) else None
                    row[f'week_{idx + 1}'] = weekValue
                
                # Add totals
                row['total_wins'] = total_dict.get(playerName, 0)
                row['total_matches'] = counts_dict.get(playerName, 0)
                row['win_percentage'] = average_dict.get(playerName, 0)
                
                table_data.append(row)
            
            # Add team as last row
            if teamKey in data_dict:
                teamData = data_dict[teamKey]
                row = {
                    'player_initials': 'T',
                    'player_name': teamKey
                }
                
                for idx in range(num_weeks):
                    weekValue = teamData[idx] if idx < len(teamData) else None
                    row[f'week_{idx + 1}'] = weekValue
                
                row['total_wins'] = total_dict.get(teamKey, 0)
                row['total_matches'] = counts_dict.get(teamKey, 0)
                row['win_percentage'] = average_dict.get(teamKey, 0)
                
                table_data.append(row)
            
            # Row metadata for team row (bold)
            row_metadata = []
            for idx, row in enumerate(table_data):
                if row['player_name'] == teamKey:
                    row_metadata.append({
                        'styling': {
                            'fontWeight': 'bold',
                            'backgroundColor': get_theme_color('background') or '#f8f9fa'
                        }
                    })
                else:
                    row_metadata.append({})
            
            result = TableData(
                columns=columns,
                data=table_data,
                title=f"{team_name} - {i18n_service.get_text('ui.win_percentage.title')}",
                description=i18n_service.get_text('ui.win_percentage.individual_desc'),
                row_metadata=row_metadata,
                config={
                    'striped': True,
                    'hover': True,
                    'compact': True,
                    'stickyHeader': True
                }
            )
            
            return result
            
        except Exception as e:
            print(f"Error in get_team_win_percentage_table_data: {e}")
            return TableData(
                columns=[],
                data=[],
                title=f"Error: {str(e)}"
            )

    def _apply_heat_map_to_columns(self, table_data: List[List], cell_metadata: Dict[str, Dict],
                                    column_indices: List[int], min_val: float = None, max_val: float = None) -> Dict[str, Dict]:
        """
        Apply heat map coloring to specified column indices (delegates to utility function).
        
        Args:
            table_data: List of rows, where each row is a list of values
            cell_metadata: Dictionary mapping "row:col" to cell metadata
            column_indices: List of column indices (0-based) to apply coloring to
            min_val: Optional minimum value for color scale. If None, calculated from data
            max_val: Optional maximum value for color scale. If None, calculated from data
            
        Returns:
            Updated cell_metadata dictionary
        """
        return apply_heat_map_to_columns(table_data, cell_metadata, column_indices, min_val, max_val)

    def get_team_vs_team_comparison_table(self, league: str, season: str, week: int = None) -> 'TableData':
        """
        Get team vs team comparison as TableData with heat map.
        Teams are sorted by average points (across all opponents) before table creation
        to ensure proper matrix alignment with diagonal cells.
        """
        from app.models.table_data import TableData, ColumnGroup, Column
        
        try:
            # ========== DATA COLLECTION ==========
            # Get all teams in the league/season
            team_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'},
                Columns.input_data: {'value': True, 'operator': 'eq'}
            }
            
            if week is not None:
                team_filters[Columns.week] = {'value': week, 'operator': 'eq'}
            
            teams_data = self.adapter.get_filtered_data(
                columns=[Columns.team_name], 
                filters=team_filters
            )
            
            if teams_data.empty:
                return TableData(
                    columns=[],
                    data=[],
                    title=i18n_service.get_text("team_vs_team_comparison_matrix"),
                    description="No data available",
                    config={"striped": True, "hover": True, "compact": True, "stickyHeader": True}
                )
            
            teams = sorted(teams_data[Columns.team_name].unique())
            
            # Get team match data (computed team totals)
            # Team totals have position=0 for both BayL and BZOL N1 structures
            team_total_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.computed_data: {'value': True, 'operator': 'eq'},
                Columns.input_data: {'value': False, 'operator': 'eq'},
                Columns.position: {'value': 0, 'operator': 'eq'}  # Team totals have position 0
            }
            
            if week is not None:
                team_total_filters[Columns.week] = {'value': week, 'operator': 'eq'}
            
            team_matches = self.adapter.get_filtered_data(
                columns=[Columns.team_name, Columns.team_name_opponent, Columns.score, Columns.points, Columns.week, Columns.round_number],
                filters=team_total_filters
            )
            
            # Get individual player data for the same matches to calculate total points
            individual_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'},
                Columns.input_data: {'value': True, 'operator': 'eq'}
            }
            
            if week is not None:
                individual_filters[Columns.week] = {'value': week, 'operator': 'eq'}
            
            individual_data = self.adapter.get_filtered_data(
                columns=[Columns.team_name, Columns.team_name_opponent, Columns.points, Columns.week, Columns.match_number, Columns.round_number],
                filters=individual_filters
            )
            
            if team_matches.empty:
                return TableData(
                    columns=[],
                    data=[],
                    title=i18n_service.get_text("team_vs_team_comparison_matrix"),
                    description="No match data available",
                    config={"striped": True, "hover": True, "compact": True, "stickyHeader": True}
                )
            
            # ========== CALCULATE COMPARISON DATA ==========
            comparison_data = {}
            for team in teams:
                comparison_data[team] = {}
                for opponent in teams:
                    if team != opponent:
                        # Get matches between this team and opponent
                        team_vs_opponent = team_matches[
                            (team_matches[Columns.team_name] == team) & 
                            (team_matches[Columns.team_name_opponent] == opponent)
                        ]
                        
                        if not team_vs_opponent.empty:
                            avg_score = round(team_vs_opponent[Columns.score].mean(), 1)
                            
                            # Calculate total points (individual + team match points)
                            total_points_list = []
                            for _, match in team_vs_opponent.iterrows():
                                round_number = match[Columns.round_number]
                                match_week = match[Columns.week]
                                
                                # Get team match points (0-3)
                                team_match_points = match[Columns.points]
                                
                                # Get individual points for this match
                                individual_match_data = individual_data[
                                    (individual_data[Columns.team_name] == team) & 
                                    (individual_data[Columns.team_name_opponent] == opponent) &
                                    (individual_data[Columns.week] == match_week)
                                ]
                                
                                # Filter by round number to get the specific match
                                individual_round_data = individual_match_data[
                                    individual_match_data[Columns.round_number] == round_number
                                ]
                                
                                individual_points = individual_round_data[Columns.points].sum() if not individual_round_data.empty else 0
                                
                                # Total points = individual points + team match points
                                total_points = individual_points + team_match_points
                                total_points_list.append(total_points)
                            
                            avg_points = round(sum(total_points_list) / len(total_points_list), 1) if total_points_list else 0.0
                        else:
                            avg_score = 0.0
                            avg_points = 0.0
                        
                        comparison_data[team][opponent] = {
                            'avg_score': avg_score,
                            'avg_points': avg_points
                        }
            
            # ========== DATA EXTENSION: Calculate team averages and sort ==========
            # Calculate average points for each team (across all opponents)
            team_avg_points = {}
            for team in teams:
                team_points_list = []
                for opponent in teams:
                    if team != opponent and opponent in comparison_data[team]:
                        team_points_list.append(comparison_data[team][opponent]['avg_points'])
                team_avg_points[team] = sum(team_points_list) / len(team_points_list) if team_points_list else 0
            
            # Sort teams by average points (descending) - this determines row/column order
            sorted_teams = sorted(teams, key=lambda t: team_avg_points[t], reverse=True)
            team_positions = {team: pos + 1 for pos, team in enumerate(sorted_teams)}
            
            # ========== CREATE TABLE STRUCTURE ==========
            columns = [
                ColumnGroup(
                    title=f'{i18n_service.get_text("opponent")} →',
                    frozen='left',
                    columns=[
                        Column(
                            title="#", 
                            field='pos', 
                            width='50px', 
                            align='center'
                        ),
                        Column(
                            title=f'{i18n_service.get_text("team")} ↓', 
                            field='team', 
                            width='180px', 
                            align='left'
                        )
                    ]
                )
            ]
            
            # Add average columns first (bold) - right after position/team group
            columns.append(ColumnGroup(
                title=i18n_service.get_text("average"),
                columns=[
                    Column(
                        title=i18n_service.get_text("score"), 
                        field='avg_score', 
                        width='80px', 
                        align='center',
                        tooltip=f'{i18n_service.get_text("average")} {i18n_service.get_text("score")} vs. all opponents'
                    ),
                    Column(
                        title=i18n_service.get_text("points"), 
                        field='avg_points', 
                        width='80px', 
                        align='center',
                        tooltip=f'{i18n_service.get_text("average")} {i18n_service.get_text("points")} vs. all opponents'
                    )
                ],
                header_style={"fontWeight": "bold"}
            ))
            
            # Add columns for each team (using sorted order)
            for team in sorted_teams:
                columns.append(ColumnGroup(
                    title=team,
                    columns=[
                        Column(
                            title=i18n_service.get_text("score"), 
                            field=f'{team}_score', 
                            width='80px', 
                            align='center',
                            tooltip=f'{i18n_service.get_text("average")} {i18n_service.get_text("score")} vs. {team}'
                        ),
                        Column(
                            title=i18n_service.get_text("points"), 
                            field=f'{team}_points', 
                            width='80px', 
                            align='center',
                            tooltip=f'{i18n_service.get_text("average")} {i18n_service.get_text("points")} vs. {team}'
                        )
                    ]
                ))
            
            # ========== GENERATE TABLE ROWS ==========
            table_data = []
            cell_metadata = {}
            
            # Collect all score and points values for heat map min/max calculation
            all_scores = []
            all_points = []
            
            for team in sorted_teams:
                for opponent in sorted_teams:
                    if team != opponent and opponent in comparison_data[team]:
                        all_scores.append(comparison_data[team][opponent]['avg_score'])
                        all_points.append(comparison_data[team][opponent]['avg_points'])
            
            if not all_scores or not all_points:
                return TableData(
                    columns=columns,
                    data=[],
                    title=i18n_service.get_text("team_vs_team_comparison_matrix"),
                    description="No match data available",
                    config={"striped": True, "hover": True, "compact": True, "stickyHeader": True}
                )
            
            score_min, score_max = min(all_scores), max(all_scores)
            points_min, points_max = min(all_points), max(all_points)
            
            # Determine column indices for heat map (same for all rows)
            # Position: 0, Team: 1, Average: 2-3, then pairs of (score, points) for each opponent
            num_teams = len(sorted_teams)
            score_column_indices = []
            points_column_indices = []
            
            # Average columns are first (right after position and team)
            avg_score_col_idx = 2
            avg_points_col_idx = 3
            
            # Team columns come after averages
            col_idx = 4  # Start after position (0), team name (1), and averages (2-3)
            for _ in range(num_teams):
                score_column_indices.append(col_idx)
                points_column_indices.append(col_idx + 1)
                col_idx += 2
            
            # Generate rows (using sorted teams)
            for row_idx, team in enumerate(sorted_teams):
                position = team_positions[team]
                row = [position, team]
                
                team_scores = []
                team_points = []
                
                # Collect all team vs opponent data first
                for opponent in sorted_teams:
                    if team != opponent:
                        if opponent in comparison_data[team]:
                            score = comparison_data[team][opponent]['avg_score']
                            points = comparison_data[team][opponent]['avg_points']
                        else:
                            score = 0.0
                            points = 0.0
                        team_scores.append(score)
                        team_points.append(points)
                
                # Calculate and add team averages first (columns 2-3)
                avg_score = round(sum(team_scores) / len(team_scores), 1) if team_scores else 0
                avg_points = round(sum(team_points) / len(team_points), 1) if team_points else 0
                row.extend([avg_score, avg_points])
                
                # Add team columns (starting at column 4)
                col_idx = 4
                for opponent in sorted_teams:
                    if team != opponent:
                        if opponent in comparison_data[team]:
                            score = comparison_data[team][opponent]['avg_score']
                            points = comparison_data[team][opponent]['avg_points']
                        else:
                            score = 0.0
                            points = 0.0
                        
                        row.extend([score, points])
                        col_idx += 2
                    else:
                        # Diagonal cells - empty cells
                        row.extend(["", ""])
                        cell_metadata[f"{row_idx}:{col_idx}"] = {"backgroundColor": get_theme_color("background")}
                        cell_metadata[f"{row_idx}:{col_idx + 1}"] = {"backgroundColor": get_theme_color("background")}
                        col_idx += 2
                
                table_data.append(row)
            
            # Heatmap coloring is now handled in the frontend
            # ========== RETURN TABLE DATA ==========
            return TableData(
                columns=columns,
                data=table_data,
                title=i18n_service.get_text("team_vs_team_comparison_matrix"),
                description=f"{i18n_service.get_text('team_vs_team_comparison_matrix_explanation')}{f' {i18n_service.get_text('week')} {week}.' if week else f' {i18n_service.get_text('article_male')} {i18n_service.get_text('season')}.'}",
                config={
                    "striped": True,
                    "hover": True,
                    "compact": True,
                    "stickyHeader": True
                },
                metadata={
                    "score_range": {"min": score_min, "max": score_max},
                    "points_range": {"min": points_min, "max": points_max},
                    "week": week
                }
            )
            
        except Exception as e:
            print(f"Error in get_team_vs_team_comparison_table: {str(e)}")
            return TableData(
                columns=[],
                data=[],
                title=i18n_service.get_text("team_vs_team_comparison_matrix"),
                description=f"Error: {str(e)}",
                config={"striped": True, "hover": True, "compact": True, "stickyHeader": True}
            )

    def get_season_league_standings(self, season: str) -> Dict[str, Any]:
        """
        Get latest week standings for all leagues in a season.
        
        Args:
            season: The season identifier
            
        Returns:
            Dictionary with leagues and their latest week standings
        """
        try:
            # Get all leagues that have data for this season
            league_filters = {
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}
            }
            
            # Get all leagues for this season
            leagues_data = self.adapter.get_filtered_data(
                columns=[Columns.league_name], 
                filters=league_filters
            )
            
            if leagues_data.empty:
                return {"leagues": []}
            
            leagues = sorted(leagues_data[Columns.league_name].unique())
            
            # Get standings for each league's latest week
            league_standings = []
            
            for league in leagues:
                try:
                    # Get the latest week for this league/season
                    latest_week = self.get_latest_week(season, league)
                    
                    if latest_week:
                        # Get the standings for the latest week
                        standings = self.get_league_week_table_simple(
                            season=season, 
                            league=league, 
                            week=latest_week
                        )
                        
                        # Get honor scores for the latest week
                        honor_scores = self.get_honor_scores(league, season, latest_week)
                        
                        if standings:
                            league_standings.append({
                                'league': league,
                                'week': latest_week,
                                'standings': standings.to_dict(),
                                'honor_scores': honor_scores
                            })
                            
                except Exception as e:
                    print(f"Error getting standings for league {league}: {e}")
                    continue
            
            return {
                'leagues': league_standings,
                'season': season
            }
            
        except Exception as e:
            print(f"Error in get_season_league_standings: {e}")
            return {"leagues": []}

    def get_record_games(self, league: str) -> TableData:
        """Legacy method - returns individual records for backward compatibility"""
        return self.get_record_individual_games(league)

    def get_individual_matches(self, team: str, season: str, league: str) -> pd.DataFrame:
        """Get individual player matches with opponent scores for PvP win calculation"""
        try:
            # Get ALL individual player data for the league/season (not just our team)
            # We need this to find opponent matches
            all_player_filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}  # Individual players only
            }
            
            all_player_data = self.adapter.get_filtered_data(filters=all_player_filters)
            
            if all_player_data.empty:
                return pd.DataFrame()
            
            # Filter to just our team's players
            our_team_data = all_player_data[all_player_data[Columns.team_name] == team]
            
            if our_team_data.empty:
                return pd.DataFrame()
            
            # For each player match, we need to find the opponent's score
            result_data = []
            
            for _, player_match in our_team_data.iterrows():
                week = player_match[Columns.week]
                round_num = player_match[Columns.round_number]
                opponent_team = player_match[Columns.team_name_opponent]
                player_name = player_match[Columns.player_name]
                player_score = player_match[Columns.score]
                
                # Find the opponent's score for the same match
                # Look in ALL player data for opponent team players in same week/round
                opponent_match = all_player_data[
                    (all_player_data[Columns.week] == week) &
                    (all_player_data[Columns.round_number] == round_num) &
                    (all_player_data[Columns.team_name] == opponent_team) &  # Their team is the opponent
                    (all_player_data[Columns.team_name_opponent] == team)  # They're playing against us
                ]
                
                if not opponent_match.empty:
                    # Find the opponent player with the same position or similar role
                    # For simplicity, we'll take the first opponent player
                    opponent_score = opponent_match[Columns.score].iloc[0]
                    
                    result_data.append({
                        'week': week,
                        'round_number': round_num,
                        'player_name': player_name,
                        'player_score': player_score,
                        'opponent_team': opponent_team,
                        'opponent_score': opponent_score,
                        'is_win': player_score > opponent_score
                    })
            
            return pd.DataFrame(result_data)
            
        except Exception as e:
            return pd.DataFrame()