from business_logic.league import League
from typing import List
from business_logic.team import Team

class DataGeneratorLeague(League):

    def __init__(self, league_name, league_level, number_of_teams, number_of_players_per_team, weeks=None):
        super().__init__(league_name, number_of_teams, number_of_players_per_team, weeks)
        self.skill = 11-league_level
        self.last_seasons_order_names = []
        self.last_seasons_order_ids = []
        

    def simulate_player_development(self):
        # print("Simulating player development for " + self.name)
        for team in self.teams:
            skill_old = team.get_skill_raw()
        
            team.simulate_player_development()
                
            # print(team.get_name() + " " + str(skill_old) + " -> " + str(team.get_skill_raw()) + " (" + str(round(team.get_skill_raw() - skill_old, 2)) + ")")

    def set_last_seasons_order(self, sorted_teams):
        #print(sorted_teams)
        self.last_seasons_order_names = sorted_teams

    def get_names_of_teams_that_will_change_leagues(self, amount_of_team_promoted, amount_of_teams_demoted):
        teams_promoted_out = self.last_seasons_order_names[:amount_of_team_promoted]
        teams_demoted_out = self.last_seasons_order_names[-amount_of_teams_demoted:]
        return teams_promoted_out, teams_demoted_out


    def eject_team_from_league(self, team_names=List[str]):
        teams_to_eject = []
        teams_to_keep = []

        for team in self.teams:
            if team.get_name() in team_names:
                teams_to_eject.append(team)
            else:
                teams_to_keep.append(team)
        
        self.teams = teams_to_keep
        return teams_to_eject
    

    def add_team_to_league(self, team:List[Team]):
        self.teams.extend(team)

    def handle_team_transfer(self, teams_promoted_into_league=None, teams_relegated_into_league=None):    
        number_of_teams_promoted_out = len(teams_relegated_into_league) if teams_relegated_into_league is not None else 0
        number_of_teams_relegated_out = len(teams_promoted_into_league) if teams_promoted_into_league is not None else 0
        
        if number_of_teams_promoted_out > 0:
            # get teams that are promoted out of league being the top number_of_teams_promoted_out teams in the last_seasons_order_ids list
            teams_promoted_out = self.last_seasons_order_ids[:number_of_teams_promoted_out] 
            # exchange teams in teams_promoted_out with teams_promoted_into_league  
            for i in range(number_of_teams_promoted_out):
                self.teams[teams_promoted_out[i]] = teams_promoted_into_league[i]
        
        
        if number_of_teams_relegated_out > 0:
            for team in teams_relegated_into_league:
                self.teams.remove(team) 
            self.teams.insert(self.last_seasons_order_ids[team], team)
        for team in teams_relegated_into_league:
            self.teams.remove(team) 
    
    def __str__(self):

        all_teams = [team.get_name() + " " + team.get_skill() for team in self.teams]
        return "\n" + self.name + " (" + str(self.skill) + ")\n------------------\n" + "\n".join(all_teams)