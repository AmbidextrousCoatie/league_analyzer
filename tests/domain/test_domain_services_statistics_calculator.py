"""
Tests for StatisticsCalculator domain service.

NOTE: These tests may fail because StatisticsCalculator uses the old Game API
(league_id, season, week, team_id, opponent_team_id, results), but the Game entity has been
refactored to use a new API (event_id, player_id, team_season_id, match_number, round_number, score, points).

The tests are kept to document expected behavior and will help guide the domain service update.
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
        club_id = uuid4()
        team = Team(id=uuid4(), name="Team A", club_id=club_id)
        
        # Create games with results - new Game API: one Game per player
        games = []
        player_ids = [uuid4() for _ in range(4)]
        team_season_id = uuid4()
        event1_id = uuid4()
        event2_id = uuid4()
        
        # Week 1: Team scores 780 total (180, 190, 200, 210)
        week1_scores = [180, 190, 200, 210]
        for i, (player_id, score) in enumerate(zip(player_ids, week1_scores)):
            games.append(Game(
                id=uuid4(),
                event_id=event1_id,
                player_id=player_id,
                team_season_id=team_season_id,
                position=i,
                match_number=1,
                round_number=1,
                score=float(score),
                points=0.5
            ))
        
        # Week 2: Team scores 800 total (200, 200, 200, 200)
        week2_scores = [200, 200, 200, 200]
        for i, (player_id, score) in enumerate(zip(player_ids, week2_scores)):
            games.append(Game(
                id=uuid4(),
                event_id=event2_id,
                player_id=player_id,
                team_season_id=team_season_id,
                position=i,
                match_number=1,
                round_number=1,
                score=float(score),
                points=0.5
            ))
        
        # Create mappings for new Game API
        team_season_to_team = {team_season_id: team.id}
        event_to_week = {event1_id: 1, event2_id: 2}
        
        stats = StatisticsCalculator.calculate_team_statistics(
            games=games,
            team_id=team.id,
            team_season_to_team=team_season_to_team,
            event_to_week=event_to_week
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
        team_season_id = uuid4()
        
        # Create games with results for this player - new Game API
        games = []
        event_ids = [uuid4() for _ in range(3)]
        scores = [180, 200, 190]
        
        # Week 1: Score 180
        games.append(Game(
            id=uuid4(),
            event_id=event_ids[0],
            player_id=player.id,
            team_season_id=team_season_id,
            position=0,
            match_number=1,
            round_number=1,
            score=180.0,
            points=0.5
        ))
        
        # Week 2: Score 200
        games.append(Game(
            id=uuid4(),
            event_id=event_ids[1],
            player_id=player.id,
            team_season_id=team_season_id,
            position=0,
            match_number=1,
            round_number=1,
            score=200.0,
            points=0.5
        ))
        
        # Week 3: Score 190
        games.append(Game(
            id=uuid4(),
            event_id=event_ids[2],
            player_id=player.id,
            team_season_id=team_season_id,
            position=0,
            match_number=1,
            round_number=1,
            score=190.0,
            points=0.5
        ))
        
        event_to_week = {event_ids[0]: 1, event_ids[1]: 2, event_ids[2]: 3}
        
        stats = StatisticsCalculator.calculate_player_statistics(
            games=games,
            player_id=player.id,
            event_to_week=event_to_week
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
        club_id = uuid4()
        team = Team(id=uuid4(), name="Team A", club_id=club_id)
        
        stats = StatisticsCalculator.calculate_team_statistics(
            games=[],
            team_id=team.id,
            team_season_to_team={}
        )
        
        assert stats.total_score == 0.0
        assert stats.total_points == 0.0
        assert stats.games_played == 0
        assert stats.average_score == 0.0
        assert stats.best_score == 0.0
        assert stats.worst_score == 0.0

