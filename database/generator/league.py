from business_logic.league import League

class DataGeneratorLeague(League):

    def __init__(self, league_name, number_of_teams, number_of_players_per_team, weeks=None, skill_level: int = 7):
        super().__init__(league_name, number_of_teams, number_of_players_per_team, weeks)
        self.skill = skill_level

    def __str__(self):

        all_teams = [team.get_name() + " " + team.get_skill() for team in self.teams]
        return "\n" + self.name + " (" + str(self.skill) + ")\n------------------\n" + "\n".join(all_teams)