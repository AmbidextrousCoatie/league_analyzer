from typing import List, Dict, Any, Optional
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
# from data_access.series_data import calculate_series_data, get_player_series_data, get_team_series_data


class LeagueService:
    def __init__(self, adapter_type=DataAdapterSelector.PANDAS):
        self.adapter = DataAdapterFactory.create_adapter(adapter_type)
        self.stats_service = StatisticsService()
        
        # Register this adapter with DataManager for automatic refresh
        try:
            from app.services.data_manager import DataManager
            data_manager = DataManager()
            data_manager.register_server_instance(self)
        except ImportError:
            # DataManager not available, continue without registration
            pass

    def refresh_data_adapter(self):
        """Refresh the data adapter with the current data source"""
        print(f"DEBUG: LeagueService refreshing data adapter")
        self.adapter = DataAdapterFactory.create_adapter(DataAdapterSelector.PANDAS)
        print(f"DEBUG: LeagueService data adapter refreshed")

    def get_available_weeks(self, season: str, league: str) -> List[int]:
        """Get available weeks for a season and league"""
        return self.adapter.get_weeks(season, league)
    
    def get_latest_week(self, season: str, league: str) -> int:
        """Get the latest week number for a season and league"""
        weeks = self.get_available_weeks(season, league)
        return max(weeks) if weeks else 1
    
    def get_seasons(self) -> List[str]:
        """Get all available seasons"""
        return self.adapter.get_seasons()

    def get_leagues(self) -> List[str]:
        """Get all available leagues for a season"""
        return self.adapter.get_leagues()

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

    def get_league_results(self, league: str, season: str) -> LeagueResults:
        """Get league results using the new data structure"""
        stats = self.stats_service.get_league_statistics(league, season)
        if not stats:
            return None
            
        # Calculate ranking based on total points
        ranking = sorted(
            stats.team_stats.keys(),
            key=lambda x: stats.team_stats[x].season_summary.total_points,
            reverse=True
        )
        
        return LeagueResults(
            name=league,
            level=self._get_league_level(league),
            weeks=stats.weekly_summaries,
            ranking=ranking,
            data=stats.season_summary
        )

    def _get_league_level(self, league: str) -> int:
        """Get the level of a league"""
        # This is a placeholder implementation
        # You should implement the actual logic based on your requirements
        return 1

    def get_league_week_table(self, season: str, league: str, week: Optional[int] = None, depth: int = 1) -> TableData:
        """
        Get a formatted table for league standings with weekly breakdowns.
        
        Args:
            season: The season identifier
            league: The league name
            week: The current week (if None, gets the latest)
            depth: How many previous weeks to include
            
        Returns:
            TableData object with the league standings
        """
        # If week is not specified, get the latest week
        if week is None:
            week = self.get_latest_week(season, league)
        
        # Get team performances from the adapter
        team_performances = self.adapter.get_league_standings(season, league, week)
        
        if not team_performances:
            # Return empty table structure
            return TableData(
                columns=[],
                data=[],
                title=f"No data available for {league} - {season}"
            )
        
        # Sort by total points (descending) and assign positions
        team_performances.sort(key=lambda x: (x.total_points, x.total_score), reverse=True)
        for i, perf in enumerate(team_performances, 1):
            perf.position = i
        
        # Create column groups
        columns = [
            ColumnGroup(
                title="Ranking",
                frozen="left",  # Freeze this group to the left
                style={"backgroundColor": "#f8f9fa"},  # Light gray background
                columns=[
                    Column(title="#", field="pos", width="50px", align="center"),
                    Column(title="Team", field="team", width="200px", align="left")
                ]
            )
        ]
        
        # Add columns for each week
        start_week = max(1, week - depth + 1)
        for w in range(start_week, week + 1):
            columns.append(
                ColumnGroup(
                    title=f"Week {w}",
                    columns=[
                        Column(title="Pins", field=f"week{w}_score", format="{:,}"),
                        Column(title="Pts.", field=f"week{w}_points", format="{:.1f}"),
                        Column(title="Avg.", field=f"week{w}_avg", format="{:.1f}")
                    ]
                )
            )
        
        # Add totals column group
        columns.append(
            ColumnGroup(
                title="Total",
                style={"backgroundColor": "#e9ecef"},
                header_style={"fontWeight": "bold"},
                columns=[
                    Column(title="Points", field="total_points", width="80px", align="center"),
                    Column(title="Score", field="total_score", width="80px", align="center"),
                    Column(title="Avg", field="average", width="80px", align="center")
                ]
            )
        )
        
        # Prepare the data rows
        data = []
        for team in team_performances:
            # Create a map of week to performance for easy lookup
            week_to_perf = {p.week: p for p in team.weekly_performances}
            
            # Start with position and team name
            row = [team.position, team.team_name]
            
            # Add weekly data
            for w in range(start_week, week + 1):
                perf = week_to_perf.get(w)
                if perf:
                    # Calculate average using players_per_team
                    weekly_avg = perf.score / perf.players_per_team
                    row.extend([perf.score / 2.0, perf.points, round(weekly_avg / 10.0, 1)])
                else:
                    row.extend([0, 0, 0])  # No data for this week
            
            # @todo: this is a hack to normalize the score, the factor 2.0 amd 10.0 is arbitrary, fix it in the structure
            # Add season totals
            row.extend([
                team.total_score / 2.0,
                team.total_points,
                team.average / 10.0
            ])
            
            data.append(row)
        
        # Create and return the TableData with configuration
        return TableData(
            columns=columns,
            data=data,
            title=f"{league} Standings - {season}",
            description=f"Through Week {week}",
            config={
                "stickyHeader": True,  # Make header sticky
                "striped": True,       # Use striped rows
                "hover": True,         # Enable hover effect
                "responsive": True,    # Make table responsive
                "compact": False       # Use normal spacing
            }
        )
    
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
                title=f"No data available for {league} - {season}",
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
            title=f"{league} Team Performance - {season}",
            series=series,
            x_axis=weeks,
            y_axis_label="Cumulative Points",
            x_axis_label="Week",
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
                    title="No Data",
                    value="No league data available",
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
                    title="League Leader",
                    value=leader.team_name,
                    subtitle=f"{leader.total_points} points",
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
                    title="League Average",
                    value=f"{league_avg:.1f}",
                    subtitle="Pins per game",
                    type="stat"
                )
            )
        
        # Weeks completed tile
        if standings.teams and standings.teams[0].weekly_performances:
            completed_weeks = len(set(p.week for p in standings.teams[0].weekly_performances))
            tiles.append(
                TileData(
                    title="Weeks Completed",
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
        # Get all events from the adapter
        events_df = self.adapter.get_filtered_data(
            filters={},
            sort_by="Date",
            ascending=False,
            limit=limit
        )
        
        # If no events, return empty list
        if events_df.empty:
            return []
        
        # Convert to list of dictionaries
        events = []
        for _, row in events_df.iterrows():
            event = {}
            for col in ["Season", "League", "Week", "Date"]:
                if col in row:
                    event[col] = row[col]
            events.append(event)
        
        return events

    def get_weeks(self, league_name: str = None, season: str = None) -> List[int]:
        """Get available weeks for a league and season"""
        #if not league_name or not season:
            # Return empty list if parameters are missing
        #    return []
        return self.adapter.get_weeks(season, league_name)

    def get_valid_combinations(self) -> Dict[str, Dict[str, List[str]]]:
        """Get valid combinations of season, league, and weeks"""
        # This is a placeholder implementation - adjust based on your data structure
        result = {}
        seasons = self.get_seasons()
        
        for season in seasons:
            result[season] = {}
            leagues = self.get_leagues()
            
            for league in leagues:
                weeks = self.get_weeks(league_name=league, season=season)
                if weeks:
                    result[season][league] = weeks
        
        return result

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

    def get_team_week_details(self, league: str, season: str, team: str, week: int) -> Dict[str, Any]:
        """Get details for a specific team in a specific week"""
        # Create a query for this specific team, league, season, and week
        query = LeagueQuery(season=season, league=league, team=team, week=week)
        
        # Get the data
        team_data = self.adapter.get_filtered_data(query.to_filter_dict())
        
        if team_data.empty:
            return {"config": []}
        
        # Process the data into the expected format for the frontend
        config = []
        
        # Add player details
        for _, row in team_data.iterrows():
            if "Player" in team_data.columns and "Score" in team_data.columns and "Opponent" in team_data.columns:
                player_detail = {
                    "player": row.get("Player", ""),
                    "score": row.get("Score", 0),
                    "opponent": row.get("Opponent", "")
                }
                config.append(player_detail)
        
        return {"config": config}

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
                    title=f"No data available for {team} - Week {week}"
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
                    title="Player",
                    frozen="left",
                    style={"backgroundColor": "#f8f9fa"},
                    columns=[
                        Column(title="Pos", field="position", width="50px", align="center"),
                        Column(title="Name", field="name", width="200px", align="left")
                    ]
                )
            ]
            
            # Add game column groups with opponent team names
            for game in games:
                opponent_name = game_to_opponent.get(game, f"Game {game}")
                columns.append(
                    ColumnGroup(
                        title=opponent_name,
                        columns=[
                            Column(title="Score", field=f"game{game}_score", width="80px", align="center"),
                            Column(title="Pts", field=f"game{game}_points", width="60px", align="center")
                        ]
                    )
                )
            
            # Add totals column group
            columns.append(
                ColumnGroup(
                    title="Total",
                    style={"backgroundColor": "#e9ecef"},
                    header_style={"fontWeight": "bold"},
                    columns=[
                        Column(title="Points", field="total_points", width="80px", align="center"),
                        Column(title="Score", field="total_score", width="80px", align="center"),
                        Column(title="Avg", field="average", width="80px", align="center")
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
                title=f"{team} - Match Day {week}",
                description=f"Score sheet for {team} in {league} - {season}",
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
                title=f"Error loading data for {team} - Week {week}"
            )

    def get_team_points_during_season(self, league_name: str, season: str) -> Dict[str, Any]:
        """Get team points throughout a season"""
        # Get all teams and their performances
        standings = self.get_league_standings(season, league_name)
        
        if not standings.teams:
            return SeriesData(
                label_x_axis="Spieltag", 
                label_y_axis="Punkte", 
                name="Punkte im Saisonverlauf", 
                query_params={"season": season, "league": league_name}
            ).to_dict()
        
        series_data = SeriesData(label_x_axis="Spieltag", label_y_axis="Punkte", name="Punkte im Saisonverlauf", 
                                 query_params={"season": season, "league": league_name})
        
        for team in standings.teams:
            week_performances = [p.points for p in team.weekly_performances]
            series_data.add_data(team.team_name, week_performances)

        return series_data.to_dict()

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

    def get_league_history_table(self, league_name: str, season: str, week: Optional[int] = None, 
                               depth: Optional[int] = None, debug_output: bool = False) -> Dict[str, Any]:
        """Get league history table data"""
        # This is a placeholder implementation - adjust based on your specific requirements
        # Get team performances
        standings = self.get_league_standings(season, league_name, week)
        
        if not standings.teams:
            return {"message": "No data found"}
        
        # Process data into the expected format
        result = {
            "title": f"{league_name} - {season} History",
            "teams": []
        }
        # @todo: this is a hack to normalize the score, the factor 2.5 is arbitrary, fix it in the structure
        for team in standings.teams:
            team_data = {
                "name": team.team_name,
                "total_points": team.total_points,
                "total_score": team.total_score,
                "average": team.average,
                "position": team.position,
                "weekly_performances": []
            }
            
            for perf in team.weekly_performances:
                team_data["weekly_performances"].append({
                    "week": perf.week,
                    "score": perf.score,
                    "points": perf.points,
                    "players_per_team": perf.players_per_team
                })
            
            result["teams"].append(team_data)
        
        if debug_output:
            print(f"League history table: {result}")
        
        return result

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
            
            # Use individual data for the main league data (scores and averages)
            league_data = individual_data
            
            if league_data.empty:
                return TableData(
                    columns=[],
                    data=[],
                    title=f"No data available for {league} - {season}"
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
                
                # Get individual player data for this team (for scores and averages)
                team_individual_data = individual_data[individual_data[Columns.team_name] == team]
                
                # Get team bonus data for this team (for team points only)
                team_bonus_team_data = team_bonus_data[team_bonus_data[Columns.team_name] == team]
                
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
                            'score': week_score,
                            'points': week_points,
                            'avg': round(week_avg, 1)
                        }
                    else:
                        team_data[team]['weekly_data'][w] = {
                            'score': 0,
                            'points': 0,
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
                    style={"backgroundColor": "#f8f9fa"},
                    columns=[
                        Column(title="#", field="pos", width="50px", align="center"),
                        Column(title=i18n_service.get_text("team"), field="team", width="200px", align="left")
                    ]
                )
            ]
            
            # Add weekly column groups
            for w in weeks_to_show:
                columns.append(
                    ColumnGroup(
                        title=f"{i18n_service.get_text('week')} {w}",
                        columns=[
                            Column(title=i18n_service.get_text("score"), field=f"week{w}_score", format="{:,}"),
                            Column(title=i18n_service.get_text("points"), field=f"week{w}_points", format="{:.1f}"),
                            Column(title=i18n_service.get_text("average"), field=f"week{w}_avg", format="{:.1f}")
                        ]
                    )
                )
            
            # Add totals column group
            columns.append(
                ColumnGroup(
                    title="Total",
                    style={"backgroundColor": "#e9ecef"},
                    header_style={"fontWeight": "bold"},
                    columns=[
                        Column(title="Points", field="season_points", format="{:,}"),
                        Column(title="Score", field="season_score", format="{:,}"),
                        Column(title="Avg", field="season_avg", format="{:.1f}")
                    ]
                )
            )
            
            # Prepare the data rows
            data = []
            for i, team in enumerate(sorted_teams, 1):
                team_info = team_data[team]
                
                # Start with position and team name
                row = [i, team]
                
                # Add weekly data
                for w in weeks_to_show:
                    week_info = team_info['weekly_data'][w]
                    row.extend([
                        week_info['score'],
                        week_info['points'],
                        week_info['avg']
                    ])
                
                # Add season totals
                row.extend([
                    team_info['season_score'],
                    team_info['season_points'],
                    team_info['season_avg']
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
                    "compact": False
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
                    title=f"No data available for {team} - Week {week}"
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
                    title="Match Info",
                    style={"backgroundColor": "#f8f9fa"},
                    columns=[
                        Column(title="Round", field="round_number", width="60px", align="center"),
                        Column(title="Opponent", field="opponent_name", width="120px", align="left"),
                    ]
                )
            ]

            # Helper to build player col group
            def player_col_group(player, prefix):
                return ColumnGroup(
                    title=player,
                        columns=[
                        Column(title="Pos", field=f"{prefix}{player}_pos", width="50px", align="center"),
                        Column(title="Score", field=f"{prefix}{player}_score", width="80px", align="center"),
                        Column(title="Pts", field=f"{prefix}{player}_points", width="60px", align="center"),
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
                    title="Team",
                    style={"backgroundColor": "#e9ecef"},
                    header_style={"fontWeight": "bold"},
                    columns=[
                        Column(title="Score", field="team_score", width="80px", align="center"),
                        Column(title="Points", field="team_points", width="80px", align="center")
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
                title=f"Error loading data for {team} - Week {week}"
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
                title="Match",
                columns=[
                    Column(title="Opponent", field="opponent", width="120px", align="left", sortable=False),
                    Column(title="Total Points", field="team_total_points", width="100px", align="center", sortable=False,
                           style={"fontWeight": "bold"}),
                ]
                #style={"borderRight": "2px solid #264653"}  # Vertical bar after Opponents group (same color as other borders)
            ),
            ColumnGroup(
                title=team,
                columns=[
                    Column(title="Score", field="team_score", width="80px", align="center", sortable=False),
                    Column(title="Pts.", field="team_points", width="80px", align="center", sortable=False),
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
                        Column(title="Score", field=f"{player_info['identifier']}_score", width="80px", align="center", sortable=False),
                        Column(title="Pts.", field=f"{player_info['identifier']}_points", width="50px", align="center", sortable=False),
                        Column(title="Pos", field=f"{player_info['identifier']}_pos", width="50px", align="center", sortable=False),
                        
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