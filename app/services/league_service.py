from business_logic.statistics import query_database
from app.services.data_manager import DataManager
from data_access.schema import Columns, ColumnsExtra
from data_access.adapters.data_adapter import DataAdapter
from data_access.adapters.data_adapter_factory import DataAdapterFactory, DataAdapterSelector
import pandas as pd
from typing import List
from business_logic.server import Server
from flask import jsonify, Response

class LeagueService:
    # fetches dataframes from server
    # converts dataframes to dicts
    # jsonifies dicts   
    # forwards JSON dict to app routes
    def __init__(self):
        self.server = Server()

    def get_valid_combinations(self):
        """Returns all existing combinations in the database"""
        combinations = self.df[[Columns.season, Columns.league_name, Columns.week]].drop_duplicates()
        print(combinations)
        return combinations.to_dict('records')

    def get_seasons(self):
        """Returns all possible seasons"""
        return self.server.get_seasons()

    def get_leagues(self):
        """Returns all possible leagues"""
        return self.server.get_leagues()

    def get_weeks(self, league_name:str=None, season:str=None):
        """Returns all possible match days"""
        return self.server.get_weeks(league_name=league_name, season=season)

    def get_teams_in_league_season(self, league_name:str, season:str, debug_output:bool=False) -> List[str]:
        return self.server.get_teams_in_league_season(league_name=league_name, season=season, debug_output=debug_output)

    def get_league_week(self, league:str, season:str, week:int=None, history_depth:int=None) -> Response:     
        """Get results of a league on a specific match day"""
        return self.server.get_league_week(league_name=league, season=season, week=week).to_dict('records')

    def get_honor_scores(self, league:str=None, season:str=None, week:int=None, team_name:str=None, player_name:str=None, individual_scores:int=1, team_scores:int=1, indivdual_averages:int=1, team_averages:int=1) -> Response:
        
        individual_scores_df, team_scores_df, individual_averages_df, team_averages_df = self.server.get_honor_scores(
            league_name=league, season=season, week=week, team_name=team_name, player_name=player_name, 
            individual_scores=individual_scores, team_scores=team_scores, indivdual_averages=indivdual_averages, team_averages=team_averages)

        honor_scores = dict()
        honor_scores['individual_scores'] = individual_scores_df.to_dict('records')
        honor_scores['team_scores'] = team_scores_df.to_dict('records')
        honor_scores['individual_averages'] = individual_averages_df.to_dict('records')
        honor_scores['team_averages'] = team_averages_df.to_dict('records') 

        return honor_scores



    def get_league_history_table(self, league_name:str, season:str, week:int=None, depth:int=None, debug_output:bool=False) -> Response:    
        if debug_output:
            print("get_league_history_table")
            print("league_name: " + league_name + " season: " + season + " week: " + str(week) + " depth: " + str(depth))
        data = self.server.get_league_history(league_name=league_name, season=season, week=week, depth=-1, debug_output=debug_output)
        # find all weeks
        weeks = data[Columns.week].unique()
        # groupby week
        
        data_collected_by_week = dict()
        data_per_week = data.groupby(Columns.week)

        # collect by week
        for week, group in data_per_week:
            if debug_output & 0 :
                print("week : " + str(week))
                print(group)
            data_collected_by_week[week] = group.to_dict('records')
        # concat all weeks
        # collect by team    
        
        data_collected_by_team = dict()
        columns_per_day = [Columns.score, Columns.points]
        columns_total = [ColumnsExtra.score_weekly, ColumnsExtra.points_weekly, ColumnsExtra.score_average_weekly]
        
        data_collected_by_team['headerGroups'] = [[Columns.team_name, 2]] + [['Week' + str(w), len(columns_per_day) ] for w in weeks] + [["Season Total", len(columns_per_day) +1]]
        data_collected_by_team['columns'] = ['Pos', Columns.team_name] + columns_per_day * max(weeks) + columns_per_day + [ColumnsExtra.score_average]
        data_collected_by_team['data'] = []

        data_per_team = data.groupby(Columns.team_name)
        data_per_team = sorted(data_per_team, key=lambda x: x[1][Columns.points].sum(), reverse=True)

        for idx, (team, group) in enumerate(data_per_team):
            team_row = [idx+1, team]
            if debug_output:
                print("team : " + str(team))
                print(group)
            points = float(round(group[Columns.points].sum(), 1))
            score = int(group[Columns.score].sum())
            score_average = float(round(group[ColumnsExtra.score_average].sum() / len(group), 2))

            for row in group.to_dict('records'):
                rows_to_extract = [row[col] for col in columns_per_day]
                team_row.extend(rows_to_extract)
                #rows_to_extract = [row[col] for col in columns_total]
                
            team_row.extend([score, points, score_average])
            data_collected_by_team['data'].append(team_row)
        #print(data_collected_by_week)
        if debug_output:
            print("collected data by team: " + str(data_collected_by_team))   
        if data_collected_by_team is not None:
            return data_collected_by_team
        else:
            return pd.DataFrame().to_dict('records')


    def get_league_week_table(self, league:str, season:str, week:int=None, depth:int=None) -> Response:     
        """Get standings of a leagaue up to a specific match day"""
        #print(" >>>>>>>>>>>>>>>>>>>> doing history just for testing")
        #self.get_league_history_table(league, season, week, 3)
        #print(" <<<<<<<<<<<<<<<<<<<< done with history")
        league_standings_data = self.server.get_league_standings(league_name=league, season=season, week=week)
        league_week_data = self.server.get_league_week(league_name=league, season=season, week=week)

        
        league_standings_data = league_standings_data.rename(columns={ColumnsExtra.score_average: ColumnsExtra.score_average_weekly, 
                                                          Columns.points: ColumnsExtra.points_weekly,
                                                          Columns.score: ColumnsExtra.score_weekly})
        league_standings_data = pd.merge(league_standings_data, league_week_data, on=Columns.team_name)
        #print("league_standings_data")
        #print(league_standings_data)


        league_standings_data = league_standings_data.sort_values(by=[Columns.points])

        data_collected = dict()
        columns_to_show_week = [Columns.score, Columns.points, ColumnsExtra.score_average]
        columns_to_show_season = [ColumnsExtra.score_weekly, ColumnsExtra.points_weekly, ColumnsExtra.score_average_weekly]
        
        data_collected['headerGroups'] = [[Columns.team_name, 2]] + [['Week' + str(week), len(columns_to_show_week)]] + [["Season Total", len(columns_to_show_season)]]
        data_collected['columns'] = ['Pos', Columns.team_name] + columns_to_show_week + columns_to_show_week
        data_collected['data'] = []

        league_standing_data_groups = league_standings_data.groupby(Columns.team_name)
        league_standing_data_groups = sorted(league_standing_data_groups, key=lambda x: x[1][Columns.points].iloc[0], reverse=True)

        for idx, (team, group) in enumerate(league_standing_data_groups):
            team_row = [idx+1, team]
            for row in group.to_dict('records'):
                rows_to_extract = [row[col] for col in columns_to_show_week]
                team_row.extend(rows_to_extract)
                rows_to_extract = [row[col] for col in columns_to_show_season]
                team_row.extend(rows_to_extract)
            data_collected['data'].append(team_row)

        #print(data_collected)

        return data_collected 


    def get_team_week_details(self, league:str, season:str, team:str, week:int) -> Response:
        return(self.server.get_team_week_details(league_name=league, season=season, team_name=team, week=week))



    def sort_by_cumulative_points_in_last_available_week(self, df):
        # Get the last week's data and sort by PointsCumulative
        last_week = df[df[Columns.week] == df[Columns.week].max()]
        final_order = last_week.sort_values(ColumnsExtra.points_cumulative, ascending=False)[Columns.team_name].tolist()
        
        # Create a categorical type with the desired order
        df[Columns.team_name] = pd.Categorical(df[Columns.team_name], categories=final_order, ordered=True)
        
        # Sort by Week and then Team (which now follows the final standings order)
        sorted_df = df.sort_values([Columns.week, Columns.team_name])
        
        return sorted_df


    def get_team_points_during_season(self, league_name: str, season: str) -> dict:
        """Get team points for each week during the season."""
        rankings = self.server.get_team_positions_and_points_during_season(league_name, season)
        #print("league_service.get_team_positions_during_season")
        #print(rankings)

        rankings = self.sort_by_cumulative_points_in_last_available_week(rankings)
        #print(rankings)

        
        rankings_grouped = rankings.groupby(Columns.team_name, observed=True)
        
        rankings_dict = dict()
        rankings_dict['weekly'] = dict()
        rankings_dict['cumulative'] = dict()


        for team, group in rankings_grouped:
            rankings_dict['weekly'][team] = group[Columns.points].tolist()
            rankings_dict['cumulative'][team] = group[ColumnsExtra.points_cumulative].tolist()

        return rankings_dict


    def get_team_positions_during_season(self, league_name: str, season: str) -> dict:
        """Get team positions for each week during the season."""
        rankings = self.server.get_team_positions_and_points_during_season(league_name, season)
        #print("league_service.get_team_positions_during_season")
        #print(rankings)

        rankings = self.sort_by_cumulative_points_in_last_available_week(rankings)
        #print(rankings)

        
        rankings_grouped = rankings.groupby(Columns.team_name, observed=True)
        
        rankings_dict = dict()
        rankings_dict['weekly'] = dict()
        rankings_dict['cumulative'] = dict()


        for team, group in rankings_grouped:
            rankings_dict['weekly'][team] = group[ColumnsExtra.position_weekly].tolist()
            rankings_dict['cumulative'][team] = group[ColumnsExtra.position_cumulative].tolist()

        return rankings_dict
        print(rankings_dict)

        weekly_pivot = rankings.pivot(index=Columns.team_name, columns=Columns.week, values=ColumnsExtra.position_weekly)
        weekly_pivot.columns = [f'Week {w} Pos' for w in weekly_pivot.columns]

        cumulative_pivot = rankings.pivot(index=Columns.team_name, columns=Columns.week, values=ColumnsExtra.position_cumulative)
        cumulative_pivot.columns = [f'Week {w} Cum' for w in cumulative_pivot.columns]

        

        for team, group in rankings_grouped:
            rankings_dict['weekly'][team] = group[ColumnsExtra.position_weekly].tolist()
            rankings_dict['cumulative'][team] = group[ColumnsExtra.position_cumulative].tolist()

        print(weekly_pivot)
        print(cumulative_pivot)

        return rankings_dict

    def get_team_averages_during_season(self, league_name: str, season: str) -> dict:
        """Get team average points for each week during the season."""
        df = self.server.get_team_averages_during_season(league_name, season)
        return df.to_dict(orient='records')       



    def get_league_week_table_deprecated(self, league:str, season:str, week:int=None, depth:int=None) -> Response:     
        """Get standings of a leagaue up to a specific match day"""
        #print(" >>>>>>>>>>>>>>>>>>>> doing history just for testing")
        #self.get_league_history_table(league, season, week, 3)
        #print(" <<<<<<<<<<<<<<<<<<<< done with history")
        league_standings_data = self.server.get_league_week(league_name=league, season=season, week=week)
        league_week_data = self.server.get_league_week(league_name=league, season=season, week=week)

        
        league_standings_data = league_standings_data.rename(columns={ColumnsExtra.score_average: ColumnsExtra.score_average_weekly, 
                                                          Columns.points: ColumnsExtra.points_weekly,
                                                          Columns.score: ColumnsExtra.score_weekly})
        league_standings_data = pd.merge(league_standings_data, league_week_data, on=Columns.team_name)
        #print(league_standings_data)
        return league_standings_data.to_dict('records') 
        # if no depth is provided, use 1 to fetch also the data of the current week
        if depth is None or depth < 1:
            depth = 1

        # history should not be deeper than the current week
        depth = min(depth, week)

        data_season = self.server.get_league_season(league_name=league, season=season, week=week, depth=depth)
        for week_current in range(week-depth, week):
            print(f"fetching week {week_current}")
            data_week = self.server.get_league_week(league_name=league, season=season, week=week_current)
        
        data_week = self.server.get_league_week(league_name=league, season=season, week=week)

        # Apply base filters
        return self.server.get_league_week(league_name=league, season=season, week=week).to_dict('records')



        table_data = []

        for _, row in lala.iterrows():
            table_row = {
                Columns.team_name: row[Columns.team_name],
                Columns.points: row[Columns.points],
                ColumnsExtra.average_score: row[ColumnsExtra.average_score],
                ColumnsExtra.position_change: row[ColumnsExtra.position_change],
            }

            table_data.append(table_row)

            if cumulative:
                table_row[ColumnsExtra.points_weekly] = row[ColumnsExtra.points_weekly]
                table_row[ColumnsExtra.average_score_weekly] = row[ColumnsExtra.average_score_weekly]


        #team_data = [{'Team': 'Team1', 'TotalPoints': 100, 'Average': 190, 'positionChange': +1, 'MatchPoints': 70, 'MatchAverage': 180},
        #             {'Team': 'Team2', 'TotalPoints': 90, 'Average': 185, 'positionChange': -1, 'MatchPoints': 60, 'MatchAverage': 175}]
                    
        return jsonify({'standings': table_data})


    def deprecated_get_table1(self, df: pd.DataFrame, filters: dict, week: int, cumulative: bool, include_changes: bool):
        

        df_filtered = query_database(df, filters)
        # Apply match day filter
        if week is not None:
            if cumulative:
                df_filtered = df_filtered[df_filtered[Columns.week] <= week]
            else:
                df_filtered = df_filtered[df_filtered[Columns.week] == week]
        
        # Calculate standings
        if not df_filtered.empty:
            standings = df_filtered.groupby('Team').agg({
                'Points': 'sum',
                'Score': 'mean'
            }).reset_index()
            print(standings)
            standings.columns = ['Team', 'Points', 'Average']
            standings = standings.sort_values(['Points', 'Average'], ascending=[False, False])
            
            # Calculate position changes if requested
            if include_changes and week and week > 1:
                # Get previous match day standings
                prev_filters = filters.copy()
                df_prev = query_database(df, prev_filters)
                df_prev = df_prev[df_prev[Columns.week] <= (week - 1)]
                
                prev_standings = df_prev.groupby('Team').agg({
                    'Points': 'sum',
                    'Score': 'mean'
                }).reset_index()
                
                prev_standings.columns = ['Team', 'Points', 'Average']
                prev_standings = prev_standings.sort_values(['Points', 'Average'], ascending=[False, False])
                
                # Calculate position changes (fixed calculation)
                current_positions = {team: pos for pos, team in enumerate(standings['Team'], 1)}
                prev_positions = {team: pos for pos, team in enumerate(prev_standings['Team'], 1)}
                
                # Positive number means team moved up, negative means team moved down
                standings['PositionChange'] = standings['Team'].apply(
                    lambda team: prev_positions.get(team, 0) - current_positions.get(team, 0)
                )
                
            return standings
        
        return pd.DataFrame(columns=['Team', 'Points', 'Average'])


    def deprecated_get_table(self, season, league, week=None, cumulative=False, week_=None):
        """Get combined table data for frontend"""
        
        
        
        filters = {
            Columns.season: season,
            Columns.league_name: league #,
            #Columns.input_data: True
        }
        
        try:
            week_value = int(week) if week and week.strip() else None
            print(f"Processing week: {week_value}")
        except ValueError:
            print(f"Invalid match day value: {week}")
            week_value = None
        
        # Get match day standings
        week_standings = pd.DataFrame()
        if week_value is not None:
            week_standings = self.get_league_stanings(
                self.df, filters, week_value, cumulative=False, include_changes=False
            )
            print(f"Match day standings found: {not week_standings.empty}")
        
        # Get cumulative standings
        season_standings = self.get_league_stanings(
            self.df, filters, week_value, cumulative=True, include_changes=(week_value > 1)
        )
        
        # Combine the data for frontend
        combined_data = []
        for _, row in season_standings.iterrows():
            team_data = {
                'Team': row['Team'],
                'TotalPoints': row['Points'],
                'Average': row['Average'] ,
                'positionChange': row.get('PositionChange', 0)
            }
            
            if not week_standings.empty:
                match_team = week_standings[week_standings['Team'] == row['Team']]
                if not match_team.empty:
                    team_data.update({
                        'MatchPoints': match_team['Points'].iloc[0],
                        'MatchAverage': match_team['Average'].iloc[0] 
                    })
            
            combined_data.append(team_data)
        
        return {'standings': combined_data}