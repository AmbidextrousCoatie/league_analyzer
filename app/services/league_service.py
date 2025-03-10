from typing import List, Dict, Any, Optional
import datetime
from data_access.adapters.data_adapter_factory import DataAdapterFactory, DataAdapterSelector
from data_access.models.league_models import LeagueQuery, TeamSeasonPerformance, LeagueStandings, TeamWeeklyPerformance
from app.models.table_data import TableData, ColumnGroup, Column, PlotData, TileData

class LeagueService:
    def __init__(self, adapter_type=DataAdapterSelector.PANDAS):
        self.adapter = DataAdapterFactory.create_adapter(adapter_type)
    
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
        
        # Create query for all weeks up to the specified week
        query = LeagueQuery(
            season=season,
            league=league,
            max_week=week
        )
        
        # Get team performances from the adapter
        # This assumes your adapter has a method to get team season performances
        # If not, you'll need to process the raw data here
        team_performances = self._get_team_season_performances(query)
        
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
    
    def _get_team_season_performances(self, query: LeagueQuery) -> List[TeamSeasonPerformance]:
        """
        Get team performances for a season.
        This method processes raw data from the adapter into TeamSeasonPerformance objects.
        """
        # Get raw data from adapter
        league_data = self.adapter.get_filtered_data(query.to_filter_dict())
        
        if league_data.empty:
            return []
        
        # Process data to get team performances
        # This implementation will depend on your specific data structure
        # Here's a simplified example assuming your DataFrame has certain columns
        
        # Group by team
        team_performances = {}
        
        # Process each row in the DataFrame
        for _, row in league_data.iterrows():
            team_id = row.get('TeamID', str(row.get('Team', '')))
            team_name = row.get('TeamName', row.get('Team', ''))
            week = row.get('Week', 0)
            score = row.get('Score', 0)
            points = row.get('Points', 0)
            
            # Initialize team data if not exists
            if team_id not in team_performances:
                team_performances[team_id] = {
                    'team_id': team_id,
                    'team_name': team_name,
                    'total_score': 0,
                    'total_points': 0,
                    'weekly_performances': {}
                }
            
            # Update team totals
            team_data = team_performances[team_id]
            team_data['total_score'] += score
            team_data['total_points'] += points
            
            # Store weekly performance
            if week not in team_data['weekly_performances']:
                team_data['weekly_performances'][week] = {
                    'score': 0,
                    'points': 0
                }
            
            week_data = team_data['weekly_performances'][week]
            week_data['score'] += score
            week_data['points'] += points
        
        # Convert to TeamSeasonPerformance objects
        result = []
        for team_id, data in team_performances.items():
            # Calculate average (assuming 4 games per week)
            weekly_count = len(data['weekly_performances'])
            games_played = weekly_count * 4  # Adjust based on your league structure
            average = data['total_score'] / games_played if games_played > 0 else 0
            
            # Create weekly performance objects
            weekly_performances = []
            for week, week_data in data['weekly_performances'].items():
                weekly_performances.append(
                    TeamWeeklyPerformance(
                        team_id=data['team_id'],
                        team_name=data['team_name'],
                        week=week,
                        score=week_data['score'],
                        points=week_data['points']
                    )
                )
            
            # Sort weekly performances by week
            weekly_performances.sort(key=lambda x: x.week)
            
            # Create the TeamSeasonPerformance
            result.append(
                TeamSeasonPerformance(
                    team_id=data['team_id'],
                    team_name=data['team_name'],
                    total_score=data['total_score'],
                    total_points=data['total_points'],
                    average=round(average, 2),
                    weekly_performances=weekly_performances
                )
            )
        
        return result
    
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
                frozen="left",
                columns=[
                    Column(title="#", field="pos"),
                    Column(title="Team", field="team")
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
                        Column(title="Pins", field=f"week{w}_score"),
                        Column(title="Pts.", field=f"week{w}_points")
                    ]
                )
            )
        
        # Add season total column
        columns.append(
            ColumnGroup(
                title="Season Total",
                columns=[
                    Column(title="Pins", field="season_total_score"),
                    Column(title="Pts.", field="season_total_points"),
                    Column(title="Avg.", field="season_total_average")
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
                    row.extend([perf.score, perf.points])
                else:
                    row.extend([0, 0])  # No data for this week
            
            # Add season totals
            row.extend([
                team.total_score,
                team.total_points,
                team.average
            ])
            
            data.append(row)
        
        # Create and return the TableData
        return TableData(
            columns=columns,
            data=data,
            title=f"{league} Standings - {season}",
            description=f"Through Week {week}"
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