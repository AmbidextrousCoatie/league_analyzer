import pytest
import pandas as pd 

from database.generator.seed import find_round_robin_combinations, generate_nested_round_robin_pairings, get_round_robin_pairings_old

@pytest.fixture
def teams():
    return ["Team1", "Team2", "Team3", "Team4", "Team5", "Team6"]

def test_get_round_robin_parings(teams):
    #parings = find_round_robin_combinations(teams)
    pairings = get_round_robin_pairings_old(teams)
    for pairing in pairings:
        print(pairing)
    
    assert len(pairings) == 2
    assert len(pairings[0]) == 2
