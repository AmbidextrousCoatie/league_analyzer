/**
 * Simple Filter Manager
 * 
 * Simplified version without complex event bus system
 * Just manages filter state and UI synchronization
 */

class SimpleFilterManager {
    constructor(urlStateManager, mode = 'team') {
        this.urlStateManager = urlStateManager;
        this.mode = mode; // 'team' or 'league'
        this.isInitializing = false;
        this.isProcessingState = false;
        this.hasAutoSelected = false;
        this.previousState = {};
        this.availableData = {
            teams: [],
            seasons: [],
            weeks: [],
            leagues: []
        };
        
        // Track currently selected buttons for deselection detection
        this.selectedButtons = new Map(); // Map of filter type to value
        
        // Listen for state changes from URL manager
        this.urlStateManager.onStateChange((state) => {
            this.handleStateChange(state);
        });
    }
    
    /**
     * Initialize the filter manager
     */
    async initialize() {
        this.isInitializing = true;
        
        try {
            // Load initial data
            await this.loadInitialData();
            
            // Set up event listeners for buttons
            this.setupButtonEventListeners();
            
            // Get current state and handle initial URL parameters
            const currentState = this.urlStateManager.getState();
            await this.handleInitialState(currentState);
            
        } catch (error) {
            console.error('❌ SimpleFilterManager: Initialization failed:', error);
        } finally {
            this.isInitializing = false;
        }
    }
    
    /**
     * Load initial data for filters
     */
    async loadInitialData() {
        try {
            // Get current database from URL
            const urlParams = new URLSearchParams(window.location.search);
            const database = urlParams.get('database') || 'db_sim';
            
            if (this.mode === 'team') {
                // Load teams for team mode
                const teamsResponse = await fetch(`/team/get_teams?database=${database}`);
                if (teamsResponse.ok) {
                    this.availableData.teams = await teamsResponse.json();
                    this.populateTeamDropdown();
                }
            } else {
                // Load leagues and seasons for league mode
                const [leaguesResponse, seasonsResponse] = await Promise.all([
                    fetch(`/league/get_available_leagues?database=${database}`),
                    fetch(`/league/get_available_seasons?database=${database}`)
                ]);
                
                if (leaguesResponse.ok) {
                    this.availableData.leagues = await leaguesResponse.json();
                    this.populateLeagueButtons();
                }
                
                if (seasonsResponse.ok) {
                    this.availableData.seasons = await seasonsResponse.json();
                    this.populateSeasonButtons();
                }
            }
            
        } catch (error) {
            console.error('❌ SimpleFilterManager: Failed to load initial data:', error);
        }
    }
    
    /**
     * Handle initial state from URL parameters
     */
    async handleInitialState(state) {
        
        let stateChanged = false;
        
        if (this.mode === 'league') {
            // Auto-selection logic (only run once)
            if (!this.hasAutoSelected) {
                // For league mode, if no league is selected, auto-select latest season to show season league standings
                if (!state.league && !state.season && this.availableData.seasons && this.availableData.seasons.length > 0) {
                    // Auto-select the latest season to show season league standings view
                    const latestSeason = this.availableData.seasons[this.availableData.seasons.length - 1]; // Last season is usually the latest
                    state.season = latestSeason;
                    stateChanged = true;
                    
                    // Update URL with latest season
                    this.urlStateManager.setState({ ...state, season: latestSeason });
                    this.hasAutoSelected = true;
                }
                // For league mode, set default league to "BayL" if no league is selected but season is selected
                else if (!state.league && this.availableData.leagues && this.availableData.leagues.length > 0) {
                    const defaultLeague = this.availableData.leagues.find(league => league === 'BayL') || this.availableData.leagues[0];
                    state.league = defaultLeague;
                    stateChanged = true;
                    
                    // Update URL with default league
                    this.urlStateManager.setState({ ...state, league: defaultLeague });
                    this.hasAutoSelected = true;
                }
            }
            
            // Load dependent data based on current state
            if (state.league) {
                // League selected - load seasons for this league
                await this.updateSeasonsForLeague(state.league);
                await this.populateSeasonButtonsPreservingSelection(state);
                
                if (state.season) {
                    // League and season available - load weeks and teams
                    await this.updateWeeksForLeagueSeason(state.league, state.season);
                    await this.populateWeekButtons(state);
                    await this.updateTeamsForLeagueSeason(state.league, state.season);
                    await this.populateTeamButtons(state);
                }
            } else if (state.season) {
                // Only season selected - load all seasons first, then populate season buttons for season league standings view
                await this.loadAllSeasons();
                await this.populateSeasonButtonsPreservingSelection(state);
            } else {
                // No league and no season - load all seasons for initial display
                await this.loadAllSeasons();
                await this.populateSeasonButtonsPreservingSelection(state);
            }
        } else if (this.mode === 'team') {
            // Team mode initialization
            if (state.team) {
                // Team selected - load seasons for this team
                await this.updateSeasonsForTeam(state.team);
                await this.populateSeasonButtonsPreservingSelection(state);
                
                if (state.season) {
                    // Team and season available - load weeks
                    await this.updateWeeksForTeamSeason(state.team, state.season);
                    await this.populateWeekButtons(state);
                }
            }
        }
    
    // Sync UI to current state
    await this.syncFiltersToState(state);
    this.previousState = { ...state };
    
    // Initialize tracking map with current state values
    this.updateTrackingMap(state);
    
    // Always trigger content rendering for initial state (even if no state changed)
    // This ensures content is rendered when entering with just database parameter
    this.dispatchFilterChangeEvent(state);
}
    
