"""
Tests for Game entity.
"""

import pytest
from uuid import uuid4
from domain.entities.game import Game
from domain.value_objects.season import Season
from domain.value_objects.score import Score
from domain.value_objects.points import Points
from domain.value_objects.handicap import Handicap
from domain.value_objects.game_result import GameResult
from domain.exceptions.domain_exception import InvalidGameData


class TestGame:
    """Test cases for Game entity."""
    
    def test_create_valid_game(self):
        """Test creating a valid game."""
        league_id = uuid4()
        season = Season("2024-25")
        team1_id = uuid4()
        team2_id = uuid4()
        
        game = Game(
            league_id=league_id,
            season=season,
            week=1,
            team_id=team1_id,
            opponent_team_id=team2_id
        )
        
        assert game.league_id == league_id
        assert game.season == season
        assert game.week == 1
        assert len(game.results) == 0
    
    def test_create_game_same_teams_raises_error(self):
        """Test that game with same teams raises error."""
        team_id = uuid4()
        with pytest.raises(InvalidGameData, match="cannot play against itself"):
            Game(
                league_id=uuid4(),
                season=Season("2024-25"),
                week=1,
                team_id=team_id,
                opponent_team_id=team_id
            )
    
    def test_create_game_negative_week_raises_error(self):
        """Test that negative week raises error."""
        with pytest.raises(InvalidGameData, match="must be positive"):
            Game(
                league_id=uuid4(),
                season=Season("2024-25"),
                week=-1,
                team_id=uuid4(),
                opponent_team_id=uuid4()
            )
    
    def test_add_result(self):
        """Test adding a result to game."""
        game = Game(
            league_id=uuid4(),
            season=Season("2024-25"),
            week=1,
            team_id=uuid4(),
            opponent_team_id=uuid4()
        )
        player_id = uuid4()
        result = GameResult(
            player_id=player_id,
            position=1,
            scratch_score=Score(200.0),
            points=Points(2.0)
        )
        
        game.add_result(result)
        assert len(game.results) == 1
        assert game._find_result(player_id) == result
    
    def test_add_duplicate_result_raises_error(self):
        """Test that adding duplicate result raises error."""
        game = Game(
            league_id=uuid4(),
            season=Season("2024-25"),
            week=1,
            team_id=uuid4(),
            opponent_team_id=uuid4()
        )
        player_id = uuid4()
        result = GameResult(
            player_id=player_id,
            position=1,
            scratch_score=Score(200.0),
            points=Points(2.0)
        )
        
        game.add_result(result)
        with pytest.raises(InvalidGameData, match="already has a result"):
            game.add_result(result)
    
    def test_update_result(self):
        """Test updating a result."""
        game = Game(
            league_id=uuid4(),
            season=Season("2024-25"),
            week=1,
            team_id=uuid4(),
            opponent_team_id=uuid4()
        )
        player_id = uuid4()
        result = GameResult(
            player_id=player_id,
            position=1,
            scratch_score=Score(200.0),
            points=Points(2.0)
        )
        game.add_result(result)
        
        game.update_result(player_id, 210.0, 3.0)
        updated = game._find_result(player_id)
        assert updated.scratch_score.value == 210.0
        assert updated.points.value == 3.0
    
    def test_update_result_with_handicap(self):
        """Test updating result with handicap."""
        game = Game(
            league_id=uuid4(),
            season=Season("2024-25"),
            week=1,
            team_id=uuid4(),
            opponent_team_id=uuid4()
        )
        player_id = uuid4()
        result = GameResult(
            player_id=player_id,
            position=1,
            scratch_score=Score(200.0),
            points=Points(2.0)
        )
        game.add_result(result)
        
        new_handicap = Handicap(20.0)
        game.update_result(player_id, 180.0, 2.0, handicap=new_handicap)
        updated = game._find_result(player_id)
        assert updated.scratch_score.value == 180.0
        assert updated.handicap == new_handicap
    
    def test_update_nonexistent_result_raises_error(self):
        """Test that updating nonexistent result raises error."""
        game = Game(
            league_id=uuid4(),
            season=Season("2024-25"),
            week=1,
            team_id=uuid4(),
            opponent_team_id=uuid4()
        )
        
        with pytest.raises(InvalidGameData, match="Result not found"):
            game.update_result(uuid4(), 200.0, 2.0)
    
    def test_remove_result(self):
        """Test removing a result."""
        game = Game(
            league_id=uuid4(),
            season=Season("2024-25"),
            week=1,
            team_id=uuid4(),
            opponent_team_id=uuid4()
        )
        player_id = uuid4()
        result = GameResult(
            player_id=player_id,
            position=1,
            scratch_score=Score(200.0),
            points=Points(2.0)
        )
        game.add_result(result)
        
        game.remove_result(player_id)
        assert len(game.results) == 0
        assert game._find_result(player_id) is None
    
    def test_update_week(self):
        """Test updating week number."""
        game = Game(
            league_id=uuid4(),
            season=Season("2024-25"),
            week=1,
            team_id=uuid4(),
            opponent_team_id=uuid4()
        )
        
        game.update_week(2)
        assert game.week == 2
    
    def test_update_week_negative_raises_error(self):
        """Test that updating to negative week raises error."""
        game = Game(
            league_id=uuid4(),
            season=Season("2024-25"),
            week=1,
            team_id=uuid4(),
            opponent_team_id=uuid4()
        )
        
        with pytest.raises(InvalidGameData, match="must be positive"):
            game.update_week(-1)
    
    def test_create_game_negative_round_raises_error(self):
        """Test that negative round number raises error."""
        with pytest.raises(InvalidGameData, match="Round number must be positive"):
            Game(
                league_id=uuid4(),
                season=Season("2024-25"),
                week=1,
                team_id=uuid4(),
                opponent_team_id=uuid4(),
                round_number=-1
            )

