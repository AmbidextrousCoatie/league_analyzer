"""
EligibilityService Domain Service

Checks player eligibility for teams based on club association.
Phase 2: Simple club-based eligibility.
Future: Will check roster submission and game history.
"""

from uuid import UUID
from domain.entities.player import Player
from domain.entities.team_season import TeamSeason
from domain.exceptions.domain_exception import DomainException


class InvalidEligibilityCheck(DomainException):
    """Raised when eligibility check fails."""
    pass


class EligibilityService:
    """
    Domain service for checking player eligibility.
    
    Phase 2: Simple club-based eligibility
    - All players of a club are eligible for all teams of that club
    
    Future: Will check:
    - Which team roster player was submitted to prior to season
    - Where player already played during season
    - Team switching conditions
    """
    
    @staticmethod
    def is_player_eligible_for_team(
        player: Player,
        team_season: TeamSeason
    ) -> bool:
        """
        Check if player is eligible for a team.
        
        Phase 2: Simple club-based eligibility
        Future: Will check roster submission and game history
        
        Args:
            player: Player entity
            team_season: TeamSeason entity
        
        Returns:
            True if player is eligible, False otherwise
        
        Raises:
            InvalidEligibilityCheck: If player or team_season is invalid
        """
        if player.club_id is None:
            return False
        
        if team_season.club_id is None:
            return False
        
        # Phase 2: Simple club-based eligibility
        # All players of a club are eligible for all teams of that club
        is_eligible = player.club_id == team_season.club_id
        
        # TODO: Future - Check roster submission
        # TODO: Future - Check where player already played during season
        # TODO: Future - Check team switching conditions
        
        return is_eligible
    
    @staticmethod
    def can_player_play_for_team(
        player: Player,
        team_season: TeamSeason
    ) -> bool:
        """
        Check if player can play for a team (eligibility + team availability).
        
        Args:
            player: Player entity
            team_season: TeamSeason entity
        
        Returns:
            True if player can play, False otherwise
        """
        # Check eligibility
        if not EligibilityService.is_player_eligible_for_team(player, team_season):
            return False
        
        # Check if team can participate
        if not team_season.can_participate():
            return False
        
        return True
    
    @staticmethod
    def validate_player_assignment(
        player: Player,
        team_season: TeamSeason
    ) -> None:
        """
        Validate that a player can be assigned to a team.
        
        Args:
            player: Player entity
            team_season: TeamSeason entity
        
        Raises:
            InvalidEligibilityCheck: If player is not eligible
        """
        if not EligibilityService.is_player_eligible_for_team(player, team_season):
            raise InvalidEligibilityCheck(
                f"Player {player.name} (club_id: {player.club_id}) is not eligible "
                f"for team (club_id: {team_season.club_id})"
            )
        
        if not team_season.can_participate():
            raise InvalidEligibilityCheck(
                f"Team (status: {team_season.vacancy_status}) cannot participate"
            )

