"""
League Service Legacy Functions
Archived functions that are no longer used in routes but kept for reference.
These functions use older data models or have been replaced by simpler versions.

DEPRECATED: These functions are not actively used. They are kept for:
- Reference during migration
- Potential future use
- Backward compatibility during transition period

Functions in this file:
- get_league_results() - Returns LeagueResults model (replaced by simpler table functions)
- get_league_week_table() - Old version with depth parameter (replaced by get_league_week_table_simple())
- get_league_history_table() - Returns Dict (replaced by get_league_history_table_data() which returns TableData)
- get_valid_combinations() - Only used by legacy route /league/get_combinations
- get_team_week_details() - Only used by legacy route /league/get_team_week_details (replaced by get_team_week_details_table_data())
- get_team_points_during_season() - Only used by legacy route /league/get_team_points_vs_average
"""
import warnings
from typing import Dict, Any, Optional, List
from app.models.statistics_models import LeagueResults
from app.models.table_data import TableData, ColumnGroup, Column
from app.services.i18n_service import i18n_service
from app.utils.color_constants import get_theme_color
from app.utils.league_utils import get_league_level
from data_access.models.league_models import LeagueQuery
from app.models.series_data import SeriesData


class LeagueServiceLegacy:
    """
    Legacy functions extracted from LeagueService.
    These methods require a LeagueService instance to access adapter and stats_service.
    """
    
    def __init__(self, league_service):
        """
        Initialize with a reference to the main LeagueService instance.
        
        Args:
            league_service: Instance of LeagueService to access adapter and stats_service
        """
        self.league_service = league_service
        self.adapter = league_service.adapter
        self.stats_service = league_service.stats_service
    
    def get_league_results(self, league: str, season: str) -> LeagueResults:
        """
        Get league results using the new data structure.
        
        DEPRECATED: This function is not used in any routes.
        Kept for reference or potential future use.
        
        Args:
            league: The league name
            season: The season identifier
            
        Returns:
            LeagueResults object
        """
        warnings.warn(
            "get_league_results() is deprecated and not used in routes. "
            "Consider using get_league_week_table_simple() or other table functions instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
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
            level=get_league_level(league),
            weeks=stats.weekly_summaries,
            ranking=ranking,
            data=stats.season_summary
        )
    
    def get_league_week_table(self, season: str, league: str, week: Optional[int] = None, depth: int = 1) -> TableData:
        """
        Get a formatted table for league standings with weekly breakdowns.
        
        DEPRECATED: This function has been replaced by get_league_week_table_simple().
        Routes use the simpler version without the depth parameter.
        
        Args:
            season: The season identifier
            league: The league name
            week: The current week (if None, gets the latest)
            depth: How many previous weeks to include
            
        Returns:
            TableData object with the league standings
        """
        warnings.warn(
            "get_league_week_table() is deprecated. "
            "Use get_league_week_table_simple() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # If week is not specified, get the latest week
        if week is None:
            week = self.league_service.get_latest_week(season, league)
        
        # Get team performances from the adapter
        team_performances = self.adapter.get_league_standings(season, league, week)
        
        if not team_performances:
            # Return empty table structure
            return TableData(
                columns=[],
                data=[],
                title=f"{i18n_service.get_text('no_data_available_for')} {league} - {season}"
            )
        
        # Sort by total points (descending) and assign positions
        team_performances.sort(key=lambda x: (x.total_points, x.total_score), reverse=True)
        for i, perf in enumerate(team_performances, 1):
            perf.position = i
        
        # Create column groups
        columns = [
            ColumnGroup(
                title=i18n_service.get_text("ranking"),
                frozen="left",  # Freeze this group to the left
                style={"backgroundColor": get_theme_color("background")},  # Light gray background
                columns=[
                    Column(title="#", field="pos", width="50px", align="center"),
                    Column(title=i18n_service.get_text("team"), field="team", width="200px", align="left")
                ]
            )
        ]
        
        # Add columns for each week
        start_week = max(1, week - depth + 1)
        for w in range(start_week, week + 1):
            columns.append(
                ColumnGroup(
                    title=f"{i18n_service.get_text('week')} {w}",
                    columns=[
                        Column(title=i18n_service.get_text("pins"), field=f"week{w}_score", format="{:,}"),
                        Column(title=i18n_service.get_text("points"), field=f"week{w}_points", format="{:.1f}"),
                        Column(title=i18n_service.get_text("avg"), field=f"week{w}_avg", format="{:.1f}")
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
                    Column(title=i18n_service.get_text("points"), field="total_points", width="80px", align="center"),
                    Column(title=i18n_service.get_text("score"), field="total_score", width="80px", align="center"),
                    Column(title=i18n_service.get_text("avg"), field="average", width="80px", align="center")
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
            description=f"{i18n_service.get_text('through_week')} {week}",
            config={
                "stickyHeader": True,  # Make header sticky
                "striped": True,       # Use striped rows
                "hover": True,         # Enable hover effect
                "responsive": True,    # Make table responsive
                "compact": False       # Use normal spacing
            }
        )
    
    def get_league_history_table(self, league_name: str, season: str, week: Optional[int] = None, 
                               depth: Optional[int] = None, debug_output: bool = False) -> Dict[str, Any]:
        """
        Get league history table data.
        
        DEPRECATED: This function returns a Dict. 
        Routes use get_league_history_table_data() which returns TableData.
        
        Args:
            league_name: The league name
            season: The season identifier
            week: The week number (if None, gets the latest)
            depth: Optional depth parameter (not used in current implementation)
            debug_output: Whether to print debug information
            
        Returns:
            Dictionary with league history data
        """
        warnings.warn(
            "get_league_history_table() is deprecated. "
            "Use get_league_history_table_data() instead, which returns TableData.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Get team performances
        standings = self.league_service.get_league_standings(season, league_name, week)
        
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
    
    def get_valid_combinations(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Get valid combinations of season, league, and weeks.
        
        DEPRECATED: This function is only used by the legacy route /league/get_combinations.
        """
        warnings.warn(
            "get_valid_combinations() is deprecated and only used by legacy route.",
            DeprecationWarning,
            stacklevel=2
        )
        
        result = {}
        seasons = self.league_service.get_seasons()
        
        for season in seasons:
            result[season] = {}
            leagues = self.league_service.get_leagues()
            
            for league in leagues:
                weeks = self.league_service.get_weeks(league_name=league, season=season)
                if weeks:
                    result[season][league] = weeks
        
        return result
    
    def get_team_week_details(self, league: str, season: str, team: str, week: int) -> Dict[str, Any]:
        """
        Get details for a specific team in a specific week.
        
        DEPRECATED: This function is only used by the legacy route /league/get_team_week_details.
        Production uses get_team_week_details_table_data() instead.
        """
        warnings.warn(
            "get_team_week_details() is deprecated. "
            "Use get_team_week_details_table_data() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
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
    
    def get_team_points_during_season(self, league_name: str, season: str) -> Dict[str, Any]:
        """
        Get team points throughout a season.
        
        DEPRECATED: This function is only used by the legacy route /league/get_team_points_vs_average.
        """
        warnings.warn(
            "get_team_points_during_season() is deprecated and only used by legacy route.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Get all teams and their performances
        standings = self.league_service.get_league_standings(season, league_name)
        
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
