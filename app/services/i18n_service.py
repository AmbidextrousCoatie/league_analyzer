from typing import Dict, Any
from enum import Enum
import threading
import hashlib

class Language(Enum):
    ENGLISH = "en"
    GERMAN = "de"

class I18nService:
    """Internationalization service for managing multi-language strings"""
    
    def __init__(self, default_language: Language = Language.ENGLISH):
        self.default_language = default_language
        self._current_language = default_language
        self._lock = threading.Lock()
        
        # Single source of truth: unified catalog with both languages
        self._catalog = {
            # Namespaced: UI languages
            "ui.language.english": {"en": "English", "de": "English"},
            "ui.language.german": {"en": "Deutsch", "de": "Deutsch"},

            # Namespaced: Generic UI/actions/status
            "action.refresh": {"en": "Refresh", "de": "Aktualisieren"},
            "action.update": {"en": "Update", "de": "Aktualisieren"},
            "action.dismiss": {"en": "Dismiss", "de": "Schließen"},
            "status.loading": {"en": "Loading...", "de": "Wird geladen..."},
            "status.loading_data": {"en": "Loading data...", "de": "Daten werden geladen..."},
            "status.no_data": {"en": "No data", "de": "Keine Daten"},
            "status.initialization_error.title": {"en": "Initialization Error", "de": "Initialisierungsfehler"},
            "status.initialization_error.message": {"en": "Failed to initialize the league statistics application. Please refresh the page.", "de": "Die Liga-Statistik-Anwendung konnte nicht initialisiert werden. Bitte laden Sie die Seite neu."},
            # Initialization helpers for placeholders on league page
            "status.initializing.season_league_standings": {"en": "Initializing season league standings...", "de": "Tabellenstand wird initialisiert..."},
            "status.initializing.league_aggregation": {"en": "Initializing league aggregation...", "de": "Liga-Aggregation wird initialisiert..."},
            "status.initializing.league_season_overview": {"en": "Initializing season overview...", "de": "Saisonübersicht wird initialisiert..."},
            "status.initializing.season_overview": {"en": "Initializing detailed overview...", "de": "Detaillierte Übersicht wird initialisiert..."},
            "status.initializing.matchday": {"en": "Initializing match day content...", "de": "Spieltagsinhalt wird initialisiert..."},
            "status.initializing.team_details": {"en": "Initializing team details...", "de": "Teamdetails werden initialisiert..."},
            "status.initializing.team_performance": {"en": "Initializing team performance analysis...", "de": "Teamleistungsanalyse wird initialisiert..."},
            "status.initializing.team_win_percentage": {"en": "Initializing team win percentage analysis...", "de": "Team-Siegquotenanalyse wird initialisiert..."},

            # Namespaced: Table headers
            "table.header.points": {"en": "Pts", "de": "Pkt."},
            "table.header.score": {"en": "Pins", "de": "Pins"},
            "table.header.average": {"en": "Avg", "de": "Ø"},
            "table.header.position": {"en": "Pos", "de": "Pos"},
            "table.header.team": {"en": "Team", "de": "Team"},
            "table.header.name": {"en": "Name", "de": "Name"},
            "table.header.week": {"en": "Week", "de": "Spieltag"},
            "table.header.total": {"en": "Total", "de": "Gesamt"},
            "table.header.ranking": {"en": "Ranking", "de": "Rang"},
            "table.header.opponent": {"en": "Opponent", "de": "Gegner"},
            "table.header.round": {"en": "#", "de": "#"},

            # Namespaced: Blocks
            "block.matchday.title": {"en": "League Results - Match Day", "de": "Liga-Ergebnisse - Spieltag"},
            "block.team_performance.title": {"en": "Team Performance Analysis", "de": "Team-Leistungsanalyse"},
            "block.team_details.title": {"en": "Score Sheet for Selected Team", "de": "Spielbericht für ausgewähltes Team"},
            "block.team_details.view.classic": {"en": "Classic", "de": "Klassisch"},
            "block.team_details.view.new": {"en": "New", "de": "Neu"},
            "block.clutch_analysis.title": {"en": "Clutch Performance", "de": "Leistung in engen Spielen"},
            "block.clutch_analysis.description": {"en": "Performance in close games (<10 point margin)", "de": "Leistung in knappen Spielen (<10 Punkte Differenz)"},
            "block.consistency_metrics.title": {"en": "Consistency Metrics", "de": "Konsistenz-Metriken"},
            "block.consistency_metrics.description": {"en": "Team performance consistency and statistical analysis", "de": "Team-Leistungskonsistenz und statistische Analyse"},
            "block.special_matches.title": {"en": "Special Moments", "de": "Besondere Momente"},
            "block.special_matches.description": {"en": "Team record performances and notable results", "de": "Team-Rekordleistungen und bemerkenswerte Ergebnisse"},

            # Namespaced: Clutch Analysis UI
            "ui.clutch.threshold": {"en": "Clutch Threshold", "de": "Schwelle für enge Spiele"},
            "ui.clutch.points": {"en": "points", "de": "Punkte"},
            "ui.clutch.title": {"en": "Clutch Games Performance per Opponent", "de": "Leistung in engen Spielen je Gegner"},
            "ui.clutch.total_games": {"en": "Total Games", "de": "Spiele insgesamt"},
            "ui.clutch.clutch_games": {"en": "Clutch Games", "de": "Enge Spiele"},
            "ui.clutch.clutch_wins": {"en": "Clutch Wins", "de": "Enge Siege"},
            "ui.clutch.win_percentage": {"en": "Win %", "de": "Sieg %"},
            "ui.clutch.try_different": {"en": "Try selecting a different team or season", "de": "Versuchen Sie ein anderes Team oder eine andere Saison auszuwählen"},
            "ui.clutch.stats_placeholder": {"en": "Clutch statistics will appear here", "de": "Statistiken über enge Spiele werden hier angezeigt"},
            "ui.clutch.margin": {"en": "margin", "de": "Abstand"},

            # Namespaced: Consistency Metrics UI
            "ui.consistency.basic_stats": {"en": "Basic Statistics", "de": "Grundstatistiken"},
            "ui.consistency.score_range": {"en": "Score Range", "de": "Ergebnisbereich"},
            "ui.consistency.description": {"en": "Statistical analysis of team performance consistency", "de": "Statistische Analyse der Team-Leistungskonsistenz"},

            # Namespaced: Win Percentage UI
            "ui.win_percentage.title": {"en": "Win Percentage Analysis", "de": "Siegquote-Analyse"},
            "ui.win_percentage.description": {"en": "Individual player win percentages and team performance", "de": "Einzelspieler-Siegquoten und Team-Leistung"},
            "ui.win_percentage.individual": {"en": "Individual Player Win Percentages", "de": "Einzelspieler-Siegquoten"},
            "ui.win_percentage.individual_desc": {"en": "Player win percentages per week with totals", "de": "Spieler-Siegquoten pro Woche mit Gesamtwerten"},
            "ui.win_percentage.trends": {"en": "Win Percentage Trends", "de": "Siegquote-Trends"},
            "ui.win_percentage.trends_desc": {"en": "Individual player win percentages over time", "de": "Einzelspieler-Siegquoten über die Zeit"},
            "ui.win_percentage.player": {"en": "Player", "de": "Spieler"},
            "ui.win_percentage.weekly": {"en": "Weekly Win %", "de": "Wöchentliche Sieg %"},
            "ui.win_percentage.totals": {"en": "Totals", "de": "Gesamtwerte"},
            "ui.win_percentage.total_wins": {"en": "Total Wins", "de": "Gesamtsiege"},
            "ui.win_percentage.total_matches": {"en": "Total Matches", "de": "Gesamtspiele"},
            "ui.win_percentage.win_percentage": {"en": "Win %", "de": "Sieg %"},

            # Namespaced: League Aggregation/Overview UI
            "ui.league.aggregation.title": {"en": "League Aggregation", "de": "Liga-Aggregation"},
            "ui.league.all_time": {"en": "All-Time Statistics", "de": "Historische Statistiken"},
            "ui.league.performance_all_seasons": {"en": "League performance across all seasons", "de": "Liga-Leistung über alle Saisons"},
            "ui.league.averages_over_time": {"en": "League Averages Over Time", "de": "Liga-Durchschnitte über die Zeit"},
            "ui.league.points_to_win": {"en": "League Points to Win", "de": "Liga-Punkte zum Sieg"},
            "ui.league.season_overview.title": {"en": "League Season Overview", "de": "Liga-Saisonübersicht"},

            # Namespaced: League Comparison / Heatmap / Team-vs-Team
            "ui.league_comparison.title": {"en": "League Comparison", "de": "Liga-Vergleich"},
            "ui.league_comparison.description": {"en": "Team performance vs league average", "de": "Teamleistung im Vergleich zum Ligadurchschnitt"},
            "ui.league_comparison.chart_title": {"en": "Team vs League Performance by Season", "de": "Team- vs. Liga-Leistung je Saison"},
            "ui.league_comparison.loading": {"en": "Loading league comparison...", "de": "Liga-Vergleich wird geladen..."},
            "ui.league_comparison.loading_table": {"en": "Loading comparison data...", "de": "Vergleichsdaten werden geladen..."},
            "ui.league_comparison.table_placeholder": {"en": "Comparison data will appear here", "de": "Vergleichsdaten erscheinen hier"},
            "ui.comparison.difference": {"en": "Difference", "de": "Differenz"},
            "ui.team_vs_team.description": {"en": "Matrix showing team performance against each opponent", "de": "Matrix mit Teamleistung gegen jeden Gegner"},
            "ui.heatmap.legend": {"en": "Heat Map Legend", "de": "Heatmap-Legende"},
            "ui.heatmap.score": {"en": "Score Heat Map", "de": "Punkte-Heatmap"},
            "ui.heatmap.points": {"en": "Points Heat Map", "de": "Matchpunkte-Heatmap"},
            "ui.heatmap.low": {"en": "Low:", "de": "Niedrig:"},
            "ui.heatmap.high": {"en": "High:", "de": "Hoch:"},
            "ui.range_label": {"en": "Range:", "de": "Bereich:"},

            # Namespaced: Team Performance UI
            "ui.team_performance.title": {"en": "Performance Analysis", "de": "Leistungsanalyse"},
            "ui.team_performance.description": {"en": "Individual player scores and team performance over time", "de": "Einzelspielergebnisse und Teamleistung über die Zeit"},
            "ui.team_performance.individual": {"en": "Individual Player Performance", "de": "Leistung einzelner Spieler"},
            "ui.team_performance.individual_desc": {"en": "Player scores per week with totals and averages per game", "de": "Spielergebnisse pro Woche mit Summen und Durchschnitt pro Spiel"},
            "ui.team_performance.trends": {"en": "Performance Trends", "de": "Leistungstrends"},
            "ui.team_performance.trends_desc": {"en": "Individual player performance over time", "de": "Leistung einzelner Spieler über die Zeit"},
            "ui.team_performance.player_performance": {"en": "Player Performance", "de": "Spielerleistung"},
            "ui.team_performance.player_perf_desc": {"en": "Individual player average scores per game with totals and averages", "de": "Durchschnittliche Spielergebnisse pro Spiel mit Summen und Durchschnitten"},
            "ui.team_performance.weekly_avg_game": {"en": "Weekly Avg/Game", "de": "Wöchentlich Ø/Spiel"},
            "ui.team_performance.total_score": {"en": "Total Score", "de": "Gesamtpinfall"},
            "ui.team_performance.avg_per_game": {"en": "Avg/Game", "de": "Ø/Spiel"},

            # Namespaced: Team History UI
            "ui.team_history.title": {"en": "Team Position History", "de": "Team-Positionsverlauf"},
            "ui.team_history.description": {"en": "Team position across seasons and league levels", "de": "Team-Position über Saisons und Liganiveaus"},
            "ui.team_history.chart_title": {"en": "Position Progression", "de": "Positionsverlauf"},
            "ui.team_history.loading": {"en": "Loading team history...", "de": "Teamverlauf wird geladen..."},
            "ui.team_history.tooltip.league": {"en": "League:", "de": "Liga:"},
            "ui.team_history.tooltip.final_position": {"en": "Final Position:", "de": "Endplatz:"},

            # Namespaced: Messages
            "msg.please_select.match_day": {"en": "Please select a match day.", "de": "Bitte wählen Sie einen Spieltag."},
            "msg.please_select.season_league": {"en": "Please select a combination of Season and League.", "de": "Bitte wählen Sie eine Kombination aus Saison und Liga."},
            "msg.please_select.team": {"en": "Please select a team to display the score sheet.", "de": "Bitte wählen Sie ein Team, um den Spielbericht anzuzeigen."},

            # Common table headers
            "points": {"en": "Pts", "de": "Pkt."},
            "score": {"en": "Pins", "de": "Pins"},
            "average": {"en": "Ø", "de": "Ø"},
            "position": {"en": "Pos", "de": "Pos"},
            "team": {"en": "Team", "de": "Team"},
            "name": {"en": "Name", "de": "Name"},
            "week": {"en": "Week", "de": "Spieltag"},
            "total": {"en": "Total", "de": "Gesamt"},
            "ranking": {"en": "Ranking", "de": "Rang"},
            "opponent": {"en": "Opponent", "de": "Gegner"},
            "round": {"en": "#", "de": "#"},
            
            # Table titles and descriptions
            "league_standings": {"en": "League Standings", "de": "Tabellenstand"},
            "league_standings_all_leagues": {"en": "Current Standings in all Leagues", "de": "Aktuelle Tabellenstände in allen Ligen"},
            "league_history": {"en": "League History", "de": "Liga-Verlauf"},
            "team_week_details": {"en": "Team Week Details", "de": "Team-Spieltagedetails"},
            "head_to_head": {"en": "Head-to-Head", "de": "Direktvergleich"},
            "match_day": {"en": "Match Day", "de": "Spieltag"},
            "through_week": {"en": "Through Week", "de": "Bis Spieltag"},
            "week_results": {"en": "Week Results & Season Totals", "de": "Spieltag-Ergebnisse & Saison-Gesamt"},
            "total_until_week": {"en": "Total until Week", "de": "Gesamt bis Spieltag"},
            
            # Navigation and UI
            "select_match_day": {"en": "Please select a match day.", "de": "Bitte wählen Sie einen Spieltag aus."},
            "loading_data": {"en": "Loading data...", "de": "Daten werden geladen..."},
            "no_data_found": {"en": "No data found for these filters", "de": "Keine Daten für diese Filter gefunden"},
            "error_loading_data": {"en": "Error loading data", "de": "Fehler beim Laden der Daten"},
            "missing_parameters": {"en": "Missing required parameters", "de": "Erforderliche Parameter fehlen"},
            
            # Chart labels
            "match_day_label": {"en": "Match Day", "de": "Spieltag"},
            "position_label": {"en": "Position", "de": "Position"},
            "points_label": {"en": "Points", "de": "Punkte"},
            "average_label": {"en": "Average", "de": "Durchschnitt"},
            "position_progression": {"en": "Position Progression", "de": "Positionsverlauf"},
            "points_progression": {"en": "Points Progression", "de": "Punkteverlauf"},
            "average_progression": {"en": "Average Progression", "de": "Durchschnittsverlauf"},
            
            # Error messages
            "season_league_required": {"en": "Season and league are required", "de": "Saison und Liga sind erforderlich"},
            "no_data_available": {"en": "No data available", "de": "Keine Daten verfügbar"},
            
            # Language names
            "english": {"en": "English", "de": "English"},
            "german": {"en": "Deutsch", "de": "Deutsch"},
            
            # Card headers and UI elements
            "league_statistics": {"en": "League Statistics", "de": "Liga-Statistiken"},
            "season": {"en": "Season", "de": "Saison"},
            "article_male": {"en":"the", "de":"der"},
            "article_female": {"en":"the", "de":"die"},
            "article_neutral": {"en":"the", "de":"das"},
            "league": {"en": "League", "de": "Liga"},
            "season_overview": {"en": "Season Overview", "de": "Saison-Übersicht"},
            "position_in_season_progress": {"en": "Position in Season ProgressSSSssSS", "de": "Position im Saison-Verlauf"},
            "points_in_season_progress": {"en": "Points in Season Progress", "de": "Punkte im Saison-Verlauf"},
            "points_per_match_day": {"en": "Points per Match Day", "de": "Punkte pro Spieltag"},
            "position_per_match_day": {"en": "Position per Match Day", "de": "Position pro Spieltag"},
            "average_per_match_day": {"en": "Average per Match Day", "de": "Durchschnitt pro Spieltag"},
            "points_vs_average": {"en": "Points vs. Average", "de": "Punkte vs. Durchschnitt"},
            "league_results_match_day": {"en": "League Results - Match Day", "de": "Liga-Ergebnisse - Spieltag"},
            "honor_scores": {"en": "Honor Scores", "de": "Bestleistungen"},
            "top_individual_scores": {"en": "Top Individual Scores", "de": "Höchste Einzel-Ergebnisse"},
            "top_team_scores": {"en": "Top Team Scores", "de": "Höchste Team-Ergebnisse"},
            "best_individual_averages": {"en": "Best Individual Averages", "de": "Höchste Einzel-Durchschnitte"},
            "best_team_averages": {"en": "Best Team Averages", "de": "Höchste Team-Durchschnitte"},
            "score_sheet_selected_team": {"en": "Score Sheet for Selected Team", "de": "Spielbericht für ausgewähltes Team"},
            "details": {"en": "Details", "de": "Details"},
            "refresh_data": {"en": "Refresh Data", "de": "Daten aktualisieren"},
            "please_select_combination": {"en": "Please select a combination of Season and League.", "de": "Bitte wählen Sie eine Kombination aus Saison und Liga."},
            "please_select_match_day": {"en": "Please select a match day.", "de": "Bitte wählen Sie einen Spieltag."},
            "please_select_team": {"en": "Please select a team to display the score sheet.", "de": "Bitte wählen Sie ein Team, um den Spielbericht anzuzeigen."},
            
            # Chart labels
            "match_day_format": {"en": "Match Day #{week}", "de": "Spieltag #{week}"},
            
            # Additional table headers and UI elements
            "player": {"en": "Player", "de": "Spieler"},
            "pins": {"en": "Pins", "de": "Pins"},
            "avg": {"en": "Avg", "de": "Ø"},
            "games": {"en": "Games", "de": "Spiele"},
            "high_game": {"en": "High Game", "de": "Höchstes Spiel"},
            "location": {"en": "Location", "de": "Ort"},
            "status": {"en": "Status", "de": "Status"},
            "date": {"en": "Date", "de": "Datum"},
            "match_info": {"en": "Match Info", "de": "Spiel-Info"},
            "match": {"en": "Match", "de": "Spiel"},
            "total_points": {"en": "Total Points", "de": "Gesamtpinfall"},
            "team_performance": {"en": "Team Performance", "de": "Team-Leistung"},
            "season_timetable": {"en": "Season Timetable", "de": "Saison-Spielplan"},
            "individual_averages": {"en": "Individual Averages", "de": "Einzel-Durchschnitte"},
            "individual_performance": {"en": "Individual Performance", "de": "Einzel-Leistung"},
            "record_individual_games": {"en": "Record Individual Games", "de": "Rekord Einzelspiele"},
            "record_team_games": {"en": "Record Team Games", "de": "Rekord Teamspiele"},
            "team_vs_team_comparison_matrix": {"en": "Team vs Team Comparison", "de": "Mannschaftsvergleich"},
            "league_leader": {"en": "League Leader", "de": "Liga-Führer"},
            "league_average": {"en": "League Average", "de": "Liga-Durchschnitt"},
            "pins_per_game": {"en": "Pins per game", "de": "Pins pro Spiel"},
            "weeks_completed": {"en": "Weeks Completed", "de": "Abgeschlossene Spieltage"},
            "no_data": {"en": "No Data", "de": "Keine Daten"},
            "no_league_data_available": {"en": "No league data available", "de": "Keine Ligadaten verfügbar"},
            "error_loading_timetable": {"en": "Error loading timetable", "de": "Fehler beim Laden des Spielplans"},
            "error_loading_individual_averages": {"en": "Error loading individual averages", "de": "Fehler beim Laden der Einzel-Durchschnitte"},
            "error_loading_individual_record_games": {"en": "Error loading individual record games", "de": "Fehler beim Laden der Rekord Einzelspiele"},
            "error_loading_team_record_games": {"en": "Error loading team record games", "de": "Fehler beim Laden der Rekord Teamspiele"},
            "cumulative_points": {"en": "Cumulative Points", "de": "Kumulative Punkte"},
            "no_data_available_for": {"en": "No data available for", "de": "Keine Daten verfügbar für"},
            "game": {"en": "Game", "de": "Spiel"},
            "score_sheet_for": {"en": "Score sheet for", "de": "Spielbericht für"},
            "history": {"en": "History", "de": "Verlauf"},
            "top_team_performances": {"en": "Top Team Performances", "de": "Top Team-Leistungen"},
            "no_timetable_available": {"en": "No timetable available", "de": "Kein Spielplan verfügbar"},
            "venue": {"en": "Venue", "de": "Ort"},
            "match_schedule": {"en": "Match Schedule", "de": "Spielplan"},
            "no_individual_data_available": {"en": "No individual data available", "de": "Keine Einzeldaten verfügbar"},
            "top_individual_performances": {"en": "Top Individual Performances", "de": "Top Einzel-Leistungen"},
            "individual_scores": {"en": "Individual Scores", "de": "Einzel-Ergebnisse"},
            "all_individual_scores_for": {"en": "All individual scores for", "de": "Alle Einzel-Ergebnisse für"},
            "view": {"en": "View", "de": "Ansicht"},
            "own_team": {"en": "Own Team", "de": "Eigenes Team"},
            "error_loading_data_for": {"en": "Error loading data for", "de": "Fehler beim Laden der Daten für"},
            "no_data_available_for_team_week": {"en": "No data available for", "de": "Keine Daten verfügbar für"},
            "standings": {"en": "Standings", "de": "Tabelle"},
            "win_percentage": {"en": "Win Percentage", "de": "Siegquote"},
            "performance": {"en": "Performance", "de": "Leistung"},
            "team_vs_team_comparison_matrix_explanation": {"en": "Average scores and match points between teams", "de": "Gegenüberstellung der erzielten Pins und Punkte im direkten Vergleich der Teams während"},
        }

        # Derive runtime per-language maps from catalog
        self._translations = self._build_translations_from_catalog(self._catalog)
        
        # Generate version hash from catalog keys to invalidate cache when translations change
        # Sort keys for consistent hashing
        catalog_keys = sorted(self._catalog.keys())
        catalog_hash = hashlib.md5(str(catalog_keys).encode()).hexdigest()[:8]
        self._translations_version = f"cat-{catalog_hash}"
    
    def get_text(self, key: str) -> str:
        """Get translated text for the given key"""
        with self._lock:
            return self._translations[self._current_language].get(key, key)
    
    def get_translations_version(self) -> str:
        with self._lock:
            return self._translations_version

    # ---- Internal helpers ----
    def _build_translations_from_catalog(self, catalog: Dict[str, Dict[str, str]]) -> Dict[Language, Dict[str, str]]:
        """Create fast lookup maps for each language from the unified catalog."""
        en_map: Dict[str, str] = {}
        de_map: Dict[str, str] = {}
        for key, vals in catalog.items():
            en_val = vals.get('en')
            de_val = vals.get('de')
            if en_val is not None:
                en_map[key] = en_val
            if de_val is not None:
                de_map[key] = de_val
        return {Language.ENGLISH: en_map, Language.GERMAN: de_map}

    def validate_catalog(self) -> Dict[str, Dict[str, bool]]:
        """Return a report showing which keys are missing in which languages."""
        report: Dict[str, Dict[str, bool]] = {}
        for key, vals in self._catalog.items():
            report[key] = {
                'en_present': bool(vals.get('en')),
                'de_present': bool(vals.get('de')),
            }
        return report
    
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