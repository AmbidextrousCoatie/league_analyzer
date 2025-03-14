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
            team_data['total_score'] += score / 2.0
            team_data['total_points'] += points
            
            # Store weekly performance
            if week not in team_data['weekly_performances']:
                team_data['weekly_performances'][week] = {
                    'score': 0,
                    'points': 0
                }
            
            week_data = team_data['weekly_performances'][week]
            week_data['score'] += score / 2.0
            week_data['points'] += points
        
        # Convert to TeamSeasonPerformance objects
        result = []
        for team_id, data in team_performances.items():
            # Calculate average (assuming 4 games per week)
            weekly_count = len(data['weekly_performances'])
           
            games_played = weekly_count * 4  # Adjust based on your league structure
            average = data['total_score'] / games_played / 5.0 if games_played > 0 else 0
            
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
        
        # Add season total column with special styling
        columns.append(
            ColumnGroup(
                title="Season Total",
                style={"backgroundColor": "#e9ecef"},  # Slightly darker background
                header_style={"fontWeight": "bold"},  # Bold header
                columns=[
                    Column(
                        title="Pins", 
                        field="season_total_score", 
                        format="{:,}",
                        style={"fontWeight": "bold"}
                    ),
                    Column(
                        title="Pts.", 
                        field="season_total_points", 
                        format="{:.1f}",
                        style={"fontWeight": "bold"}
                    ),
                    Column(
                        title="Avg.", 
                        field="season_total_average", 
                        format="{:.1f}",
                        style={"fontWeight": "bold"}
                    )
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
                    row.extend([perf.score, perf.points, round(weekly_avg, 1)])
                else:
                    row.extend([0, 0, 0])  # No data for this week
            
            # Add season totals
            row.extend([
                team.total_score,
                team.total_points,
                team.average
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
            return {"message": "No data found"}
        
        # Process the data into a suitable format
        # This is a placeholder - adjust based on your specific requirements
        result = {
            "team": team,
            "league": league,
            "season": season,
            "week": week,
            "games": []
        }
        
        # Add game details
        for _, row in team_data.iterrows():
            game = {
                "lane": row.get("Lane", ""),
                "score": row.get("Score", 0),
                "points": row.get("Points", 0)
            }
            result["games"].append(game)
        
        return result

    def get_team_points_during_season(self, league_name: str, season: str) -> Dict[str, Any]:
        """Get team points throughout a season"""
        # Get all teams and their performances
        standings = self.get_league_standings(season, league_name)
        
        if not standings.teams:
            return {"weekly": {}, "total": {}}
        
        # Get all weeks in the season
        all_weeks = sorted(set(
            perf.week for team in standings.teams 
            for perf in team.weekly_performances
        ))
        
        # Prepare result structure
        weekly_points = {}
        total_points = {}
        
        for team in standings.teams:
            # Create a map of week to points for this team
            week_to_points = {p.week: p.points for p in team.weekly_performances}
            
            # Add points for each week (or 0 if no data)
            weekly_points[team.team_name] = [week_to_points.get(week, 0) for week in all_weeks]
            
            # Add total points
            total_points[team.team_name] = team.total_points
        
        return {
            "weekly": weekly_points,
            "total": total_points
        }

    def get_team_averages_during_season(self, league_name: str, season: str) -> Dict[str, Any]:
        """Get team averages throughout a season"""
        # Get all teams and their performances
        standings = self.get_league_standings(season, league_name)
        
        if not standings.teams:
            return {"averages": {}, "total": {}}
        
        # Get all weeks in the season
        all_weeks = sorted(set(
            perf.week for team in standings.teams 
            for perf in team.weekly_performances
        ))
        
        # Prepare result structure
        weekly_averages = {}
        total_averages = {}
        
        for team in standings.teams:
            # Create a map of week to score for this team
            week_to_perf = {p.week: p for p in team.weekly_performances}
            
            # Calculate average for each week (assuming 4 games per week)
            averages = []
            for week in all_weeks:
                perf = week_to_perf.get(week)
                if perf:
                    # Assuming 4 games per week
                    avg = perf.score / 4 if perf.score > 0 else 0
                    averages.append(round(avg, 2))
                else:
                    averages.append(0)
            
            weekly_averages[team.team_name] = averages
            
            # Add total average
            total_averages[team.team_name] = team.average
        
        return {
            "averages": weekly_averages,
            "total": total_averages
        }

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
                        individual_scores: int = 3, team_scores: int = 3,
                        indivdual_averages: int = 3, team_averages: int = 3) -> Dict[str, Any]:
        """Get honor scores for a specific week"""
        # Create a query for this league, season, and week
        query = LeagueQuery(season=season, league=league, week=week)
        
        # Get the data
        league_data = self.adapter.get_filtered_data(query.to_filter_dict())
        
        if league_data.empty:
            return {
                "individual_scores": [],
                "team_scores": [],
                "individual_averages": [],
                "team_averages": []
            }
        
        # Process individual scores
        individual_scores_list = []
        if "Player" in league_data.columns and "Score" in league_data.columns:
            player_scores = league_data.groupby("Player")["Score"].max().reset_index()
            player_scores = player_scores.sort_values("Score", ascending=False).head(individual_scores)
            
            for _, row in player_scores.iterrows():
                individual_scores_list.append({
                    "player": row["Player"],
                    "score": row["Score"]
                })
        
        # Process team scores
        team_scores_list = []
        if "Team" in league_data.columns and "Score" in league_data.columns:
            team_scores = league_data.groupby("Team")["Score"].sum().reset_index()
            team_scores = team_scores.sort_values("Score", ascending=False).head(team_scores)
            
            for _, row in team_scores.iterrows():
                team_scores_list.append({
                    "team": row["Team"],
                    "score": row["Score"]
                })
        
        # Process individual averages
        individual_averages_list = []
        if "Player" in league_data.columns and "Score" in league_data.columns:
            player_averages = league_data.groupby("Player")["Score"].mean().reset_index()
            player_averages = player_averages.sort_values("Score", ascending=False).head(indivdual_averages)
            
            for _, row in player_averages.iterrows():
                individual_averages_list.append({
                    "player": row["Player"],
                    "average": round(row["Score"], 2)
                })
        
        # Process team averages
        team_averages_list = []
        if "Team" in league_data.columns and "Score" in league_data.columns:
            team_averages = league_data.groupby("Team")["Score"].mean().reset_index()
            team_averages = team_averages.sort_values("Score", ascending=False).head(team_averages)
            
            for _, row in team_averages.iterrows():
                team_averages_list.append({
                    "team": row["Team"],
                    "average": round(row["Score"], 2)
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
        # Get the raw history data
        history_data = self.get_league_history_table(league_name, season, week)
        
        if "message" in history_data:
            # Return empty table if no data
            return TableData(
                columns=[],
                data=[],
                title=f"No data available for {league_name} - {season}"
            )
        
        # Get all weeks from the data
        all_weeks = set()
        for team in history_data["teams"]:
            for perf in team["weekly_performances"]:
                all_weeks.add(perf["week"])
        all_weeks = sorted(all_weeks)
        
        # Create column groups
        columns = [
            ColumnGroup(
                title="Ranking",
                frozen="left",
                style={"backgroundColor": "#f8f9fa"},
                columns=[
                    Column(title="#", field="pos", width="50px", align="center"),
                    Column(title="Team", field="team", width="200px", align="left")
                ]
            )
        ]
        
        # Add a column group for each week
        for week in all_weeks:
            columns.append(
                ColumnGroup(
                    title=f"Week {week}",
                    columns=[
                        Column(title="Pins", field=f"week{week}_score", format="{:,}"),
                        Column(title="Pts.", field=f"week{week}_points", format="{:.1f}"),
                        Column(title="Avg.", field=f"week{week}_avg", format="{:.1f}")
                    ]
                )
            )
        
        # Add season total column
        columns.append(
            ColumnGroup(
                title="Season Total",
                style={"backgroundColor": "#e9ecef"},
                header_style={"fontWeight": "bold"},
                columns=[
                    Column(
                        title="Pins", 
                        field="total_score", 
                        format="{:,}",
                        style={"fontWeight": "bold"}
                    ),
                    Column(
                        title="Pts.", 
                        field="total_points", 
                        format="{:.1f}",
                        style={"fontWeight": "bold"}
                    ),
                    Column(
                        title="Avg.", 
                        field="average", 
                        format="{:.1f}",
                        style={"fontWeight": "bold", "color": "#007bff"}
                    )
                ]
            )
        )
        
        # Prepare the data rows
        data = []
        for team in history_data["teams"]:
            # Create a map of week to performance for easy lookup
            week_to_perf = {p["week"]: p for p in team["weekly_performances"]}
            
            # Start with position and team name
            row = [team["position"], team["name"]]
            
            # Add weekly data
            for week in all_weeks:
                perf = week_to_perf.get(week)
                if perf:
                    # Get players_per_team from the performance or use default
                    players_per_team = perf.get("players_per_team", 4)
                    # Calculate average using players_per_team
                    weekly_avg = perf["score"] / players_per_team / 2.0
                    row.extend([perf["score"], perf["points"], round(weekly_avg, 1)])
                else:
                    row.extend([0, 0, 0])  # No data for this week
            
            # Add season totals
            row.extend([
                team["total_score"],
                team["total_points"],
                team["average"]
            ])
            
            data.append(row)
        
        # Sort by position
        data.sort(key=lambda x: x[0])  # Sort by position (first column)
        
        # Create and return the TableData
        return TableData(
            columns=columns,
            data=data,
            title=f"{league_name} History - {season}",
            description=f"Through Week {max(all_weeks) if all_weeks else 0}",
            config={
                "stickyHeader": True,
                "striped": True,
                "hover": True,
                "responsive": True
            }
        )