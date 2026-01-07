"""
Tests for StandingsCalculator domain service.

NOTE: These tests may fail because StandingsCalculator uses the old Game API
(league_id, season, week, team_id, opponent_team_id, results), but the Game entity has been
refactored to use a new API (event_id, player_id, team_season_id, match_number, round_number, score, points).

The tests are kept to document expected behavior and will help guide the domain service update.
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
        # Create teams (with club_id as required by new Team model)
        club_id = uuid4()
        team1 = Team(id=uuid4(), name="Team A", club_id=club_id)
        team2 = Team(id=uuid4(), name="Team B", club_id=club_id)
        
        # Create league (teams don't need to be added to league for calculator)
        league = League(id=uuid4(), name="Test League", level=3)
        
        # Create event and team seasons for the new Game API
        event_id = uuid4()
        team1_season_id = uuid4()
        team2_season_id = uuid4()
        
        # Create games for week 1 - new Game API: one Game per player
        # Team 1 players: scores 180, 190, 200, 210 = 780 total, 2 points (win)
        team1_player_ids = [uuid4() for _ in range(4)]
        team1_scores = [180, 190, 200, 210]
        team1_games = [
            Game(
                id=uuid4(),
                event_id=event_id,
                player_id=pid,
                team_season_id=team1_season_id,
                position=i,
                match_number=1,
                round_number=1,
                score=float(score),
                points=0.5
            )
            for i, (pid, score) in enumerate(zip(team1_player_ids, team1_scores))
        ]
        
        # Team 2 players: scores 170, 180, 190, 200 = 740 total, 0 points (loss)
        team2_player_ids = [uuid4() for _ in range(4)]
        team2_scores = [170, 180, 190, 200]
        team2_games = [
            Game(
                id=uuid4(),
                event_id=event_id,
                player_id=pid,
                team_season_id=team2_season_id,
                position=i,
                match_number=1,
                round_number=1,
                score=float(score),
                points=0.0
            )
            for i, (pid, score) in enumerate(zip(team2_player_ids, team2_scores))
        ]
        
        games = team1_games + team2_games
        teams = {team1.id: team1, team2.id: team2}
        league_season_id = uuid4()
        
        # Create mappings for new Game API
        team_season_to_team = {
            team1_season_id: team1.id,
            team2_season_id: team2.id
        }
        event_to_week = {event_id: 1}
        
        standings = StandingsCalculator.calculate_standings(
            games=games,
            teams=teams,
            league_season_id=league_season_id,
            team_season_to_team=team_season_to_team,
            event_to_week=event_to_week
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
        club_id = uuid4()
        team1 = Team(id=uuid4(), name="Team A", club_id=club_id)
        team2 = Team(id=uuid4(), name="Team B", club_id=club_id)
        
        league = League(id=uuid4(), name="Test League", level=3)
        
        # Create events and team seasons
        event1_id = uuid4()
        event2_id = uuid4()
        team1_season_id = uuid4()
        team2_season_id = uuid4()
        
        games = []
        
        # Week 1: Team 1 wins (2 points, 780 score)
        # Team 1 players: 180, 190, 200, 210
        team1_week1_player_ids = [uuid4() for _ in range(4)]
        team1_week1_scores = [180, 190, 200, 210]
        for i, (pid, score) in enumerate(zip(team1_week1_player_ids, team1_week1_scores)):
            games.append(Game(
                id=uuid4(),
                event_id=event1_id,
                player_id=pid,
                team_season_id=team1_season_id,
                position=i,
                match_number=1,
                round_number=1,
                score=float(score),
                points=0.5
            ))
        
        # Team 2 players: 170, 180, 190, 200
        team2_week1_player_ids = [uuid4() for _ in range(4)]
        team2_week1_scores = [170, 180, 190, 200]
        for i, (pid, score) in enumerate(zip(team2_week1_player_ids, team2_week1_scores)):
            games.append(Game(
                id=uuid4(),
                event_id=event1_id,
                player_id=pid,
                team_season_id=team2_season_id,
                position=i,
                match_number=1,
                round_number=1,
                score=float(score),
                points=0.0
            ))
        
        # Week 2: Team 2 wins (2 points, 800 score)
        # Team 1 players: 160, 170, 180, 190
        team1_week2_player_ids = [uuid4() for _ in range(4)]
        team1_week2_scores = [160, 170, 180, 190]
        for i, (pid, score) in enumerate(zip(team1_week2_player_ids, team1_week2_scores)):
            games.append(Game(
                id=uuid4(),
                event_id=event2_id,
                player_id=pid,
                team_season_id=team1_season_id,
                position=i,
                match_number=1,
                round_number=1,
                score=float(score),
                points=0.0
            ))
        
        # Team 2 players: 200, 210, 190, 200
        team2_week2_player_ids = [uuid4() for _ in range(4)]
        team2_week2_scores = [200, 210, 190, 200]
        for i, (pid, score) in enumerate(zip(team2_week2_player_ids, team2_week2_scores)):
            games.append(Game(
                id=uuid4(),
                event_id=event2_id,
                player_id=pid,
                team_season_id=team2_season_id,
                position=i,
                match_number=1,
                round_number=1,
                score=float(score),
                points=0.5
            ))
        
        teams = {team1.id: team1, team2.id: team2}
        league_season_id = uuid4()
        
        # Create mappings for new Game API
        team_season_to_team = {
            team1_season_id: team1.id,
            team2_season_id: team2.id
        }
        event_to_week = {event1_id: 1, event2_id: 2}
        
        standings = StandingsCalculator.calculate_standings(
            games=games,
            teams=teams,
            league_season_id=league_season_id,
            team_season_to_team=team_season_to_team,
            event_to_week=event_to_week
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
        club_id = uuid4()
        team1 = Team(id=uuid4(), name="Team A", club_id=club_id)
        team2 = Team(id=uuid4(), name="Team B", club_id=club_id)
        
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
        club_id = uuid4()
        team1 = Team(id=uuid4(), name="Team A", club_id=club_id)
        team2 = Team(id=uuid4(), name="Team B", club_id=club_id)
        
        league = League(id=uuid4(), name="Test League", level=3)
        
        # Create event and team seasons
        event_id = uuid4()
        team1_season_id = uuid4()
        team2_season_id = uuid4()
        
        # Both teams have 2 points, but Team 1 has higher total score
        # Team 1: 800 total (200, 200, 200, 200)
        team1_player_ids = [uuid4() for _ in range(4)]
        team1_scores = [200, 200, 200, 200]
        team1_games = [
            Game(
                id=uuid4(),
                event_id=event_id,
                player_id=pid,
                team_season_id=team1_season_id,
                position=i,
                match_number=1,
                round_number=1,
                score=float(score),
                points=0.5
            )
            for i, (pid, score) in enumerate(zip(team1_player_ids, team1_scores))
        ]
        
        # Team 2: 700 total (175, 175, 175, 175)
        team2_player_ids = [uuid4() for _ in range(4)]
        team2_scores = [175, 175, 175, 175]
        team2_games = [
            Game(
                id=uuid4(),
                event_id=event_id,
                player_id=pid,
                team_season_id=team2_season_id,
                position=i,
                match_number=1,
                round_number=1,
                score=float(score),
                points=0.0
            )
            for i, (pid, score) in enumerate(zip(team2_player_ids, team2_scores))
        ]
        
        games = team1_games + team2_games
        teams = {team1.id: team1, team2.id: team2}
        league_season_id = uuid4()
        
        # Create mappings for new Game API
        team_season_to_team = {
            team1_season_id: team1.id,
            team2_season_id: team2.id
        }
        event_to_week = {event_id: 1}
        
        standings = StandingsCalculator.calculate_standings(
            games=games,
            teams=teams,
            league_season_id=league_season_id,
            team_season_to_team=team_season_to_team,
            event_to_week=event_to_week
        )
        
        # Team 1 should be first (same points, higher score)
        team1_standing = next(s for s in standings.teams if s.team_id == team1.id)
        assert team1_standing.position == 1
        assert team1_standing.total_score == 800.0
        
        team2_standing = next(s for s in standings.teams if s.team_id == team2.id)
        assert team2_standing.position == 2
        assert team2_standing.total_score == 700.0

