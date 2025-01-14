import random

class Player:

    def __init__(self, player_id, name_first, name_last):
        self.id = player_id
        self.name_first = name_first
        self.name_last = name_last

    def get_full_name(self):
        return self.name_first + " " + self.name_last

    def __str__(self):
        return str(self.id) + ": " + self.name_first + " " + self.name_last + " (" + str(self.skill) + ")"
