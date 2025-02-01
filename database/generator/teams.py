from business_logic.team import Team

class DataGeneratorTeam(Team):
    def __init__(self, team_name, players, home_alley):
        super().__init__(team_name, players, home_alley)

    def get_skill(self):
        skills = [player.skill for player in self.players]
        avg = round(sum(skills) / len(skills), 2)
        return "(" + str(avg) + ")"
    
    def get_skill_raw(self):
        skills = [player.skill for player in self.players]
        avg = round(sum(skills) / len(skills), 2)
        return round(avg, 2)
    

    def simulate_player_development(self):
        for player in self.players:
            player.simulate_player_development()

    def simulate_n_games(self, n):
        print("Simulating " + str(n) + " games for " + self.get_name() + " with skill " + str(self.get_skill()))
        for player in self.players:
            score = 0
            for i in range(n):
                score += player.simulate_score()
            print(player.get_name() + "(" + str(player.skill) + "): " + str(score/n))

