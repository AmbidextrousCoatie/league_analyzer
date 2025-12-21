"""
Tests for StatisticsCalculator domain service.
"""

import pytest
from uuid import uuid4
from domain.domain_services.statistics_calculator import (
    StatisticsCalculator,
    TeamStatistics,
    PlayerStatistics
)
from domain.entities.game import Game
from domain.entities.team import Team
from domain.entities.player import Player
from domain.value_objects import Score, Points, Season, GameResult


class TestStatisticsCalculator:
    """Test cases for StatisticsCalculator domain service."""
    
    def test_calculate_team_statistics(self):
        """Test calculating team statistics."""
        team = Team(id=uuid4(), name="Team A")
        
        # Create games with results
        games = []
        player_ids = [uuid4() for _ in range(4)]
        
        # Week 1: Team scores 780 total
        game1 = Game(
            id=uuid4(),
            league_id=uuid4(),
            season=Season("2024-25"),
            week=1,
            team_id=team.id,
            opponent_team_id=uuid4()
        )
        for i, (player_id, score) in enumerate(zip(player_ids, [180, 190, 200, 210]), 1):
            game1.add_result(GameResult(
                player_id=player_id,
                position=i,
                scratch_score=Score(score),
                points=Points(0.5)
            ))
        games.append(game1)
        
        # Week 2: Team scores 800 total
        game2 = Game(
            id=uuid4(),
            league_id=uuid4(),
            season=Season("2024-25"),
            week=2,
            team_id=team.id,
            opponent_team_id=uuid4()
        )
        for i, (player_id, score) in enumerate(zip(player_ids, [200, 200, 200, 200]), 1):
            game2.add_result(GameResult(
                player_id=player_id,
                position=i,
                scratch_score=Score(score),
                points=Points(0.5)
            ))
        games.append(game2)
        
        # Map players to team
        player_to_team = {pid: team.id for pid in player_ids}
        
        stats = StatisticsCalculator.calculate_team_statistics(
            games=games,
            team_id=team.id,
            player_to_team=player_to_team
        )
        
        assert stats.team_id == team.id
        assert stats.total_score == 1580.0  # 780 + 800
        assert stats.total_points == 4.0  # 2 + 2
        assert stats.games_played == 8  # 4 players * 2 weeks
        assert stats.average_score == 197.5  # 1580 / 8
        assert stats.best_score == 210.0
        assert stats.worst_score == 180.0
        assert len(stats.weekly_performances) == 2
    
    def test_calculate_player_statistics(self):
        """Test calculating player statistics."""
        player = Player(id=uuid4(), name="Player A", team_id=uuid4())
        
        # Create games with results for this player
        games = []
        
        # Week 1: Score 180
        game1 = Game(
            id=uuid4(),
            league_id=uuid4(),
            season=Season("2024-25"),
            week=1,
            team_id=player.team_id,
            opponent_team_id=uuid4()
        )
        game1.add_result(GameResult(
            player_id=player.id,
            position=1,
            scratch_score=Score(180),
            points=Points(0.5)
        ))
        games.append(game1)
        
        # Week 2: Score 200
        game2 = Game(
            id=uuid4(),
            league_id=uuid4(),
            season=Season("2024-25"),
            week=2,
            team_id=player.team_id,
            opponent_team_id=uuid4()
        )
        game2.add_result(GameResult(
            player_id=player.id,
            position=1,
            scratch_score=Score(200),
            points=Points(0.5)
        ))
        games.append(game2)
        
        # Week 3: Score 190
        game3 = Game(
            id=uuid4(),
            league_id=uuid4(),
            season=Season("2024-25"),
            week=3,
            team_id=player.team_id,
            opponent_team_id=uuid4()
        )
        game3.add_result(GameResult(
            player_id=player.id,
            position=1,
            scratch_score=Score(190),
            points=Points(0.5)
        ))
        games.append(game3)
        
        stats = StatisticsCalculator.calculate_player_statistics(
            games=games,
            player_id=player.id
        )
        
        assert stats.player_id == player.id
        assert stats.total_score == 570.0  # 180 + 200 + 190
        assert stats.total_points == 1.5  # 0.5 + 0.5 + 0.5
        assert stats.games_played == 3
        assert stats.average_score == 190.0  # 570 / 3
        assert stats.best_score == 200.0
        assert stats.worst_score == 180.0
    
    def test_calculate_statistics_empty_games(self):
        """Test calculating statistics with no games."""
        team = Team(id=uuid4(), name="Team A")
        
        stats = StatisticsCalculator.calculate_team_statistics(
            games=[],
            team_id=team.id,
            player_to_team={}
        )
        
        assert stats.total_score == 0.0
        assert stats.total_points == 0.0
        assert stats.games_played == 0
        assert stats.average_score == 0.0
        assert stats.best_score == 0.0
        assert stats.worst_score == 0.0

