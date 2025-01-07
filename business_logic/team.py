class Team:

    def __init__(self, team_name, players, home_alley):
        self.team_name = team_name
        self.players = players
        self.home_alley = home_alley

    def get_name(self):
        return self.team_name

    def get_skill(self):
        skills = [player.skill for player in self.players]
        avg = round(sum(skills) / len(skills), 2)
        return "(" + str(avg) + ")"

    def get_number_of_players(self):
        return len(self.players)

    def __str__(self):

        players = "\n".join([str(player) for player in self.players])
        return "\n" + self.team_name + "\n-----------------------\n" + players
