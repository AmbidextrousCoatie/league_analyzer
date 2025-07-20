from typing import Dict, Any
from enum import Enum
import threading

class Language(Enum):
    ENGLISH = "en"
    GERMAN = "de"

class I18nService:
    """Internationalization service for managing multi-language strings"""
    
    def __init__(self, default_language: Language = Language.ENGLISH):
        self.default_language = default_language
        self._current_language = default_language
        self._lock = threading.Lock()
        self._translations = {
            Language.ENGLISH: {
                # Common table headers
                "points": "Pts",
                "score": "Pins", 
                "average": "Avg",
                "position": "Pos",
                "team": "Team",
                "name": "Name",
                "week": "Week",
                "total": "Total",
                "ranking": "Ranking",
                "opponent": "Opponent",
                "round": "#",
                
                # Table titles and descriptions
                "league_standings": "League Standings",
                "league_history": "League History",
                "team_week_details": "Team Week Details",
                "head_to_head": "Head-to-Head",
                "match_day": "Match Day",
                "through_week": "Through Week",
                "week_results": "Week Results & Season Totals",
                "total_until_week": "Total until Week",
                
                # Navigation and UI
                "select_match_day": "Please select a match day.",
                "loading_data": "Loading data...",
                "no_data_found": "No data found for these filters",
                "error_loading_data": "Error loading data",
                "missing_parameters": "Missing required parameters",
                
                # Chart labels
                "match_day_label": "Match Day",
                "position_label": "Position",
                "points_label": "Points",
                "average_label": "Average",
                "position_progression": "Position Progression",
                "points_progression": "Points Progression",
                "average_progression": "Average Progression",
                
                # Error messages
                "season_league_required": "Season and league are required",
                "no_data_available": "No data available",
                
                # Language names
                "english": "English",
                "german": "Deutsch",
                
                # Card headers and UI elements
                "league_statistics": "League Statistics",
                "season": "Season",
                "league": "League", 
                "week": "Week",
                "team": "Team",
                "season_overview": "Season Overview",
                "position_in_season_progress": "Position in Season Progress",
                "points_in_season_progress": "Points in Season Progress",
                "points_per_match_day": "Points per Match Day",
                "position_per_match_day": "Position per Match Day",
                "average_per_match_day": "Average per Match Day",
                "points_vs_average": "Points vs. Average",
                "league_results_match_day": "League Results - Match Day",
                "honor_scores": "Honor Scores",
                "top_individual_scores": "Top Individual Scores",
                "top_team_scores": "Top Team Scores",
                "best_individual_averages": "Best Individual Averages",
                "best_team_averages": "Best Team Averages",
                "score_sheet_selected_team": "Score Sheet for Selected Team",
                "details": "Details",
                "head_to_head": "Head-to-Head",
                "refresh_data": "Refresh Data",
                "please_select_combination": "Please select a combination of Season and League.",
                "please_select_match_day": "Please select a match day.",
                "please_select_team": "Please select a team to display the score sheet.",
                
                # Chart labels
                "match_day_label": "Match Day",
                "match_day_format": "Match Day #{week}",
            },
            Language.GERMAN: {
                # Common table headers
                "points": "Pts",
                "score": "Pins",
                "average": "Avg", 
                "position": "Pos",
                "team": "Team",
                "name": "Name",
                "week": "Spieltag",
                "total": "Gesamt",
                "ranking": "Rang",
                "opponent": "Gegner",
                "round": "#",
                
                # Table titles and descriptions
                "league_standings": "Liga-Tabelle",
                "league_history": "Liga-Verlauf",
                "team_week_details": "Team-Spieltagedetails",
                "head_to_head": "Direktvergleich",
                "match_day": "Spieltag",
                "through_week": "Bis Spieltag",
                "week_results": "Spieltag-Ergebnisse & Saison-Gesamt",
                "total_until_week": "Gesamt bis Spieltag",
                
                # Navigation and UI
                "select_match_day": "Bitte wählen Sie einen Spieltag aus.",
                "loading_data": "Daten werden geladen...",
                "no_data_found": "Keine Daten für diese Filter gefunden",
                "error_loading_data": "Fehler beim Laden der Daten",
                "missing_parameters": "Erforderliche Parameter fehlen",
                
                # Chart labels
                "match_day_label": "Spieltag",
                "position_label": "Position",
                "points_label": "Punkte",
                "average_label": "Durchschnitt",
                "position_progression": "Positionsverlauf",
                "points_progression": "Punkteverlauf",
                "average_progression": "Durchschnittsverlauf",
                
                # Error messages
                "season_league_required": "Saison und Liga sind erforderlich",
                "no_data_available": "Keine Daten verfügbar",
                
                # Language names
                "english": "English",
                "german": "Deutsch",
                
                # Card headers and UI elements
                "league_statistics": "Liga-Statistiken",
                "season": "Saison",
                "league": "Liga", 
                "week": "Spieltag",
                "team": "Team",
                "season_overview": "Saison-Übersicht",
                "position_in_season_progress": "Position im Saison-Verlauf",
                "points_in_season_progress": "Punkte im Saison-Verlauf",
                "points_per_match_day": "Punkte pro Spieltag",
                "position_per_match_day": "Position pro Spieltag",
                "average_per_match_day": "Durchschnitt pro Spieltag",
                "points_vs_average": "Punkte vs. Durchschnitt",
                "league_results_match_day": "Liga-Ergebnisse - Spieltag",
                "honor_scores": "Bestleistungen",
                "top_individual_scores": "Höchste Einzel-Ergebnisse",
                "top_team_scores": "Höchste Team-Ergebnisse",
                "best_individual_averages": "Beste Einzel-Durchschnitte",
                "best_team_averages": "Beste Team-Durchschnitte", 
                "score_sheet_selected_team": "Spielbericht für ausgewähltes Team",
                "details": "Details",
                "head_to_head": "Direktvergleich",
                "refresh_data": "Daten aktualisieren",
                "please_select_combination": "Bitte wählen Sie eine Kombination aus Saison und Liga.",
                "please_select_match_day": "Bitte wählen Sie einen Spieltag.",
                "please_select_team": "Bitte wählen Sie ein Team, um den Spielbericht anzuzeigen.",
                
                # Chart labels
                "match_day_label": "Spieltag",
                "match_day_format": "Spieltag #{week}",
            }
        }
    
    def get_text(self, key: str) -> str:
        """Get translated text for the given key"""
        with self._lock:
            return self._translations[self._current_language].get(key, key)
    
    def set_language(self, language: Language):
        """Set the current language"""
        with self._lock:
            self._current_language = language
    
    def get_current_language(self) -> Language:
        """Get the current language"""
        with self._lock:
            return self._current_language
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages with their display names"""
        return {
            Language.ENGLISH.value: self.get_text("english"),
            Language.GERMAN.value: self.get_text("german")
        }

# Global instance
i18n_service = I18nService() 