    /**
     * Handle state changes from URL or user interaction
     */
    async handleStateChange(state) {
        
        try {
            // Prevent infinite loops by checking if we're already processing this state
            if (this.isProcessingState) {
                console.log('🔄 SimpleFilterManager: Already processing state change, skipping to prevent infinite loop');
                return;
            }
            
            this.isProcessingState = true;
            
            // Check if database changed
            const databaseChanged = this.previousState.database && 
                                  state.database && 
                                  this.previousState.database !== state.database;
            
            if (databaseChanged) {
                
                // Reset all filters when database changes
                const resetState = {
                    ...state,
                    team: '',
                    season: '',
                    week: '',
                    league: ''
                };
                
                // Update URL state with reset filters
                this.urlStateManager.setState(resetState);
                
                // Reload teams for the new database
                await this.loadInitialData();
                
                // Sync UI to reset state
                await this.syncFiltersToState(resetState);
                
                // Store reset state as previous
                this.previousState = { ...resetState };
            } else {
                if (this.mode === 'team') {
                    // Team mode logic
                    const teamChanged = this.previousState.team !== state.team;
                    const seasonChanged = this.previousState.season !== state.season;
                    
                    if (teamChanged) {
                        if (state.team) {
                            // Team changed to a specific value - update seasons
                            await this.updateSeasonsForTeam(state.team);
                            await this.updateSeasonButtonsIfChanged(state);
                        } else {
                            // Team deselected - preserve season if still valid, reset dependent buttons
                            await this.populateSeasonButtonsPreservingSelection(state);
                            await this.populateWeekButtons(state);
                        }
                    } else if (seasonChanged) {
                        if (state.team && state.season) {
                            // Season changed to a specific value - update weeks
                            await this.updateWeeksForTeamSeason(state.team, state.season);
                            await this.updateWeekButtonsIfChanged(state);
                        } else if (state.team && !state.season) {
                            // Season deselected but team still selected - reset weeks for team
                            await this.populateWeekButtons(state);
                        }
                    }
                } else {
                    // League mode logic
                    const leagueChanged = this.previousState.league !== state.league;
                    const seasonChanged = this.previousState.season !== state.season;
                    const weekChanged = this.previousState.week !== state.week;
                    
                    if (leagueChanged) {
                        if (state.league) {
                            // League changed to a specific value - update seasons for this league
                            await this.updateSeasonsForLeague(state.league);
                            await this.populateSeasonButtonsPreservingSelection(state);
                        } else {
                            // League deselected - load all seasons first, then preserve season if still valid
                            await this.loadAllSeasons();
                            await this.populateSeasonButtonsPreservingSelection(state);
                            await this.populateWeekButtons(state);
                            await this.populateTeamButtons(state);
                        }
                    } else if (seasonChanged) {
                        if (state.league && state.season) {
                            // Season changed to a specific value - update weeks and teams
                            await this.updateWeeksForLeagueSeason(state.league, state.season);
                            await this.updateWeekButtonsIfChanged(state);
                            await this.updateTeamsForLeagueSeason(state.league, state.season);
                            await this.updateTeamButtonsIfChanged(state);
                        } else if (state.league && !state.season) {
                            // Season deselected but league still selected - reset weeks and teams for league
                            await this.populateWeekButtons(state);
                            await this.populateTeamButtons(state);
                        } else if (!state.league && state.season) {
                            // Season selected but no league - reset weeks and teams
                            await this.populateWeekButtons(state);
                            await this.populateTeamButtons(state);
                        }
                    } else if (weekChanged) {
                        // Week changed - no need to load teams since they're already loaded when season is selected
                    }
                }
                
                // Always sync UI to current state (but don't recreate buttons)
                await this.syncFiltersToState(state);
                this.previousState = { ...state };
            }
            
            // Update tracking map to match current state
            this.updateTrackingMap(state);
            
            // Dispatch filter change event for content rendering
            this.dispatchFilterChangeEvent(state);
            
        } catch (error) {
            console.error('❌ SimpleFilterManager: Error handling state change:', error);
        } finally {
            // Always reset the processing flag
            this.isProcessingState = false;
        }
    }
    
