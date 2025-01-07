class League:

    def __init__(self, league_name, number_of_teams, number_of_players_per_team, weeks=None, skill_level: int = 7):
        self.name = league_name
        self.number_of_teams = number_of_teams
        self.number_of_players_per_team = number_of_players_per_team
        self.skill = skill_level
        self.weeks = number_of_teams if weeks is None else weeks
        self.teams = []

    def __str__(self):

        all_teams = [team.get_name() + " " + team.get_skill() for team in self.teams]
        return "\n" + self.name + " (" + str(self.skill) + ")\n------------------\n" + "\n".join(all_teams)
