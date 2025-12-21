"""
TEMPORARY DEMO ROUTES - CAN BE REMOVED AFTER PHASE 1

These routes are for demonstration purposes only to show domain services working.
They use test data and should be replaced with proper application layer handlers.

TODO: Remove this file when Phase 2 (Application Layer) is implemented.
"""

from fastapi import APIRouter
from typing import Dict, List
from uuid import UUID, uuid4
from datetime import datetime

from domain.entities import Team, League, Game, Player
from domain.value_objects import Score, Points, Season, GameResult
from domain.domain_services import StandingsCalculator, StatisticsCalculator
from infrastructure.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/temp/demo", tags=["TEMPORARY - Demo"])


def create_demo_data() -> Dict:
    """
    Create demo data similar to test fixtures.
    
    Returns:
        Dictionary with teams, league, games, and player_to_team mapping
    """
    # Create season
    season = Season("2024-25")
    
    # Create league
    league = League(name="Demo League", season=season)
    
    # Create teams
    team1 = Team(name="Team Alpha", league_id=league.id)
    team2 = Team(name="Team Beta", league_id=league.id)
    team3 = Team(name="Team Gamma", league_id=league.id)
    
    league.add_team(team1)
    league.add_team(team2)
    league.add_team(team3)
    
    # Create players
    players_team1 = [Player(name=f"Player {i+1}A", team_id=team1.id) for i in range(4)]
    players_team2 = [Player(name=f"Player {i+1}B", team_id=team2.id) for i in range(4)]
    players_team3 = [Player(name=f"Player {i+1}C", team_id=team3.id) for i in range(4)]
    
    all_players = players_team1 + players_team2 + players_team3
    
    # Create player-to-team mapping
    player_to_team: Dict[UUID, UUID] = {}
    for player in players_team1:
        player_to_team[player.id] = team1.id
    for player in players_team2:
        player_to_team[player.id] = team2.id
    for player in players_team3:
        player_to_team[player.id] = team3.id
    
    # Create games
    games: List[Game] = []
    
    # Week 1: Team 1 vs Team 2 (Team 1 wins)
    game1 = Game(
        league_id=league.id,
        season=season,
        week=1,
        team_id=team1.id,
        opponent_team_id=team2.id
    )
    # Team 1 scores: 180, 190, 200, 210 = 780 total, 2 points
    for i, (player, score) in enumerate(zip(players_team1, [180, 190, 200, 210]), 1):
        game1.add_result(GameResult(
            player_id=player.id,
            position=i,
            scratch_score=Score(score),
            points=Points(0.5)
        ))
    # Team 2 scores: 170, 180, 190, 200 = 740 total, 0 points
    for i, (player, score) in enumerate(zip(players_team2, [170, 180, 190, 200]), 1):
        game1.add_result(GameResult(
            player_id=player.id,
            position=i,
            scratch_score=Score(score),
            points=Points(0.0)
        ))
    games.append(game1)
    
    # Week 1: Team 3 vs Team 1 (Team 3 wins)
    game2 = Game(
        league_id=league.id,
        season=season,
        week=1,
        team_id=team3.id,
        opponent_team_id=team1.id
    )
    # Team 3 scores: 200, 210, 190, 200 = 800 total, 2 points
    for i, (player, score) in enumerate(zip(players_team3, [200, 210, 190, 200]), 1):
        game2.add_result(GameResult(
            player_id=player.id,
            position=i,
            scratch_score=Score(score),
            points=Points(0.5)
        ))
    # Team 1 scores: 160, 170, 180, 190 = 700 total, 0 points
    for i, (player, score) in enumerate(zip(players_team1, [160, 170, 180, 190]), 1):
        game2.add_result(GameResult(
            player_id=player.id,
            position=i,
            scratch_score=Score(score),
            points=Points(0.0)
        ))
    games.append(game2)
    
    # Week 2: Team 2 vs Team 3 (Team 2 wins)
    game3 = Game(
        league_id=league.id,
        season=season,
        week=2,
        team_id=team2.id,
        opponent_team_id=team3.id
    )
    # Team 2 scores: 200, 210, 190, 200 = 800 total, 2 points
    for i, (player, score) in enumerate(zip(players_team2, [200, 210, 190, 200]), 1):
        game3.add_result(GameResult(
            player_id=player.id,
            position=i,
            scratch_score=Score(score),
            points=Points(0.5)
        ))
    # Team 3 scores: 175, 185, 195, 205 = 760 total, 0 points
    for i, (player, score) in enumerate(zip(players_team3, [175, 185, 195, 205]), 1):
        game3.add_result(GameResult(
            player_id=player.id,
            position=i,
            scratch_score=Score(score),
            points=Points(0.0)
        ))
    games.append(game3)
    
    # Week 2: Team 1 vs Team 2 (Team 1 wins)
    game4 = Game(
        league_id=league.id,
        season=season,
        week=2,
        team_id=team1.id,
        opponent_team_id=team2.id
    )
    # Team 1 scores: 200, 200, 200, 200 = 800 total, 2 points
    for i, (player, score) in enumerate(zip(players_team1, [200, 200, 200, 200]), 1):
        game4.add_result(GameResult(
            player_id=player.id,
            position=i,
            scratch_score=Score(score),
            points=Points(0.5)
        ))
    # Team 2 scores: 175, 175, 175, 175 = 700 total, 0 points
    for i, (player, score) in enumerate(zip(players_team2, [175, 175, 175, 175]), 1):
        game4.add_result(GameResult(
            player_id=player.id,
            position=i,
            scratch_score=Score(score),
            points=Points(0.0)
        ))
    games.append(game4)
    
    teams = {
        team1.id: team1,
        team2.id: team2,
        team3.id: team3
    }
    
    return {
        'league': league,
        'teams': teams,
        'games': games,
        'players': all_players,
        'player_to_team': player_to_team
    }