    /**
     * Sync UI filters to match current state
     */
    async syncFiltersToState(state) {
        if (this.mode === 'team') {
            // Update team select
            const teamSelect = document.getElementById('teamSelect');
            if (teamSelect) {
                teamSelect.value = state.team || '';
            }
        } else {
            // Update league buttons
            const leagueButtons = document.querySelectorAll('input[name="league"]');
            leagueButtons.forEach(button => {
                button.checked = button.value === state.league;
            });
            
            // Update team buttons (for league mode)
            const teamButtons = document.querySelectorAll('input[name="team"]');
            teamButtons.forEach(button => {
                button.checked = button.value === state.team;
            });
        }
        
        // Update season buttons (common to both modes)
        const seasonButtons = document.querySelectorAll('input[name="season"]');
        seasonButtons.forEach(button => {
            button.checked = button.value === state.season;
        });
        
        // Update week buttons (common to both modes)
        const weekButtons = document.querySelectorAll('input[name="week"]');
        weekButtons.forEach(button => {
            button.checked = button.value === state.week;
        });
        
        console.log('🔄 SimpleFilterManager: UI synced to state');
    }
    
    /**
     * Update available seasons for a team
     */
    async updateSeasonsForTeam(teamName) {
        if (!teamName) {
            this.availableData.seasons = [];
            return;
        }
        
        try {
            // Get current database from URL
            const urlParams = new URLSearchParams(window.location.search);
            const database = urlParams.get('database') || 'db_sim';
            
            const response = await fetch(`/team/get_available_seasons?team_name=${encodeURIComponent(teamName)}&database=${database}`);
            if (response.ok) {
                this.availableData.seasons = await response.json();
            }
        } catch (error) {
            console.error('❌ SimpleFilterManager: Failed to load seasons:', error);
        }
    }
    
    /**
     * Update available weeks for a team and season
     */
    async updateWeeksForTeamSeason(teamName, season) {
        if (!teamName || !season) {
            this.availableData.weeks = [];
            return;
        }
        
        try {
            // Get current database from URL
            const urlParams = new URLSearchParams(window.location.search);
            const database = urlParams.get('database') || 'db_sim';
            
            const response = await fetch(`/team/get_available_weeks?team_name=${encodeURIComponent(teamName)}&season=${encodeURIComponent(season)}&database=${database}`);
            if (response.ok) {
                this.availableData.weeks = await response.json();
            }
        } catch (error) {
            console.error('❌ SimpleFilterManager: Failed to load weeks:', error);
        }
    }
    
    /**
     * Load all available seasons (when no league is selected)
     */
    async loadAllSeasons() {
        try {
            // Get current database from URL
            const urlParams = new URLSearchParams(window.location.search);
            const database = urlParams.get('database') || 'db_real';
            console.log('🔍 loadAllSeasons: Fetching seasons with database:', database);
            const response = await fetch(`/league/get_available_seasons?database=${database}`);
            console.log('🔍 loadAllSeasons: Response status:', response.status);
            if (response.ok) {
                this.availableData.seasons = await response.json();
                console.log('📊 Loaded all seasons:', this.availableData.seasons);
            } else {
                console.error('❌ loadAllSeasons: Response not ok:', response.status, response.statusText);
            }
        } catch (error) {
            console.error('❌ SimpleFilterManager: Failed to load all seasons:', error);
        }
    }
    
