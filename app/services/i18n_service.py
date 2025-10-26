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
                "average": "Ø",
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
                
                # Additional table headers and UI elements
                "ranking": "Ranking",
                "total": "Total",
                "player": "Player",
                "position": "Pos",
                "name": "Name",
                "pins": "Pins",
                "points": "Points",
                "average": "Avg",
                "avg": "Avg",
                "round": "Round",
                "opponent": "Opponent",
                "games": "Games",
                "high_game": "High Game",
                "location": "Location",
                "status": "Status",
                "date": "Date",
                "match_info": "Match Info",
                "match": "Match",
                "total_points": "Total Points",
                "team_performance": "Team Performance",
                "season_timetable": "Season Timetable",
                "individual_averages": "Individual Averages",
                "individual_performance": "Individual Performance",
                "record_individual_games": "Record Individual Games",
                "record_team_games": "Record Team Games",
                "team_vs_team_comparison_matrix": "Team vs Team Comparison Matrix",
                "league_leader": "League Leader",
                "league_average": "League Average",
                "pins_per_game": "Pins per game",
                "weeks_completed": "Weeks Completed",
                "no_data": "No Data",
                "no_league_data_available": "No league data available",
                "error_loading_data": "Error loading data",
                "error_loading_timetable": "Error loading timetable",
                "error_loading_individual_averages": "Error loading individual averages",
                "error_loading_individual_record_games": "Error loading individual record games",
                "error_loading_team_record_games": "Error loading team record games",
                "cumulative_points": "Cumulative Points",
                "no_data_available_for": "No data available for",
                "through_week": "Through Week",
                "game": "Game",
                "match_day": "Match Day",
                "score_sheet_for": "Score sheet for",
                "history": "History",
                "top_team_performances": "Top Team Performances",
                "no_timetable_available": "No timetable available",
                "venue": "Venue",
                "match_schedule": "Match Schedule",
                "no_individual_data_available": "No individual data available",
                "individual_averages": "Individual Averages",
                "top_individual_performances": "Top Individual Performances",
                "record_individual_games": "Record Individual Games",
                "record_team_games": "Record Team Games",
                "head_to_head": "Head-to-Head",
                "individual_scores": "Individual Scores",
                "all_individual_scores_for": "All individual scores for",
                "week": "Week",
                "view": "View",
                "own_team": "Own Team",
                "error_loading_data_for": "Error loading data for",
                "no_data_available_for_team_week": "No data available for",
                "standings": "Standings",
                "team_performance": "Team Performance",
                "win_percentage": "Win Percentage",
                "performance": "Performance",
                "average_scores_and_match_points_between_teams": "Average scores and match points between teams",
                "week": "Week",
                "season": "Season",
            },
            Language.GERMAN: {
                # Common table headers
                "points": "Pkt.",
                "score": "Pins",
                "average": "Ø", 
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
                
                # Additional table headers and UI elements
                "ranking": "Rang",
                "total": "Gesamt",
                "player": "Spieler",
                "position": "Pos",
                "name": "Name",
                "pins": "Pins",
                "points": "Punkte",
                "average": "Ø",
                "avg": "Ø",
                "round": "Runde",
                "opponent": "Gegner",
                "games": "Spiele",
                "high_game": "Höchstes Spiel",
                "location": "Ort",
                "status": "Status",
                "date": "Datum",
                "match_info": "Spiel-Info",
                "match": "Spiel",
                "total_points": "Gesamtpunkte",
                "team_performance": "Team-Leistung",
                "season_timetable": "Saison-Spielplan",
                "individual_averages": "Einzel-Durchschnitte",
                "individual_performance": "Einzel-Leistung",
                "record_individual_games": "Rekord Einzelspiele",
                "record_team_games": "Rekord Teamspiele",
                "team_vs_team_comparison_matrix": "Team vs Team Vergleichsmatrix",
                "league_leader": "Liga-Führer",
                "league_average": "Liga-Durchschnitt",
                "pins_per_game": "Pins pro Spiel",
                "weeks_completed": "Abgeschlossene Spieltage",
                "no_data": "Keine Daten",
                "no_league_data_available": "Keine Ligadaten verfügbar",
                "error_loading_data": "Fehler beim Laden der Daten",
                "error_loading_timetable": "Fehler beim Laden des Spielplans",
                "error_loading_individual_averages": "Fehler beim Laden der Einzel-Durchschnitte",
                "error_loading_individual_record_games": "Fehler beim Laden der Rekord Einzelspiele",
                "error_loading_team_record_games": "Fehler beim Laden der Rekord Teamspiele",
                "cumulative_points": "Kumulative Punkte",
                "no_data_available_for": "Keine Daten verfügbar für",
                "through_week": "Bis Spieltag",
                "game": "Spiel",
                "match_day": "Spieltag",
                "score_sheet_for": "Spielbericht für",
                "history": "Verlauf",
                "top_team_performances": "Top Team-Leistungen",
                "no_timetable_available": "Kein Spielplan verfügbar",
                "venue": "Ort",
                "match_schedule": "Spielplan",
                "no_individual_data_available": "Keine Einzeldaten verfügbar",
                "individual_averages": "Einzel-Durchschnitte",
                "top_individual_performances": "Top Einzel-Leistungen",
                "record_individual_games": "Rekord Einzelspiele",
                "record_team_games": "Rekord Teamspiele",
                "head_to_head": "Direktvergleich",
                "individual_scores": "Einzel-Ergebnisse",
                "all_individual_scores_for": "Alle Einzel-Ergebnisse für",
                "week": "Spieltag",
                "view": "Ansicht",
                "own_team": "Eigenes Team",
                "error_loading_data_for": "Fehler beim Laden der Daten für",
                "no_data_available_for_team_week": "Keine Daten verfügbar für",
                "standings": "Tabelle",
                "team_performance": "Team-Leistung",
                "win_percentage": "Siegquote",
                "performance": "Leistung",
                "average_scores_and_match_points_between_teams": "Durchschnittliche Ergebnisse und Matchpunkte zwischen Teams",
                "week": "Spieltag",
                "season": "Saison",
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

# Global instance - default to German
i18n_service = I18nService(default_language=Language.GERMAN) 