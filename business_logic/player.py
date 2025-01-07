import random

class Player:

    def __init__(self, player_id, name_first, name_last, skill=None):
        self.id = player_id
        self.name_first = name_first
        self.name_last = name_last
        self.skill = skill

    def simulate_score(self):
        # 7.5 == 200
        base_score = 200

        offset_due_to_skill = self.skill - 7.5

        luck_or_lack_of = (random.random() - 0.5) * 50

        score = base_score * (1 + offset_due_to_skill / 10) + luck_or_lack_of

        return int(score)

    def get_full_name(self):
        return self.name_first + " " + self.name_last

    def __str__(self):
        return str(self.id) + ": " + self.name_first + " " + self.name_last + " (" + str(self.skill) + ")"
