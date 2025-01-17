from business_logic.player import Player
import random

class DataGeneratorPlayer(Player):
    
    def __init__(self, player_id, name_first, name_last, skill=None):
        
        self.skill = skill
        super().__init__(player_id, name_first, name_last)
        

    def simulate_score(self, is_home_alley: bool=False, has_a_good_day: bool=False):
        # 7.5 == 200
        base_score = 200

        offset_due_to_skill = self.skill - 7.5

        luck_or_lack_of = (random.random() - 0.5) * 25

        home_bonus = 15 if is_home_alley else 0

        good_day_bonus = 25 if has_a_good_day else 0

        score = base_score * (1 + offset_due_to_skill / 10) + luck_or_lack_of + home_bonus + good_day_bonus

        return int(score)