"""
Pandas Data Adapter Implementation

Pandas-based implementation of DataAdapter interface.
"""

from pathlib import Path
from typing import Optional
import pandas as pd
from infrastructure.logging import get_logger
from infrastructure.persistence.adapters.data_adapter import DataAdapter

logger = get_logger(__name__)


class PandasDataAdapter(DataAdapter):
    """
    Pandas implementation of DataAdapter.
    
    Reads data from CSV files using pandas.
    """
    
    def __init__(self, data_path: Path):
        """
        Initialize Pandas adapter.
        
        Args:
            data_path: Path to CSV data file
        
        Raises:
            ValueError: If data_path doesn't exist
        """
        if not data_path.exists():
            raise ValueError(f"Data file not found: {data_path}")
        
        self.data_path = data_path
        self._data: Optional[pd.DataFrame] = None
        logger.debug(f"Initialized PandasDataAdapter with path: {data_path}")
    
    def _load_data(self) -> pd.DataFrame:
        """Load data from CSV file."""
        if self._data is None:
            logger.debug(f"Loading data from {self.data_path}")
            self._data = pd.read_csv(self.data_path)
            logger.debug(f"Loaded {len(self._data)} rows from {self.data_path}")
        return self._data
    
    def get_league_data(self, league_id: str, season: Optional[str] = None) -> pd.DataFrame:
        """Get league data."""
        logger.debug(f"Getting league data: league={league_id}, season={season}")
        data = self._load_data()
        
        # Filter by league
        filtered = data[data['league'] == league_id]
        
        # Filter by season if provided
        if season:
            filtered = filtered[filtered['season'] == season]
        
        logger.debug(f"Found {len(filtered)} rows for league {league_id}")
        return filtered
    
    def get_team_data(self, team_id: str, season: Optional[str] = None) -> pd.DataFrame:
        """Get team data."""
        logger.debug(f"Getting team data: team={team_id}, season={season}")
        data = self._load_data()
        
        # Filter by team
        filtered = data[data['team'] == team_id]
        
        # Filter by season if provided
        if season:
            filtered = filtered[filtered['season'] == season]
        
        logger.debug(f"Found {len(filtered)} rows for team {team_id}")
        return filtered
    
    def get_player_data(self, player_id: str, season: Optional[str] = None) -> pd.DataFrame:
        """Get player data."""
        logger.debug(f"Getting player data: player={player_id}, season={season}")
        data = self._load_data()
        
        # Filter by player
        filtered = data[data['player'] == player_id]
        
        # Filter by season if provided
        if season:
            filtered = filtered[filtered['season'] == season]
        
        logger.debug(f"Found {len(filtered)} rows for player {player_id}")
        return filtered
    
    def get_game_data(self, game_id: str) -> pd.DataFrame:
        """Get game data."""
        logger.debug(f"Getting game data: game={game_id}")
        data = self._load_data()
        
        # Filter by game
        filtered = data[data['game_id'] == game_id]
        
        logger.debug(f"Found {len(filtered)} rows for game {game_id}")
        return filtered
    
    def get_event_data(self) -> pd.DataFrame:
        """
        Get all event data from event.csv.
        
        Returns:
            DataFrame with all event data
        """
        # If data_path is event.csv itself, use it directly
        if self.data_path.name == "event.csv":
            event_path = self.data_path
        elif self.data_path.is_dir():
            # If data_path is a directory, look for event.csv inside it
            event_path = self.data_path / "event.csv"
        else:
            # Otherwise, look for event.csv in the same directory
            event_path = self.data_path.parent / "event.csv"
        
        if not event_path.exists():
            logger.warning(f"Event file not found: {event_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'dbu_id', 'league_season_id', 'event_type', 'league_week', 'tournament_stage',
                'date', 'venue_id', 'oil_pattern_id', 'status', 'disqualification_reason', 'notes'
            ])
        
        logger.debug(f"Loading event data from {event_path}")
        df = pd.read_csv(event_path)
        logger.debug(f"Loaded {len(df)} events from {event_path}")
        return df
    
    def save_event_data(self, df: pd.DataFrame) -> None:
        """
        Save event data to event.csv.
        
        Args:
            df: DataFrame with event data to save
        """
        # If data_path is event.csv itself, use it directly
        if self.data_path.name == "event.csv":
            event_path = self.data_path
        elif self.data_path.is_dir():
            # If data_path is a directory, save to event.csv inside it
            event_path = self.data_path / "event.csv"
        else:
            # Otherwise, save to event.csv in the same directory
            event_path = self.data_path.parent / "event.csv"
        
        logger.debug(f"Saving {len(df)} events to {event_path}")
        df.to_csv(event_path, index=False)
        logger.debug(f"Saved {len(df)} events to {event_path}")
        # Invalidate cache if exists
        if hasattr(self, '_event_data'):
            self._event_data = None
    
    def get_league_season_data(self) -> pd.DataFrame:
        """
        Get all league season data from league_season.csv.
        
        Returns:
            DataFrame with all league season data
        """
        league_season_path = (self.data_path / "league_season.csv") if self.data_path.is_dir() else (self.data_path.parent / "league_season.csv")
        if not league_season_path.exists():
            logger.warning(f"League season file not found: {league_season_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'league_id', 'season', 'scoring_system_id',
                'number_of_teams', 'players_per_team'
            ])
        
        logger.debug(f"Loading league season data from {league_season_path}")
        df = pd.read_csv(league_season_path)
        logger.debug(f"Loaded {len(df)} league seasons from {league_season_path}")
        return df
    
    def save_league_season_data(self, df: pd.DataFrame) -> None:
        """
        Save league season data to league_season.csv.
        
        Args:
            df: DataFrame with league season data to save
        """
        league_season_path = (self.data_path / "league_season.csv") if self.data_path.is_dir() else (self.data_path.parent / "league_season.csv")
        logger.debug(f"Saving {len(df)} league seasons to {league_season_path}")
        df.to_csv(league_season_path, index=False)
        logger.debug(f"Saved {len(df)} league seasons to {league_season_path}")
        # Invalidate cache if exists
        if hasattr(self, '_league_season_data'):
            self._league_season_data = None
    
    def get_team_season_data(self) -> pd.DataFrame:
        """
        Get all team season data from team_season.csv.
        
        Returns:
            DataFrame with all team season data
        """
        team_season_path = (self.data_path / "team_season.csv") if self.data_path.is_dir() else (self.data_path.parent / "team_season.csv")
        if not team_season_path.exists():
            logger.warning(f"Team season file not found: {team_season_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'league_season_id', 'club_id', 'team_number', 'vacancy_status'
            ])
        
        logger.debug(f"Loading team season data from {team_season_path}")
        df = pd.read_csv(team_season_path)
        logger.debug(f"Loaded {len(df)} team seasons from {team_season_path}")
        return df
    
    def save_team_season_data(self, df: pd.DataFrame) -> None:
        """
        Save team season data to team_season.csv.
        
        Args:
            df: DataFrame with team season data to save
        """
        team_season_path = (self.data_path / "team_season.csv") if self.data_path.is_dir() else (self.data_path.parent / "team_season.csv")
        logger.debug(f"Saving {len(df)} team seasons to {team_season_path}")
        df.to_csv(team_season_path, index=False)
        logger.debug(f"Saved {len(df)} team seasons to {team_season_path}")
        # Invalidate cache if exists
        if hasattr(self, '_team_season_data'):
            self._team_season_data = None
    
    def get_game_data(self) -> pd.DataFrame:
        """
        Get all game data from game.csv.
        
        Returns:
            DataFrame with all game data
        """
        game_path = (self.data_path / "game.csv") if self.data_path.is_dir() else (self.data_path.parent / "game.csv")
        if not game_path.exists():
            logger.warning(f"Game file not found: {game_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'event_id', 'player_id', 'team_season_id', 'position',
                'match_number', 'round_number', 'score', 'points',
                'opponent_id', 'opponent_team_season_id', 'handicap', 'is_disqualified'
            ])
        
        logger.debug(f"Loading game data from {game_path}")
        df = pd.read_csv(game_path)
        #logger.info(f"Loaded {len(df)} games from {game_path}")
        return df
    
    def save_game_data(self, df: pd.DataFrame) -> None:
        """
        Save game data to game.csv.
        
        Args:
            df: DataFrame with game data to save
        """
        game_path = (self.data_path / "game.csv") if self.data_path.is_dir() else (self.data_path.parent / "game.csv")
        #logger.debug(f"Saving {len(df)} games to {game_path}")
        df.to_csv(game_path, index=False)
        #logger.info(f"Saved {len(df)} games to {game_path}")
        # Invalidate cache if exists
        if hasattr(self, '_game_data'):
            self._game_data = None
    
    def get_player_data(self) -> pd.DataFrame:
        """
        Get all player data from player.csv.
        
        Returns:
            DataFrame with all player data
        """
        player_path = (self.data_path / "player.csv") if self.data_path.is_dir() else (self.data_path.parent / "player.csv")
        if not player_path.exists():
            logger.warning(f"Player file not found: {player_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'dbu_id', 'given_name', 'family_name', 'full_name'
            ])
        
        logger.debug(f"Loading player data from {player_path}")
        df = pd.read_csv(player_path)
        logger.debug(f"Loaded {len(df)} players from {player_path}")
        return df
    
    def save_player_data(self, df: pd.DataFrame) -> None:
        """
        Save player data to player.csv.
        
        Args:
            df: DataFrame with player data to save
        """
        player_path = (self.data_path / "player.csv") if self.data_path.is_dir() else (self.data_path.parent / "player.csv")
        logger.debug(f"Saving {len(df)} players to {player_path}")
        df.to_csv(player_path, index=False)
        logger.debug(f"Saved {len(df)} players to {player_path}")
        # Invalidate cache if exists
        if hasattr(self, '_player_data'):
            self._player_data = None
    
    def get_team_data(self) -> pd.DataFrame:
        """
        Get all team data from team.csv.
        
        Returns:
            DataFrame with all team data
        """
        team_path = (self.data_path / "team.csv") if self.data_path.is_dir() else (self.data_path.parent / "team.csv")
        logger.debug(f"Loading team data from {team_path}")
        
        if not team_path.exists():
            logger.debug(f"Team file not found at {team_path}, returning empty DataFrame")
            return pd.DataFrame(columns=['id', 'name', 'club_id', 'team_number', 'created_at', 'updated_at'])
        
        try:
            df = pd.read_csv(team_path)
            logger.debug(f"Loaded {len(df)} teams from {team_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading team data from {team_path}: {e}")
            return pd.DataFrame(columns=['id', 'name', 'club_id', 'team_number', 'created_at', 'updated_at'])
    
    def save_team_data(self, df: pd.DataFrame) -> None:
        """
        Save team data to team.csv.
        
        Args:
            df: DataFrame with team data to save
        """
        team_path = (self.data_path / "team.csv") if self.data_path.is_dir() else (self.data_path.parent / "team.csv")
        logger.debug(f"Saving {len(df)} teams to {team_path}")
        df.to_csv(team_path, index=False)
        logger.debug(f"Saved {len(df)} teams to {team_path}")
    
    def get_league_data(self) -> pd.DataFrame:
        """
        Get all league data from league.csv.
        
        Returns:
            DataFrame with all league data
        """
        league_path = (self.data_path / "league.csv") if self.data_path.is_dir() else (self.data_path.parent / "league.csv")
        if not league_path.exists():
            logger.warning(f"League file not found: {league_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'name', 'abbreviation', 'level'
            ])
        
        logger.debug(f"Loading league data from {league_path}")
        df = pd.read_csv(league_path)
        logger.debug(f"Loaded {len(df)} leagues from {league_path}")
        return df
    
    def save_league_data(self, df: pd.DataFrame) -> None:
        """
        Save league data to league.csv.
        
        Args:
            df: DataFrame with league data to save
        """
        league_path = (self.data_path / "league.csv") if self.data_path.is_dir() else (self.data_path.parent / "league.csv")
        logger.debug(f"Saving {len(df)} leagues to {league_path}")
        df.to_csv(league_path, index=False)
        logger.debug(f"Saved {len(df)} leagues to {league_path}")
        # Invalidate cache if exists
        if hasattr(self, '_league_data'):
            self._league_data = None
    
    def get_club_data(self) -> pd.DataFrame:
        """
        Get all club data from club.csv.
        
        Returns:
            DataFrame with all club data
        """
        club_path = (self.data_path / "club.csv") if self.data_path.is_dir() else (self.data_path.parent / "club.csv")
        if not club_path.exists():
            logger.warning(f"Club file not found: {club_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'name', 'short_name', 'home_alley_id', 'address'
            ])
        
        logger.debug(f"Loading club data from {club_path}")
        df = pd.read_csv(club_path)
        logger.debug(f"Loaded {len(df)} clubs from {club_path}")
        return df
    
    def save_club_data(self, df: pd.DataFrame) -> None:
        """
        Save club data to club.csv.
        
        Args:
            df: DataFrame with club data to save
        """
        club_path = (self.data_path / "club.csv") if self.data_path.is_dir() else (self.data_path.parent / "club.csv")
        logger.debug(f"Saving {len(df)} clubs to {club_path}")
        df.to_csv(club_path, index=False)
        logger.debug(f"Saved {len(df)} clubs to {club_path}")
        # Invalidate cache if exists
        if hasattr(self, '_club_data'):
            self._club_data = None
    
    def get_scoring_system_data(self) -> pd.DataFrame:
        """
        Get all scoring system data from scoring_system.csv.
        
        Returns:
            DataFrame with all scoring system data
        """
        scoring_system_path = (self.data_path / "scoring_system.csv") if self.data_path.is_dir() else (self.data_path.parent / "scoring_system.csv")
        if not scoring_system_path.exists():
            logger.warning(f"Scoring system file not found: {scoring_system_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'name', 'points_per_individual_match_win', 'points_per_individual_match_tie',
                'points_per_individual_match_loss', 'points_per_team_match_win', 'points_per_team_match_tie',
                'points_per_team_match_loss', 'allow_ties'
            ])
        
        logger.debug(f"Loading scoring system data from {scoring_system_path}")
        df = pd.read_csv(scoring_system_path)
        logger.debug(f"Loaded {len(df)} scoring systems from {scoring_system_path}")
        return df
    
    def save_scoring_system_data(self, df: pd.DataFrame) -> None:
        """
        Save scoring system data to scoring_system.csv.
        
        Args:
            df: DataFrame with scoring system data to save
        """
        scoring_system_path = (self.data_path / "scoring_system.csv") if self.data_path.is_dir() else (self.data_path.parent / "scoring_system.csv")
        logger.debug(f"Saving {len(df)} scoring systems to {scoring_system_path}")
        df.to_csv(scoring_system_path, index=False)
        logger.debug(f"Saved {len(df)} scoring systems to {scoring_system_path}")
        # Invalidate cache if exists
        if hasattr(self, '_scoring_system_data'):
            self._scoring_system_data = None
    
    def get_club_player_data(self) -> pd.DataFrame:
        """
        Get all club player data from club_player.csv.
        
        Returns:
            DataFrame with all club player data
        """
        club_player_path = (self.data_path / "club_player.csv") if self.data_path.is_dir() else (self.data_path.parent / "club_player.csv")
        if not club_player_path.exists():
            logger.warning(f"Club player file not found: {club_player_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'club_id', 'player_id', 'date_entry', 'date_exit'
            ])
        
        logger.debug(f"Loading club player data from {club_player_path}")
        df = pd.read_csv(club_player_path)
        logger.debug(f"Loaded {len(df)} club player relationships from {club_player_path}")
        return df
    
    def save_club_player_data(self, df: pd.DataFrame) -> None:
        """
        Save club player data to club_player.csv.
        
        Args:
            df: DataFrame with club player data to save
        """
        club_player_path = (self.data_path / "club_player.csv") if self.data_path.is_dir() else (self.data_path.parent / "club_player.csv")
        logger.debug(f"Saving {len(df)} club player relationships to {club_player_path}")
        df.to_csv(club_player_path, index=False)
        logger.debug(f"Saved {len(df)} club player relationships to {club_player_path}")
        # Invalidate cache if exists
        if hasattr(self, '_club_player_data'):
            self._club_player_data = None
    
    def get_match_data(self) -> pd.DataFrame:
        """
        Get all match data from match.csv.
        
        Returns:
            DataFrame with all match data
        """
        match_path = (self.data_path / "match.csv") if self.data_path.is_dir() else (self.data_path.parent / "match.csv")
        if not match_path.exists():
            logger.warning(f"Match file not found: {match_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'event_id', 'round_number', 'match_number',
                'team1_team_season_id', 'team2_team_season_id',
                'team1_total_score', 'team2_total_score',
                'status', 'created_at', 'updated_at'
            ])
        
        logger.debug(f"Loading match data from {match_path}")
        df = pd.read_csv(match_path)
        logger.debug(f"Loaded {len(df)} matches from {match_path}")
        return df
    
    def save_match_data(self, df: pd.DataFrame) -> None:
        """
        Save match data to match.csv.
        
        Args:
            df: DataFrame with match data to save
        """
        match_path = (self.data_path / "match.csv") if self.data_path.is_dir() else (self.data_path.parent / "match.csv")
        logger.debug(f"Saving {len(df)} matches to {match_path}")
        df.to_csv(match_path, index=False)
        logger.debug(f"Saved {len(df)} matches to {match_path}")
    
    def get_game_result_data(self) -> pd.DataFrame:
        """
        Get all game result data from game_result.csv.
        
        Returns:
            DataFrame with all game result data
        """
        game_result_path = (self.data_path / "game_result.csv") if self.data_path.is_dir() else (self.data_path.parent / "game_result.csv")
        if not game_result_path.exists():
            logger.warning(f"Game result file not found: {game_result_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'match_id', 'player_id', 'team_season_id', 'position',
                'score', 'handicap', 'is_disqualified', 'created_at', 'updated_at'
            ])
        
        logger.debug(f"Loading game result data from {game_result_path}")
        df = pd.read_csv(game_result_path)
        logger.debug(f"Loaded {len(df)} game results from {game_result_path}")
        return df
    
    def save_game_result_data(self, df: pd.DataFrame) -> None:
        """
        Save game result data to game_result.csv.
        
        Args:
            df: DataFrame with game result data to save
        """
        game_result_path = (self.data_path / "game_result.csv") if self.data_path.is_dir() else (self.data_path.parent / "game_result.csv")
        logger.debug(f"Saving {len(df)} game results to {game_result_path}")
        df.to_csv(game_result_path, index=False)
        logger.debug(f"Saved {len(df)} game results to {game_result_path}")
    
    def get_position_comparison_data(self) -> pd.DataFrame:
        """
        Get all position comparison data from position_comparison.csv.
        
        Returns:
            DataFrame with all position comparison data
        """
        comparison_path = (self.data_path / "position_comparison.csv") if self.data_path.is_dir() else (self.data_path.parent / "position_comparison.csv")
        if not comparison_path.exists():
            logger.warning(f"Position comparison file not found: {comparison_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'match_id', 'position', 'team1_player_id', 'team2_player_id',
                'team1_score', 'team2_score', 'outcome', 'created_at', 'updated_at'
            ])
        
        logger.debug(f"Loading position comparison data from {comparison_path}")
        df = pd.read_csv(comparison_path)
        logger.debug(f"Loaded {len(df)} position comparisons from {comparison_path}")
        return df
    
    def save_position_comparison_data(self, df: pd.DataFrame) -> None:
        """
        Save position comparison data to position_comparison.csv.
        
        Args:
            df: DataFrame with position comparison data to save
        """
        comparison_path = (self.data_path / "position_comparison.csv") if self.data_path.is_dir() else (self.data_path.parent / "position_comparison.csv")
        logger.debug(f"Saving {len(df)} position comparisons to {comparison_path}")
        df.to_csv(comparison_path, index=False)
        logger.debug(f"Saved {len(df)} position comparisons to {comparison_path}")
    
    def get_match_scoring_data(self) -> pd.DataFrame:
        """
        Get all match scoring data from match_scoring.csv.
        
        Returns:
            DataFrame with all match scoring data
        """
        scoring_path = (self.data_path / "match_scoring.csv") if self.data_path.is_dir() else (self.data_path.parent / "match_scoring.csv")
        if not scoring_path.exists():
            logger.warning(f"Match scoring file not found: {scoring_path}, returning empty DataFrame")
            return pd.DataFrame(columns=[
                'id', 'match_id', 'scoring_system_id',
                'team1_individual_points', 'team2_individual_points',
                'team1_match_points', 'team2_match_points',
                'computed_at', 'created_at', 'updated_at'
            ])
        
        logger.debug(f"Loading match scoring data from {scoring_path}")
        df = pd.read_csv(scoring_path)
        logger.debug(f"Loaded {len(df)} match scorings from {scoring_path}")
        return df
    
    def save_match_scoring_data(self, df: pd.DataFrame) -> None:
        """
        Save match scoring data to match_scoring.csv.
        
        Args:
            df: DataFrame with match scoring data to save
        """
        scoring_path = (self.data_path / "match_scoring.csv") if self.data_path.is_dir() else (self.data_path.parent / "match_scoring.csv")
        logger.debug(f"Saving {len(df)} match scorings to {scoring_path}")
        df.to_csv(scoring_path, index=False)
        logger.debug(f"Saved {len(df)} match scorings to {scoring_path}")