@router.get("/standings")
def get_standings():
    """
    TEMPORARY: Get league standings using StandingsCalculator.
    
    This endpoint demonstrates the StandingsCalculator domain service.
    TODO: Replace with proper application layer handler.
    """
    logger.info("TEMPORARY demo endpoint: /api/temp/demo/standings accessed")
    
    demo_data = create_demo_data()
    
    # Create mock league season ID
    league_season_id = demo_data['league'].id  # Using league ID as mock
    
    standings = StandingsCalculator.calculate_standings(
        games=demo_data['games'],
        teams=demo_data['teams'],
        league_season_id=league_season_id,
        player_to_team=demo_data['player_to_team']
    )
    
    # Convert to JSON-serializable format
    result = []
    for standing in standings.teams:
        weekly_perfs = []
        for wp in standing.weekly_performances:
            weekly_perfs.append({
                'week': wp.week,
                'score': round(wp.score, 2),
                'points': round(wp.points, 2),
                'games': wp.number_of_games
            })
        
        result.append({
            'team_id': str(standing.team_id),
            'team_name': standing.team_name,
            'position': standing.position,
            'total_score': round(standing.total_score, 2),
            'total_points': round(standing.total_points, 2),
            'average_score': round(standing.average_score, 2),
            'weekly_performances': weekly_perfs
        })
    
    return {
        'league_name': demo_data['league'].name,
        'season': str(demo_data['league'].season),
        'league_season_id': str(league_season_id),
        'status': str(standings.status),
        'calculated_at': standings.calculated_at.isoformat(),
        'standings': result,
        'note': 'TEMPORARY DEMO ENDPOINT - Will be replaced in Phase 2'
    }


@router.get("/team-statistics/{team_name}")
def get_team_statistics(team_name: str):
    """
    TEMPORARY: Get team statistics using StatisticsCalculator.
    
    This endpoint demonstrates the StatisticsCalculator domain service.
    TODO: Replace with proper application layer handler.
    """
    logger.info(f"TEMPORARY demo endpoint: /api/temp/demo/team-statistics/{team_name} accessed")
    
    demo_data = create_demo_data()
    
    # Find team by name
    team = None
    for t in demo_data['teams'].values():
        if t.name == team_name:
            team = t
            break
    
    if not team:
        return {
            'error': f'Team "{team_name}" not found',
            'available_teams': [t.name for t in demo_data['teams'].values()]
        }
    
    stats = StatisticsCalculator.calculate_team_statistics(
        games=demo_data['games'],
        team_id=team.id,
        player_to_team=demo_data['player_to_team']
    )
    
    weekly_perfs = []
    for wp in stats.weekly_performances:
        weekly_perfs.append({
            'week': wp.week,
            'total_score': round(wp.total_score, 2),
            'total_points': round(wp.total_points, 2),
            'games': wp.number_of_games
        })
    
    return {
        'team_id': str(stats.team_id),
        'team_name': team_name,
        'total_score': round(stats.total_score, 2),
        'total_points': round(stats.total_points, 2),
        'games_played': stats.games_played,
        'average_score': round(stats.average_score, 2),
        'best_score': round(stats.best_score, 2),
        'worst_score': round(stats.worst_score, 2),
        'weekly_performances': weekly_perfs,
        'note': 'TEMPORARY DEMO ENDPOINT - Will be replaced in Phase 2'
    }


@router.get("/player-statistics/{player_name}")
def get_player_statistics(player_name: str):
    """
    TEMPORARY: Get player statistics using StatisticsCalculator.
    
    This endpoint demonstrates the StatisticsCalculator domain service.
    TODO: Replace with proper application layer handler.
    """
    logger.info(f"TEMPORARY demo endpoint: /api/temp/demo/player-statistics/{player_name} accessed")
    
    demo_data = create_demo_data()
    
    # Find player by name
    player = None
    for p in demo_data['players']:
        if p.name == player_name:
            player = p
            break
    
    if not player:
        return {
            'error': f'Player "{player_name}" not found',
            'available_players': [p.name for p in demo_data['players']]
        }
    
    stats = StatisticsCalculator.calculate_player_statistics(
        games=demo_data['games'],
        player_id=player.id
    )
    
    return {
        'player_id': str(stats.player_id),
        'player_name': player_name,
        'total_score': round(stats.total_score, 2),
        'total_points': round(stats.total_points, 2),
        'games_played': stats.games_played,
        'average_score': round(stats.average_score, 2),
        'best_score': round(stats.best_score, 2),
        'worst_score': round(stats.worst_score, 2),
        'note': 'TEMPORARY DEMO ENDPOINT - Will be replaced in Phase 2'
    }


@router.get("/demo-data")
def get_demo_data():
    """
    TEMPORARY: Get raw demo data structure.
    
    Useful for debugging and understanding the data model.
    TODO: Remove when proper data access layer is implemented.
    """
    logger.info("TEMPORARY demo endpoint: /api/temp/demo/demo-data accessed")
    
    demo_data = create_demo_data()
    
    return {
        'league': {
            'id': str(demo_data['league'].id),
            'name': demo_data['league'].name,
            'season': str(demo_data['league'].season)
        },
        'teams': [
            {
                'id': str(t.id),
                'name': t.name,
                'league_id': str(t.league_id)
            }
            for t in demo_data['teams'].values()
        ],
        'players': [
            {
                'id': str(p.id),
                'name': p.name,
                'team_id': str(p.team_id) if p.team_id else None
            }
            for p in demo_data['players']
        ],
        'games_count': len(demo_data['games']),
        'note': 'TEMPORARY DEMO ENDPOINT - Will be replaced in Phase 2'
    }

