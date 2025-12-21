"""
Seed Sample Data

Creates a sample dataset using CRUD operations on CSV repositories.
This demonstrates the repositories working end-to-end.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import asyncio
from uuid import uuid4
from datetime import datetime, timedelta
from domain.entities.league import League
from domain.entities.league_season import LeagueSeason
from domain.entities.team_season import TeamSeason
from domain.entities.event import Event
from domain.entities.game import Game
from domain.entities.player import Player
from domain.entities.team import Team
from domain.value_objects.season import Season
from domain.value_objects.event_status import EventStatus
from domain.value_objects.vacancy_status import VacancyStatus
from infrastructure.persistence.adapters.pandas_adapter import PandasDataAdapter
from infrastructure.persistence.mappers.csv.event_mapper import PandasEventMapper
from infrastructure.persistence.mappers.csv.league_season_mapper import PandasLeagueSeasonMapper
from infrastructure.persistence.mappers.csv.team_season_mapper import PandasTeamSeasonMapper
from infrastructure.persistence.mappers.csv.game_mapper import PandasGameMapper
from infrastructure.persistence.mappers.csv.player_mapper import PandasPlayerMapper
from infrastructure.persistence.mappers.csv.league_mapper import PandasLeagueMapper
from infrastructure.persistence.mappers.csv.team_mapper import PandasTeamMapper
from infrastructure.persistence.repositories.csv.event_repository import PandasEventRepository
from infrastructure.persistence.repositories.csv.league_season_repository import PandasLeagueSeasonRepository
from infrastructure.persistence.repositories.csv.team_season_repository import PandasTeamSeasonRepository
from infrastructure.persistence.repositories.csv.game_repository import PandasGameRepository
from infrastructure.persistence.repositories.csv.player_repository import PandasPlayerRepository
from infrastructure.persistence.repositories.csv.league_repository import PandasLeagueRepository
from infrastructure.persistence.repositories.csv.team_repository import PandasTeamRepository


async def seed_sample_data():
    """Create sample data using CRUD operations."""
    print("=" * 70)
    print("Seeding Sample Data Using CSV Repositories")
    print("=" * 70)
    print()
    
    # Setup data path - adapter expects a directory, not individual files
    data_path = Path("sample_data/relational_csv")
    
    # Create a single adapter for all entities (it handles multiple CSV files)
    adapter = PandasDataAdapter(data_path)
    
    event_mapper = PandasEventMapper()
    league_season_mapper = PandasLeagueSeasonMapper()
    team_season_mapper = PandasTeamSeasonMapper()
    game_mapper = PandasGameMapper()
    player_mapper = PandasPlayerMapper()
    league_mapper = PandasLeagueMapper()
    team_mapper = PandasTeamMapper()
    
    # Create repositories (all use the same adapter)
    event_repo = PandasEventRepository(adapter, event_mapper)
    league_season_repo = PandasLeagueSeasonRepository(adapter, league_season_mapper)
    team_season_repo = PandasTeamSeasonRepository(adapter, team_season_mapper)
    game_repo = PandasGameRepository(adapter, game_mapper)
    player_repo = PandasPlayerRepository(adapter, player_mapper)
    league_repo = PandasLeagueRepository(adapter, league_mapper)
    team_repo = PandasTeamRepository(adapter, team_mapper)
    
    print("Creating sample data...")
    print("-" * 70)
    
    # 1. Create League
    print("1. Creating League...")
    from domain.entities.league import get_league_long_name
    # Bayernliga (BayL) is level 3 - the highest level league in this dataset
    # (Levels 1-2 are federal leagues: 1. BL and 2. BL, not in dataset)
    league = League(
        id=uuid4(),
        name=get_league_long_name("BayL"),  # Use Bayernliga as example
        abbreviation="BayL",  # Abbreviation
        level=3  # Bayernliga is level 3 (highest in dataset)
    )
    league = await league_repo.add(league)
    print(f"   [OK] Created League: {league.name} ({league.abbreviation}, Level: {league.level}, ID: {league.id})")
    
    # 2. Create LeagueSeason
    print("2. Creating LeagueSeason...")
    league_season = LeagueSeason(
        id=uuid4(),
        league_id=league.id,
        season=Season("2024-25"),
        scoring_system_id="sample_scoring",
        number_of_teams=8,
        players_per_team=4
    )
    league_season = await league_season_repo.add(league_season)
    print(f"   [OK] Created LeagueSeason: {league_season.id}")
    
    # 3. Create Players
    print("3. Creating Players...")
    players = []
    club_id = uuid4()
    player_names = [
        ("John", "Doe"),
        ("Jane", "Smith"),
        ("Bob", "Johnson"),
        ("Alice", "Williams"),
        ("Charlie", "Brown"),
        ("Diana", "Davis"),
        ("Eve", "Miller"),
        ("Frank", "Wilson")
    ]
    
    for given, family in player_names:
        player = Player(
            id=uuid4(),
            name=f"{given} {family}",
            club_id=club_id
        )
        player = await player_repo.add(player)
        players.append(player)
        print(f"   [OK] Created Player: {player.name} (ID: {player.id})")
    
    # 4. Create Teams
    print("4. Creating Teams...")
    teams = []
    for i in range(4):
        team = Team(
            id=uuid4(),
            name=f"Team {i+1}"
        )
        team.assign_to_league(league.id)
        team = await team_repo.add(team)
        teams.append(team)
        print(f"   [OK] Created Team: {team.name} (ID: {team.id})")
    
    # 5. Create TeamSeasons
    print("5. Creating TeamSeasons...")
    team_seasons = []
    for i, team in enumerate(teams):
        team_season = TeamSeason(
            id=uuid4(),
            league_season_id=league_season.id,
            club_id=club_id,
            team_number=i+1,
            vacancy_status=VacancyStatus.ACTIVE
        )
        team_season = await team_season_repo.add(team_season)
        team_seasons.append(team_season)
        print(f"   [OK] Created TeamSeason: Team {i+1} (ID: {team_season.id})")
    
    # 6. Create Events
    print("6. Creating Events...")
    events = []
    base_date = datetime(2024, 10, 1)
    for week in range(1, 5):  # 4 weeks
        event = Event(
            id=uuid4(),
            league_season_id=league_season.id,
            event_type="league",
            league_week=week,
            date=base_date + timedelta(weeks=week-1),
            venue_id=f"venue-{week}",
            status=EventStatus.COMPLETED if week < 4 else EventStatus.SCHEDULED
        )
        event = await event_repo.add(event)
        events.append(event)
        print(f"   [OK] Created Event: Week {week} (ID: {event.id})")
    
    # 7. Create Games
    print("7. Creating Games...")
    games = []
    for event in events:
        for match_num in range(2):  # 2 matches per event
            game = Game(
                id=uuid4(),
                event_id=event.id,
                team_id=team_seasons[match_num * 2].id,
                opponent_team_id=team_seasons[match_num * 2 + 1].id,
                match_number=match_num + 1,
                round_number=1
            )
            game = await game_repo.add(game)
            games.append(game)
            print(f"   [OK] Created Game: Match {match_num+1} in Week {event.league_week} (ID: {game.id})")
    
    print()
    print("=" * 70)
    print("Sample Data Seeding Complete!")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  - Leagues: 1")
    print(f"  - League Seasons: 1")
    print(f"  - Teams: {len(teams)}")
    print(f"  - Team Seasons: {len(team_seasons)}")
    print(f"  - Players: {len(players)}")
    print(f"  - Events: {len(events)}")
    print(f"  - Games: {len(games)}")
    print()
    print("Data saved to CSV files in sample_data/relational_csv/")
    print()


if __name__ == "__main__":
    asyncio.run(seed_sample_data())