    /**
     * Update available seasons for a league
     */
    async updateSeasonsForLeague(leagueName) {
        if (!leagueName) {
            this.availableData.seasons = [];
            return;
        }
        
        try {
            // Get current database from URL
            const urlParams = new URLSearchParams(window.location.search);
            const database = urlParams.get('database') || 'db_sim';
            // console.info(`####################### updateSeasonsForLeague - leagueName: ${leagueName} and database: ${database}`);
            const response = await fetch(`/league/get_available_seasons?league=${encodeURIComponent(leagueName)}&database=${database}`);
            if (response.ok) {
                this.availableData.seasons = await response.json();
            }
        } catch (error) {
            console.error('❌ SimpleFilterManager: Failed to load seasons for league:', error);
        }
    }
    
    /**
     * Update available weeks for a league and season
     */
    async updateWeeksForLeagueSeason(leagueName, season) {
        if (!leagueName || !season) {
            this.availableData.weeks = [];
            return;
        }
        
        try {
            // Get current database from URL
            const urlParams = new URLSearchParams(window.location.search);
            const database = urlParams.get('database') || 'db_sim';
            
            const response = await fetch(`/league/get_available_weeks?league=${encodeURIComponent(leagueName)}&season=${encodeURIComponent(season)}&database=${database}`);
            if (response.ok) {
                this.availableData.weeks = await response.json();
            }
        } catch (error) {
            console.error('❌ SimpleFilterManager: Failed to load weeks for league:', error);
        }
    }
    
    /**
     * Update available teams for a league and season
     */
    async updateTeamsForLeagueSeason(leagueName, season) {
        if (!leagueName || !season) {
            this.availableData.teams = [];
            return;
        }
        
        try {
            // Get current database from URL
            const urlParams = new URLSearchParams(window.location.search);
            const database = urlParams.get('database') || 'db_sim';
            
            const response = await fetch(`/league/get_available_teams?league=${encodeURIComponent(leagueName)}&season=${encodeURIComponent(season)}&database=${database}`);
            if (response.ok) {
                this.availableData.teams = await response.json();
            }
        } catch (error) {
            console.error('❌ SimpleFilterManager: Failed to load teams for league:', error);
        }
    }
    
    /**
     * Populate the team dropdown with available teams
     */
    populateTeamDropdown() {
        const teamSelect = document.getElementById('teamSelect');
        if (!teamSelect) {
            console.warn('SimpleFilterManager: Team select element not found');
            return;
        }
        
        // Clear existing options except the first one (placeholder)
        while (teamSelect.options.length > 1) {
            teamSelect.remove(1);
        }
        
        // Add team options
        this.availableData.teams.forEach(team => {
            const option = document.createElement('option');
            option.value = team;
            option.textContent = team;
            teamSelect.appendChild(option);
        });
        
        console.log(`📊 SimpleFilterManager: Populated team dropdown with ${this.availableData.teams.length} teams`);
    }
    
    /**
     * Populate league buttons with available leagues
     */
    populateLeagueButtons() {
        const container = document.getElementById('buttonsLeague');
        if (!container) {
            console.warn('SimpleFilterManager: League buttons container not found');
            return;
        }
        
        if (!this.availableData.leagues || this.availableData.leagues.length === 0) {
            container.innerHTML = '<span class="text-muted">Keine Ligen verfügbar</span>';
            return;
        }
        
        // Get current state to determine which button should be checked
        const currentState = this.urlStateManager.getState();
        let selectedLeague = currentState.league || '';
        
        // If no league is selected, default to "BayL" or first available league
        if (!selectedLeague) {
            selectedLeague = this.availableData.leagues.find(league => league === 'BayL') || this.availableData.leagues[0];
            console.log(`🏆 No league selected, defaulting to: ${selectedLeague}`);
        }
        
        // Create league buttons
        const buttonsHtml = this.availableData.leagues.map(league => {
            const isChecked = league === selectedLeague;
            
            return `
                <input type="radio" class="btn-check" name="league" id="league_${league}" 
                       value="${league}" ${isChecked ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="league_${league}">${league}</label>
            `;
        }).join('');
        
        container.innerHTML = buttonsHtml;
        console.log(`📊 SimpleFilterManager: Populated league buttons with ${this.availableData.leagues.length} leagues, selected: ${selectedLeague}`);
    }
    
