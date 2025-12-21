"""
Tests for StandingsCalculator domain service.
"""

import pytest
from uuid import uuid4
from datetime import datetime
from domain.domain_services.standings_calculator import (
    StandingsCalculator,
    TeamStanding,
    WeeklyPerformance,
    Standings
)
from domain.value_objects.standings_status import StandingsStatus
from domain.entities.game import Game
from domain.entities.team import Team
from domain.entities.league import League
from domain.value_objects import Score, Points, Season, GameResult


class TestStandingsCalculator:
    """Test cases for StandingsCalculator domain service."""
    
    def test_calculate_standings_single_week(self):
        """Test calculating standings for a single week."""
        # Create teams
        team1 = Team(id=uuid4(), name="Team A")
        team2 = Team(id=uuid4(), name="Team B")
        
        # Create league
        league = League(id=uuid4(), name="Test League", season=Season("2024-25"))
        league.add_team(team1)
        league.add_team(team2)
        
        # Create games for week 1
        game1 = Game(
            id=uuid4(),
            league_id=league.id,
            season=Season("2024-25"),
            week=1,
            team_id=team1.id,
            opponent_team_id=team2.id
        )
        
        # Team 1 scores: 180, 190, 200, 210 = 780 total, 2 points (win)
        game1.add_result(GameResult(
            player_id=uuid4(),
            position=1,
            scratch_score=Score(180),
            points=Points(0.5)
        ))
        game1.add_result(GameResult(
            player_id=uuid4(),
            position=2,
            scratch_score=Score(190),
            points=Points(0.5)
        ))
        game1.add_result(GameResult(
            player_id=uuid4(),
            position=3,
            scratch_score=Score(200),
            points=Points(0.5)
        ))
        game1.add_result(GameResult(
            player_id=uuid4(),
            position=4,
            scratch_score=Score(210),
            points=Points(0.5)
        ))
        
        # Team 2 scores: 170, 180, 190, 200 = 740 total, 0 points (loss)
        game1.add_result(GameResult(
            player_id=uuid4(),
            position=1,
            scratch_score=Score(170),
            points=Points(0)
        ))
        game1.add_result(GameResult(
            player_id=uuid4(),
            position=2,
            scratch_score=Score(180),
            points=Points(0)
        ))
        game1.add_result(GameResult(
            player_id=uuid4(),
            position=3,
            scratch_score=Score(190),
            points=Points(0)
        ))
        game1.add_result(GameResult(
            player_id=uuid4(),
            position=4,
            scratch_score=Score(200),
            points=Points(0)
        ))
        
        games = [game1]
        teams = {team1.id: team1, team2.id: team2}
        league_season_id = uuid4()
        
        standings = StandingsCalculator.calculate_standings(
            games=games,
            teams=teams,
            league_season_id=league_season_id
        )
        
        assert isinstance(standings, Standings)
        assert len(standings.teams) == 2
        
        # Team 1 should be first (2 points, 780 score)
        team1_standing = next(s for s in standings.teams if s.team_id == team1.id)
        assert team1_standing.position == 1
        assert team1_standing.total_points == 2.0
        assert team1_standing.total_score == 780.0
        
        # Team 2 should be second (0 points, 740 score)
        team2_standing = next(s for s in standings.teams if s.team_id == team2.id)
        assert team2_standing.position == 2
        assert team2_standing.total_points == 0.0
        assert team2_standing.total_score == 740.0
    
    def test_calculate_standings_multiple_weeks(self):
        """Test calculating standings across multiple weeks."""
        team1 = Team(id=uuid4(), name="Team A")
        team2 = Team(id=uuid4(), name="Team B")
        
        league = League(id=uuid4(), name="Test League", season=Season("2024-25"))
        league.add_team(team1)
        league.add_team(team2)
        
        games = []
        
        # Week 1: Team 1 wins (2 points, 780 score)
        game1 = Game(
            id=uuid4(),
            league_id=league.id,
            season=Season("2024-25"),
            week=1,
            team_id=team1.id,
            opponent_team_id=team2.id
        )
        for i, score in enumerate([180, 190, 200, 210], 1):
            game1.add_result(GameResult(
                player_id=uuid4(),
                position=i,
                scratch_score=Score(score),
                points=Points(0.5)
            ))
        for i, score in enumerate([170, 180, 190, 200], 1):
            game1.add_result(GameResult(
                player_id=uuid4(),
                position=i,
                scratch_score=Score(score),
                points=Points(0)
            ))
        games.append(game1)
        
        # Week 2: Team 2 wins (2 points, 800 score)
        game2 = Game(
            id=uuid4(),
            league_id=league.id,
            season=Season("2024-25"),
            week=2,
            team_id=team1.id,
            opponent_team_id=team2.id
        )
        for i, score in enumerate([160, 170, 180, 190], 1):
            game2.add_result(GameResult(
                player_id=uuid4(),
                position=i,
                scratch_score=Score(score),
                points=Points(0)
            ))
        for i, score in enumerate([200, 210, 190, 200], 1):
            game2.add_result(GameResult(
                player_id=uuid4(),
                position=i,
                scratch_score=Score(score),
                points=Points(0.5)
            ))
        games.append(game2)
        
        teams = {team1.id: team1, team2.id: team2}
        league_season_id = uuid4()
        
        standings = StandingsCalculator.calculate_standings(
            games=games,
            teams=teams,
            league_season_id=league_season_id
        )
        
        assert isinstance(standings, Standings)
        assert len(standings.teams) == 2
        
        # Both teams should have 2 points total
        # Team 2 should be first (higher total score: 800 + 740 = 1540 vs 780 + 700 = 1480)
        team1_standing = next(s for s in standings.teams if s.team_id == team1.id)
        team2_standing = next(s for s in standings.teams if s.team_id == team2.id)
        
        assert team2_standing.position == 1
        assert team2_standing.total_points == 2.0
        assert team2_standing.total_score == 1540.0
        
        assert team1_standing.position == 2
        assert team1_standing.total_points == 2.0
        assert team1_standing.total_score == 1480.0
        
        # Check weekly performances
        assert len(team1_standing.weekly_performances) == 2
        assert len(team2_standing.weekly_performances) == 2
    
    def test_calculate_standings_empty_games(self):
        """Test calculating standings with no games."""
        team1 = Team(id=uuid4(), name="Team A")
        team2 = Team(id=uuid4(), name="Team B")
        
        teams = {team1.id: team1, team2.id: team2}
        league_season_id = uuid4()
        
        standings = StandingsCalculator.calculate_standings(
            games=[],
            teams=teams,
            league_season_id=league_season_id
        )
        
        # Should return standings with zero values
        assert isinstance(standings, Standings)
        assert len(standings.teams) == 2
        for standing in standings.teams:
            assert standing.total_points == 0.0
            assert standing.total_score == 0.0
            assert len(standing.weekly_performances) == 0
    
    def test_calculate_standings_tie_breaker(self):
        """Test that standings use score as tie-breaker when points are equal."""
        team1 = Team(id=uuid4(), name="Team A")
        team2 = Team(id=uuid4(), name="Team B")
        
        league = League(id=uuid4(), name="Test League", season=Season("2024-25"))
        
        # Both teams have 2 points, but Team 1 has higher total score
        game1 = Game(
            id=uuid4(),
            league_id=league.id,
            season=Season("2024-25"),
            week=1,
            team_id=team1.id,
            opponent_team_id=team2.id
        )
        # Team 1: 800 total
        for i, score in enumerate([200, 200, 200, 200], 1):
            game1.add_result(GameResult(
                player_id=uuid4(),
                position=i,
                scratch_score=Score(score),
                points=Points(0.5)
            ))
        # Team 2: 700 total
        for i, score in enumerate([175, 175, 175, 175], 1):
            game1.add_result(GameResult(
                player_id=uuid4(),
                position=i,
                scratch_score=Score(score),
                points=Points(0)
            ))
        
        games = [game1]
        teams = {team1.id: team1, team2.id: team2}
        league_season_id = uuid4()
        
        standings = StandingsCalculator.calculate_standings(
            games=games,
            teams=teams,
            league_season_id=league_season_id
        )
        
        # Team 1 should be first (same points, higher score)
        team1_standing = next(s for s in standings.teams if s.team_id == team1.id)
        assert team1_standing.position == 1
        assert team1_standing.total_score == 800.0
        
        team2_standing = next(s for s in standings.teams if s.team_id == team2.id)
        assert team2_standing.position == 2
        assert team2_standing.total_score == 700.0

