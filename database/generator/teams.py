from business_logic.team import Team

class DataGeneratorTeam(Team):
    def __init__(self, team_name, players, home_alley):
        super().__init__(team_name, players, home_alley)

    def get_skill(self):
        skills = [player.skill for player in self.players]
        avg = round(sum(skills) / len(skills), 2)
        return "(" + str(avg) + ")"