    /**
     * Populate season buttons with available seasons
     */
    async populateSeasonButtons(state) {
        const container = document.getElementById('buttonsSeason');
        if (!container) {
            console.warn('SimpleFilterManager: Season buttons container not found');
            return;
        }
        
        if (!this.availableData.seasons || this.availableData.seasons.length === 0) {
            container.innerHTML = '<span class="text-muted">Keine Saisons verfügbar</span>';
            return;
        }
        
        // Get current state to determine which button should be checked
        const currentState = this.urlStateManager.getState();
        const selectedSeason = currentState.season || '';
        
        // Create season buttons with "All" option
        const buttonsHtml = ['All', ...this.availableData.seasons].map(season => {
            const seasonValue = season === 'All' ? '' : season;
            const isChecked = seasonValue === selectedSeason || (season === 'All' && !selectedSeason);
            
            return `
                <input type="radio" class="btn-check" name="season" id="season_${season}" 
                       value="${seasonValue}" 
                       ${isChecked ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="season_${season}">${season}</label>
            `;
        }).join('');
        
        container.innerHTML = buttonsHtml;
        console.log(`📊 SimpleFilterManager: Populated season buttons with ${this.availableData.seasons.length} seasons, selected: ${selectedSeason}`);
    }
    
    /**
     * Populate season buttons while preserving current selection if still valid
     */
    async populateSeasonButtonsPreservingSelection(state) {
        console.log('🎯 populateSeasonButtonsPreservingSelection called with state:', state);
        const container = document.getElementById('buttonsSeason');
        if (!container) {
            console.warn('SimpleFilterManager: Season buttons container not found');
            return;
        }
        
        if (!this.availableData.seasons || this.availableData.seasons.length === 0) {
            container.innerHTML = '<span class="text-muted">Keine Saisons verfügbar</span>';
            return;
        }
        
        // Get current state to determine which button should be checked
        const currentState = state || this.urlStateManager.getState();
        const selectedSeason = currentState.season || '';
        
        // Check if the currently selected season is still available
        const isSeasonStillValid = !selectedSeason || this.availableData.seasons.includes(selectedSeason);
        
        console.log(`🔍 Season preservation check: selectedSeason="${selectedSeason}", availableSeasons=[${this.availableData.seasons.join(', ')}], isValid=${isSeasonStillValid}`);
        
        // If season is still valid, keep it selected; otherwise, default to "All"
        const seasonToSelect = isSeasonStillValid ? selectedSeason : '';
        
        // Create season buttons with "All" option
        const buttonsHtml = ['All', ...this.availableData.seasons].map(season => {
            const seasonValue = season === 'All' ? '' : season;
            const isChecked = seasonValue === seasonToSelect || (season === 'All' && !seasonToSelect);
            
            return `
                <input type="radio" class="btn-check" name="season" id="season_${season}" 
                       value="${seasonValue}" 
                       ${isChecked ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="season_${season}">${season}</label>
            `;
        }).join('');
        
        container.innerHTML = buttonsHtml;
        
        // If we changed the selection, update the URL state
        if (seasonToSelect !== selectedSeason) {
            const newState = { ...currentState, season: seasonToSelect };
            this.urlStateManager.setState(newState);
            console.log(`📊 SimpleFilterManager: Season selection changed from "${selectedSeason}" to "${seasonToSelect}"`);
        } else {
            console.log(`📊 SimpleFilterManager: Preserved season selection: "${selectedSeason}"`);
        }
    }
    
