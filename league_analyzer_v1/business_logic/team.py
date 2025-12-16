class Team:

    def __init__(self, team_name_wo_number, team_number, players, home_alley):
        self.team_name = team_name_wo_number + " " + str(team_number)
        self.team_name_wo_number = team_name_wo_number
        self.team_number = team_number
        
        self.players = players
        self.home_alley = home_alley

    def get_name(self):
        return self.team_name

    def get_name_wo_number(self):
        return self.team_name_wo_number


    def get_number_of_players(self):
        return len(self.players)

    def __str__(self):

        players = "\n".join([str(player) for player in self.players])
        return "\n" + self.team_name + "\n-----------------------\n" + players
