"""
Tests for Game entity.

Game entity represents a single player's game result in a match.
Each Game represents one player's performance in one match.
"""

import pytest
from uuid import uuid4
from domain.entities.game import Game
from domain.exceptions.domain_exception import InvalidGameData


class TestGame:
    """Test cases for Game entity."""
    
    def test_create_valid_game(self):
        """Test creating a valid game."""
        event_id = uuid4()
        player_id = uuid4()
        team_season_id = uuid4()
        
        game = Game(
            event_id=event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        
        assert game.event_id == event_id
        assert game.player_id == player_id
        assert game.team_season_id == team_season_id
        assert game.position == 1
        assert game.match_number == 1
        assert game.round_number == 1
        assert game.score == 200.0
        assert game.points == 2.0
    
    def test_create_game_missing_event_id_raises_error(self):
        """Test that game without event_id raises error."""
        with pytest.raises(InvalidGameData, match="must have an event_id"):
            Game(
                event_id=None,
                player_id=uuid4(),
                team_season_id=uuid4(),
                position=1,
                match_number=1,
                round_number=1,
                score=200.0,
                points=2.0
            )
    
    def test_create_game_missing_player_id_raises_error(self):
        """Test that game without player_id raises error."""
        with pytest.raises(InvalidGameData, match="must have a player_id"):
            Game(
                event_id=uuid4(),
                player_id=None,
                team_season_id=uuid4(),
                position=1,
                match_number=1,
                round_number=1,
                score=200.0,
                points=2.0
            )
    
    def test_create_game_missing_team_season_id_raises_error(self):
        """Test that game without team_season_id raises error."""
        with pytest.raises(InvalidGameData, match="must have a team_season_id"):
            Game(
                event_id=uuid4(),
                player_id=uuid4(),
                team_season_id=None,
                position=1,
                match_number=1,
                round_number=1,
                score=200.0,
                points=2.0
            )
    
    def test_create_game_invalid_position_low_raises_error(self):
        """Test that position < 0 raises error."""
        with pytest.raises(InvalidGameData, match="Position must be between 0 and 3"):
            Game(
                event_id=uuid4(),
                player_id=uuid4(),
                team_season_id=uuid4(),
                position=-1,
                match_number=1,
                round_number=1,
                score=200.0,
                points=2.0
            )
    
    def test_create_game_invalid_position_high_raises_error(self):
        """Test that position > 3 raises error."""
        with pytest.raises(InvalidGameData, match="Position must be between 0 and 3"):
            Game(
                event_id=uuid4(),
                player_id=uuid4(),
                team_season_id=uuid4(),
                position=4,
                match_number=1,
                round_number=1,
                score=200.0,
                points=2.0
            )
    
    def test_create_game_negative_match_number_raises_error(self):
        """Test that negative match number raises error."""
        with pytest.raises(InvalidGameData, match="Match number must be non-negative"):
            Game(
                event_id=uuid4(),
                player_id=uuid4(),
                team_season_id=uuid4(),
                position=1,
                match_number=-1,
                round_number=1,
                score=200.0,
                points=2.0
            )
    
    def test_create_game_negative_round_number_raises_error(self):
        """Test that negative round number raises error."""
        with pytest.raises(InvalidGameData, match="Round number must be positive"):
            Game(
                event_id=uuid4(),
                player_id=uuid4(),
                team_season_id=uuid4(),
                position=1,
                match_number=1,
                round_number=0,
                score=200.0,
                points=2.0
            )
    
    def test_create_game_negative_score_raises_error(self):
        """Test that negative score raises error."""
        with pytest.raises(InvalidGameData, match="Score must be non-negative"):
            Game(
                event_id=uuid4(),
                player_id=uuid4(),
                team_season_id=uuid4(),
                position=1,
                match_number=1,
                round_number=1,
                score=-1.0,
                points=2.0
            )
    
    def test_create_game_negative_points_raises_error(self):
        """Test that negative points raises error."""
        with pytest.raises(InvalidGameData, match="Points must be non-negative"):
            Game(
                event_id=uuid4(),
                player_id=uuid4(),
                team_season_id=uuid4(),
                position=1,
                match_number=1,
                round_number=1,
                score=200.0,
                points=-1.0
            )
    
    def test_update_score(self):
        """Test updating score."""
        game = Game(
            event_id=uuid4(),
            player_id=uuid4(),
            team_season_id=uuid4(),
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        
        game.update_score(210.0)
        assert game.score == 210.0
    
    def test_update_score_negative_raises_error(self):
        """Test that updating to negative score raises error."""
        game = Game(
            event_id=uuid4(),
            player_id=uuid4(),
            team_season_id=uuid4(),
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        
        with pytest.raises(InvalidGameData, match="Score must be non-negative"):
            game.update_score(-1.0)
    
    def test_update_points(self):
        """Test updating points."""
        game = Game(
            event_id=uuid4(),
            player_id=uuid4(),
            team_season_id=uuid4(),
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        
        game.update_points(3.0)
        assert game.points == 3.0
    
    def test_update_points_negative_raises_error(self):
        """Test that updating to negative points raises error."""
        game = Game(
            event_id=uuid4(),
            player_id=uuid4(),
            team_season_id=uuid4(),
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        
        with pytest.raises(InvalidGameData, match="Points must be non-negative"):
            game.update_points(-1.0)
    
    def test_set_opponent(self):
        """Test setting opponent information."""
        game = Game(
            event_id=uuid4(),
            player_id=uuid4(),
            team_season_id=uuid4(),
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        
        opponent_id = uuid4()
        opponent_team_season_id = uuid4()
        game.set_opponent(opponent_id, opponent_team_season_id)
        
        assert game.opponent_id == opponent_id
        assert game.opponent_team_season_id == opponent_team_season_id
    
    def test_set_handicap(self):
        """Test setting handicap."""
        game = Game(
            event_id=uuid4(),
            player_id=uuid4(),
            team_season_id=uuid4(),
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        
        game.set_handicap(20.0)
        assert game.handicap == 20.0
    
    def test_disqualify(self):
        """Test disqualifying a game."""
        game = Game(
            event_id=uuid4(),
            player_id=uuid4(),
            team_season_id=uuid4(),
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        
        assert game.is_disqualified == False
        game.disqualify()
        assert game.is_disqualified == True
    
    def test_clear_disqualification(self):
        """Test clearing disqualification."""
        game = Game(
            event_id=uuid4(),
            player_id=uuid4(),
            team_season_id=uuid4(),
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0,
            is_disqualified=True
        )
        
        assert game.is_disqualified == True
        game.clear_disqualification()
        assert game.is_disqualified == False
    
    def test_game_equality(self):
        """Test game equality based on ID."""
        event_id = uuid4()
        player_id = uuid4()
        team_season_id = uuid4()
        
        game1 = Game(
            event_id=event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        
        game2 = Game(
            event_id=event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        
        game3 = Game(
            event_id=event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        game3.id = game1.id  # Same ID
        
        assert game1 == game3
        assert game1 != game2
        assert game1 != "not a game"
    
    def test_game_hash(self):
        """Test game hashing."""
        event_id = uuid4()
        player_id = uuid4()
        team_season_id = uuid4()
        
        game1 = Game(
            event_id=event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        
        game2 = Game(
            event_id=event_id,
            player_id=player_id,
            team_season_id=team_season_id,
            position=1,
            match_number=1,
            round_number=1,
            score=200.0,
            points=2.0
        )
        game2.id = game1.id
        
        assert hash(game1) == hash(game2)
    
    def test_valid_positions(self):
        """Test that all valid positions (0-3) are accepted."""
        event_id = uuid4()
        player_id = uuid4()
        team_season_id = uuid4()
        
        for position in [0, 1, 2, 3]:
            game = Game(
                event_id=event_id,
                player_id=player_id,
                team_season_id=team_season_id,
                position=position,
                match_number=1,
                round_number=1,
                score=200.0,
                points=2.0
            )
            assert game.position == position