    /**
     * Populate week buttons with available weeks
     * Only shows weeks if league and season are both selected
     */
    async populateWeekButtons(state) {
        const container = document.getElementById('buttonsWeek');
        if (!container) {
            console.warn('SimpleFilterManager: Week buttons container not found');
            return;
        }
        
        // Get current state to determine prerequisites
        const currentState = state || this.urlStateManager.getState();
        
        // Only show week buttons if league and season are selected
        if (!currentState.league || !currentState.season) {
            container.innerHTML = '<span class="text-muted">Wählen Sie Liga und Saison aus</span>';
            console.log('📊 SimpleFilterManager: Week buttons hidden - prerequisites not met');
            return;
        }
        
        if (!this.availableData.weeks || this.availableData.weeks.length === 0) {
            container.innerHTML = '<span class="text-muted">Keine Wochen verfügbar</span>';
            return;
        }
        
        const selectedWeek = currentState.week || '';
        
        // Create week buttons
        const buttonsHtml = this.availableData.weeks.map(week => {
            const isChecked = week.toString() === selectedWeek;
            
            return `
                <input type="radio" class="btn-check" name="week" id="week_${week}" 
                       value="${week}" ${isChecked ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="week_${week}">${week}</label>
            `;
        }).join('');
        
        container.innerHTML = buttonsHtml;
        console.log(`📊 SimpleFilterManager: Populated week buttons with ${this.availableData.weeks.length} weeks, selected: ${selectedWeek}`);
    }
    
    /**
     * Update season buttons only if the data has changed
     */
    async updateSeasonButtonsIfChanged(state) {
        const container = document.getElementById('buttonsSeason');
        if (!container) {
            console.warn('SimpleFilterManager: Season buttons container not found');
            return;
        }
        
        // Get current button values
        const currentButtons = Array.from(container.querySelectorAll('input[name="season"]'))
            .map(input => input.value)
            .sort();
        
        // Get new data values
        const newData = ['', ...this.availableData.seasons].sort();
        
        // Compare arrays
        const dataChanged = currentButtons.length !== newData.length || 
                           !currentButtons.every((val, index) => val === newData[index]);
        
        if (dataChanged) {
            await this.populateSeasonButtonsPreservingSelection(state);
        } else {
        }
    }
    
    /**
     * Update week buttons only if the data has changed
     */
    async updateWeekButtonsIfChanged(state) {
        const container = document.getElementById('buttonsWeek');
        if (!container) {
            console.warn('SimpleFilterManager: Week buttons container not found');
            return;
        }
        
        // Get current button values
        const currentButtons = Array.from(container.querySelectorAll('input[name="week"]'))
            .map(input => input.value)
            .sort();
        
        // Get new data values
        const newData = this.availableData.weeks.map(w => w.toString()).sort();
        
        // Compare arrays
        const dataChanged = currentButtons.length !== newData.length || 
                           !currentButtons.every((val, index) => val === newData[index]);
        
        if (dataChanged) {
            await this.populateWeekButtons(state);
        } else {
        }
    }
    
    /**
     * Populate team buttons with available teams (for league mode)
     * Only shows teams if league, season, AND week are all selected
     */
    async populateTeamButtons(state) {
        const container = document.getElementById('buttonsTeam');
        if (!container) {
            console.warn('SimpleFilterManager: Team buttons container not found');
            return;
        }
        
        // Get current state to determine prerequisites
        const currentState = state || this.urlStateManager.getState();
        
        // Only show team buttons if league AND season are selected
        if (!currentState.league || !currentState.season) {
            container.innerHTML = '<span class="text-muted">Wählen Sie Liga und Saison aus</span>';
            console.log('📊 SimpleFilterManager: Team buttons hidden - prerequisites not met');
            return;
        }
        
        if (!this.availableData.teams || this.availableData.teams.length === 0) {
            container.innerHTML = '<span class="text-muted">Keine Teams verfügbar</span>';
            return;
        }
        
        const selectedTeam = currentState.team || '';
        
        // Create team buttons
        const buttonsHtml = this.availableData.teams.map(team => {
            const isChecked = team === selectedTeam;
            
            return `
                <input type="radio" class="btn-check" name="team" id="team_${team}" 
                       value="${team}" ${isChecked ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="team_${team}">${team}</label>
            `;
        }).join('');
        
        container.innerHTML = buttonsHtml;
        console.log(`📊 SimpleFilterManager: Populated team buttons with ${this.availableData.teams.length} teams, selected: ${selectedTeam}`);
    }
    
    /**
     * Update team buttons only if the data has changed
     */
    async updateTeamButtonsIfChanged(state) {
        const container = document.getElementById('buttonsTeam');
        if (!container) {
            console.warn('SimpleFilterManager: Team buttons container not found');
            return;
        }
        
        // Get current button values
        const currentButtons = Array.from(container.querySelectorAll('input[name="team"]'))
            .map(input => input.value)
            .sort();
        
        // Get new data values
        const newData = this.availableData.teams.sort();
        
        // Compare arrays
        const dataChanged = currentButtons.length !== newData.length || 
                           !currentButtons.every((val, index) => val === newData[index]);
        
        if (dataChanged) {
            await this.populateTeamButtons(state);
        } else {
        }
    }
    
