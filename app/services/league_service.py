from typing import List, Dict, Any, Optional
import datetime


from data_access.adapters.data_adapter_factory import DataAdapterFactory, DataAdapterSelector
from data_access.models.league_models import LeagueQuery, TeamSeasonPerformance, LeagueStandings, TeamWeeklyPerformance
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
            filters = {
                Columns.league_name: {'value': league, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'},
                Columns.computed_data: {'value': False, 'operator': 'eq'}
            }
            
            league_data = self.adapter.get_filtered_data(filters=filters)
            
            if league_data.empty:
                return TableData(
                    columns=[],
                    data=[],
                    title=f"No data available for {league} - {season}"
                )
            
            # Get all teams and weeks
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
                    'season_points': 0
                }
                
                # Get team data
                team_season_data = league_data[league_data[Columns.team_name] == team]
                
                # Calculate season totals
                if not team_season_data.empty:
                    team_data[team]['season_score'] = int(team_season_data[Columns.score].sum())
                    team_data[team]['season_points'] = float(team_season_data[Columns.points].sum())
                
                # Calculate weekly data
                for w in weeks_to_show:
                    team_week_data = team_season_data[team_season_data[Columns.week] == w]
                    
                    if not team_week_data.empty:
                        week_score = int(team_week_data[Columns.score].sum())
                        week_points = float(team_week_data[Columns.points].sum())
                        week_avg = week_score / len(team_week_data) if len(team_week_data) > 0 else 0
                        
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
            
            # Sort teams by week points (descending), then by week score (descending)
            # For history mode, sort by the selected week's performance
            if include_history:
                sort_week = week
            else:
                sort_week = week
            
            sorted_teams = sorted(
                teams,
                key=lambda t: (
                    team_data[t]['weekly_data'].get(sort_week, {}).get('points', 0),
                    team_data[t]['weekly_data'].get(sort_week, {}).get('score', 0)
                ),
                reverse=True
            )
            
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
            
            # Add weekly column groups
            for w in weeks_to_show:
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
            
            # Add season total column
            columns.append(
                ColumnGroup(
                    title="Season Total",
                    style={"backgroundColor": "#e9ecef"},
                    header_style={"fontWeight": "bold"},
                    columns=[
                        Column(title="Pins", field="season_score", format="{:,}"),
                        Column(title="Pts.", field="season_points", format="{:.1f}"),
                        Column(title="Avg.", field="season_avg", format="{:.1f}")
                    ]
                )
            )
            
            # Prepare the data rows
            data = []
            for i, team in enumerate(sorted_teams, 1):
                team_info = team_data[team]
                
                # Calculate season average
                team_season_data = league_data[league_data[Columns.team_name] == team]
                season_avg = team_info['season_score'] / len(team_season_data) if len(team_season_data) > 0 else 0
                
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
                    round(season_avg, 1)
                ])
                
                data.append(row)
            
            # Create and return the TableData
            title = f"{league} History - {season}" if include_history else f"{league} Standings - {season}"
            description = f"Through Week {week}" if include_history else f"Week {week} Results & Season Totals"
            
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
        # Get all data for this league and season (both individual and team points)
        filters = {
            'League': {'value': league_name, 'operator': 'eq'},
            'Season': {'value': season, 'operator': 'eq'}
        }
        all_data = self.adapter.get_filtered_data(filters=filters)
        
        if all_data.empty:
            return SeriesData(
                label_x_axis="Spieltag", 
                label_y_axis="Position", 
                name="Position im Saisonverlauf", 
                query_params={"season": season, "league": league_name}
            ).to_dict()
        
        # Get all weeks and teams
        all_weeks = sorted(all_data['Week'].unique())
        all_teams = sorted(all_data['Team'].unique())
        
        # Calculate weekly points for each team (individual + team points)
        weekly_points = {}
        for team in all_teams:
            weekly_points[team] = []
            for week in all_weeks:
                week_data = all_data[(all_data['Team'] == team) & (all_data['Week'] == week)]
                if not week_data.empty:
                    # Sum up all points (individual + team) for this team in this week
                    total_week_points = week_data['Points'].sum()
                    weekly_points[team].append(total_week_points)
                else:
                    weekly_points[team].append(0)
        
        # Create SeriesData
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
        # Get all data for this league and season (both individual and team points)
        filters = {
            'League': {'value': league_name, 'operator': 'eq'},
            'Season': {'value': season, 'operator': 'eq'}
        }
        all_data = self.adapter.get_filtered_data(filters=filters)
        
        if all_data.empty:
            return SeriesData(
                label_x_axis="Spieltag", 
                label_y_axis="Punkte", 
                name="Punkte im Saisonverlauf", 
                query_params={"season": season, "league": league_name}
            ).to_dict()
        
        # Get all weeks and teams
        all_weeks = sorted(all_data['Week'].unique())
        all_teams = sorted(all_data['Team'].unique())
        
        # Calculate weekly points for each team (individual + team points)
        weekly_points = {}
        for team in all_teams:
            weekly_points[team] = []
            for week in all_weeks:
                week_data = all_data[(all_data['Team'] == team) & (all_data['Week'] == week)]
                if not week_data.empty:
                    # Sum up all points (individual + team) for this team in this week
                    total_week_points = week_data['Points'].sum()
                    weekly_points[team].append(total_week_points)
                else:
                    weekly_points[team].append(0)
        
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