from typing import Dict, List, Optional, Any
from business_logic.server import Server
from app.models.statistics_models import (
    LeagueStatistics, TeamStatistics, PlayerStatistics,
    LeagueWeekSummary, LeagueSeasonSummary,
    TeamWeekPerformance, TeamSeasonSummary,
    PlayerWeekPerformance, PlayerSeasonSummary
)
from data_access.models.raw_data_models import RawTeamData, RawLeagueData, RawPlayerData
from data_access.schema import Columns

class StatisticsService:
    def __init__(self, database: str = None):
        self.database = database
        self.server = Server(database=database)

    def get_team_statistics(self, team: str, season: str) -> Optional[TeamStatistics]:
        """Get comprehensive team statistics for a specific team and season."""
        # Get raw team data
        raw_team_data = self.server.data_adapter.get_raw_team_data(team, season)
        if not raw_team_data:
            return None
            
        # Get all weeks for this team
        weeks = sorted({p.week for p in raw_team_data.players})
        
        # Calculate weekly performances
        weekly_performances = {}
        for week in weeks:
            week_players = [p for p in raw_team_data.players if p.week == week]
            
            # Get player scores for this week
            player_scores = {
                p.player_name: p.score
                for p in week_players
            }
           
            weekly_performances[week] = TeamWeekPerformance(
                team_id=team,
                team_name=team,
                week=week,
                total_score=sum(p.score for p in week_players),
                points=sum(p.points for p in week_players),
                number_of_games=len([p.score for p in week_players]),
                player_scores=player_scores
            )
        
        # Calculate season summary
        all_scores = [p.score for p in raw_team_data.players]
        season_summary = TeamSeasonSummary(
            total_score=sum(all_scores),
            total_points=sum(p.points for p in raw_team_data.players),
            average_score=sum(all_scores) / len(all_scores) if all_scores else 0,
            games_played=len(raw_team_data.players),
            best_score=max(all_scores) if all_scores else 0,
            worst_score=min(all_scores) if all_scores else 0
        )
        
        # Get player contributions
        player_contributions = {}
        for player_name in {p.player_name for p in raw_team_data.players}:
            player_data = [p for p in raw_team_data.players if p.player_name == player_name]
            player_contributions[player_name] = {
                'total_score': sum(p.score for p in player_data),
                'average_score': sum(p.score for p in player_data) / len(player_data),
                'games_played': len(player_data)
            }
        
        return TeamStatistics(
            team_name=team,
            season=season,
            weekly_performances=weekly_performances,
            season_summary=season_summary,
            player_contributions=player_contributions
        )

    def get_league_statistics(self, league: str, season: str) -> Optional[LeagueStatistics]:
        """Get comprehensive league statistics"""
        # Get raw league data
        raw_league_data = self.server.data_adapter.get_raw_league_data(league, season)
        if not raw_league_data:
            return None
            
        # Process data for each team
        team_stats = {}
        player_stats = {}
        weekly_summaries = {}
        
        # Get all weeks in the league
        all_weeks = sorted({
            p.week 
            for team in raw_league_data.teams 
            for p in team.players
        })
        
        # Create weekly summaries
        for week in all_weeks:
            week_data = {}
            for team in raw_league_data.teams:
                week_players = [p for p in team.players if p.week == week]
                if week_players:
                    week_data[team.team_name] = [
                        sum(p.score for p in week_players),  # Total pins
                        sum(p.points for p in week_players),  # Points
                        sum(p.score for p in week_players) / len(week_players) / len(week_players)  # Average
                    ]
            weekly_summaries[week] = LeagueWeekSummary(data=week_data)
        
        # Create season summary
        season_data = {}
        for team in raw_league_data.teams:
            season_data[team.team_name] = [
                sum(p.score for p in team.players),  # Total pins
                sum(p.points for p in team.players),  # Points
                sum(p.score for p in team.players) / len(team.players) / len(team.players) # Average
            ]
        season_summary = LeagueSeasonSummary(data=season_data)
        
        # Get team and player statistics
        for team in raw_league_data.teams:
            team_stats[team.team_name] = self.get_team_statistics(team.team_name, season)
            for player_name in {p.player_name for p in team.players}:
                player_stats[player_name] = self.get_player_statistics(player_name, season)
        
        return LeagueStatistics(
            name=league,
            season=season,
            team_stats=team_stats,
            player_stats=player_stats,
            weekly_summaries=weekly_summaries,
            season_summary=season_summary
        )

    def get_player_statistics(self, player: str, season: str) -> PlayerStatistics:
        """Get comprehensive player statistics"""
        # Get raw data from server
        player_data = self.server.data_adapter.get_filtered_data(
            filters={
                Columns.player_name: {'value': player, 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'}
            }
        )
        
        if player_data.empty:
            return None
            
        # Process weekly performances
        weekly_performances = {}
        weeks = sorted(player_data[Columns.week].unique())
        
        for week in weeks:
            week_data = player_data[player_data[Columns.week] == week]
            
            weekly_performances[week] = PlayerWeekPerformance(
                player_id=str(week_data[Columns.player_id].iloc[0]),
                player_name=player,
                week=week,
                score=week_data[Columns.score].sum(),
                points=week_data[Columns.points].sum(),
                games_played=len(week_data)
            )
        
        # Calculate season summary
        season_summary = PlayerSeasonSummary(
            total_score=player_data[Columns.score].sum(),
            total_points=player_data[Columns.points].sum(),
            average_score=player_data[Columns.score].mean(),
            games_played=len(player_data),
            best_score=player_data[Columns.score].max(),
            worst_score=player_data[Columns.score].min()
        )
        
        # Calculate team contribution
        team_data = self.server.data_adapter.get_filtered_data(
            filters={
                Columns.team_name: {'value': player_data[Columns.team_name].iloc[0], 'operator': 'eq'},
                Columns.season: {'value': season, 'operator': 'eq'}
            }
        )
        team_contribution = (season_summary.total_score / team_data[Columns.score].sum()) * 100
        
        return PlayerStatistics(
            name=player,
            season=season,
            weekly_performances=weekly_performances,
            season_summary=season_summary,
            team_contribution=team_contribution
        )

    def get_team_series_data(self, team_name: str, season: str, league: str, 
                            x_field: str, y_field: str) -> Dict[str, Any]:
        """Get team series data using the new SeriesData class"""
        raw_data = self.server.data_adapter.get_team_series_data(team_name, season, league)
        
        series_data = calculate_series_data_from_dataframe(
            df=pd.DataFrame(raw_data),
            x_field=x_field,
            y_field=y_field,
            name=f"{team_name} {y_field}",
            label_x=x_field,
            label_y=y_field,
            query_params={"team": team_name, "season": season, "league": league}
        )
        
        return series_data.to_dict() 