    /**
     * Set up event listeners for filter buttons
     */
    setupButtonEventListeners() {
        // Use event delegation for all filter buttons
        document.addEventListener('change', (event) => {
            const target = event.target;
            
            if (target.name === 'league') {
                const league = target.value;
                this.selectedButtons.set('league', league);
                this.updateState({ league, season: '', week: '', team: '' });
            } else if (target.name === 'season') {
                const season = target.value;
                this.selectedButtons.set('season', season);
                this.updateState({ season, week: '' });
            } else if (target.name === 'week') {
                const week = target.value;
                this.selectedButtons.set('week', week);
                this.updateState({ week });
            } else if (target.name === 'team') {
                const team = target.value;
                this.selectedButtons.set('team', team);
                this.updateState({ team });
            }
        });
        
        // Add click event listeners for deselection functionality
        document.addEventListener('click', (event) => {
            let target = event.target;
            let radioInput = null;
            
            // Check if clicked element is a label for a radio button
            if (target.tagName === 'LABEL' && target.getAttribute('for')) {
                radioInput = document.getElementById(target.getAttribute('for'));
            } else if (target.type === 'radio') {
                radioInput = target;
            }
            
            // If we found a radio button filter, handle deselection
            if (radioInput && radioInput.type === 'radio' && ['league', 'season', 'week', 'team'].includes(radioInput.name)) {
                const buttonName = radioInput.name;
                const buttonValue = radioInput.value;
                const currentlySelected = this.selectedButtons.get(buttonName);
                
                
                // Check if clicking the same button that was already selected (before the click changes its state)
                if (currentlySelected === buttonValue) {
                    
                    // Prevent the default behavior and uncheck
                    event.preventDefault();
                    event.stopPropagation();
                    radioInput.checked = false;
                    
                    // Update our tracking map
                    this.selectedButtons.delete(buttonName);
                    
                    // Trigger the appropriate state update for deselection
                    if (buttonName === 'league') {
                        this.updateState({ league: '', season: '', week: '', team: '' });
                    } else if (buttonName === 'season') {
                        this.updateState({ season: '', week: '', team: '' });
                    } else if (buttonName === 'week') {
                        this.updateState({ week: '' });
                    } else if (buttonName === 'team') {
                        this.updateState({ team: '' });
                    }
                    
                    // Don't update tracking for selection since we're deselecting
                    return;
                }
                
                // If this is not a deselection, the change event will handle updating the tracking
            }
        });
        
        // Handle team dropdown for team mode
        if (this.mode === 'team') {
            const teamSelect = document.getElementById('teamSelect');
            if (teamSelect) {
                teamSelect.addEventListener('change', (event) => {
                    const team = event.target.value;
                    this.updateState({ team, season: '', week: '' });
                });
            }
        }
        
    }
    
    /**
     * Update state and trigger URL update
     */
    updateState(newState) {
        const currentState = this.urlStateManager.getState();
        const updatedState = { ...currentState, ...newState };
        this.urlStateManager.setState(updatedState);
        
        // Update the tracking map to match the new state
        this.updateTrackingMap(updatedState);
    }
    
    /**
     * Update the tracking map to match the current state
     */
    updateTrackingMap(state) {
        // Clear tracking map and repopulate with current selections
        this.selectedButtons.clear();
        
        if (state.league) this.selectedButtons.set('league', state.league);
        if (state.season) this.selectedButtons.set('season', state.season);
        if (state.week) this.selectedButtons.set('week', state.week);
        if (state.team) this.selectedButtons.set('team', state.team);
    }
    
    /**
     * Dispatch filter change event for content rendering
     */
    dispatchFilterChangeEvent(state) {
        const event = new CustomEvent('filterChange', {
            detail: state,
            bubbles: true
        });
        document.dispatchEvent(event);
        console.log('📢 SimpleFilterManager: Dispatched filterChange event:', state);
    }
    
}

// Make globally available
window.SimpleFilterManager = SimpleFilterManager;
