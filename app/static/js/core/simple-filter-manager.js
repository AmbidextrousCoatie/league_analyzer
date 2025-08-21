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
        this.previousState = {};
        this.availableData = {
            teams: [],
            seasons: [],
            weeks: [],
            leagues: []
        };
        
        // Listen for state changes from URL manager
        this.urlStateManager.onStateChange((state) => {
            this.handleStateChange(state);
        });
    }
    
    /**
     * Initialize the filter manager
     */
    async initialize() {
        console.log('🔧 SimpleFilterManager: Initializing...');
        this.isInitializing = true;
        
        try {
            // Load initial data
            await this.loadInitialData();
            
            // Set up event listeners for buttons
            this.setupButtonEventListeners();
            
            // Get current state and handle initial URL parameters
            const currentState = this.urlStateManager.getState();
            await this.handleInitialState(currentState);
            
            console.log('✅ SimpleFilterManager: Initialized successfully');
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
            
            console.log(`📊 SimpleFilterManager: Loaded initial data for ${this.mode} mode, database: ${database}`);
        } catch (error) {
            console.error('❌ SimpleFilterManager: Failed to load initial data:', error);
        }
    }
    
    /**
     * Handle initial state from URL parameters
     */
    async handleInitialState(state) {
        console.log('🔄 SimpleFilterManager: Handling initial state:', state);
        
        let stateChanged = false;
        
        if (this.mode === 'league') {
            // For league mode, set default league to "BayL" if no league is selected
            if (!state.league && this.availableData.leagues && this.availableData.leagues.length > 0) {
                const defaultLeague = this.availableData.leagues.find(league => league === 'BayL') || this.availableData.leagues[0];
                console.log(`🏆 Setting default league to: ${defaultLeague}`);
                state.league = defaultLeague;
                stateChanged = true;
                
                // Update URL with default league
                this.urlStateManager.setState({ ...state, league: defaultLeague });
            }
            
            // Load dependent data based on current state
            if (state.league && !state.season) {
                // League selected but no season - load seasons for this league
                await this.updateSeasonsForLeague(state.league);
                await this.populateSeasonButtons();
            }
            
            if (state.league && state.season && !state.week) {
                // League and season selected but no week - load weeks
                await this.updateWeeksForLeagueSeason(state.league, state.season);
                await this.populateWeekButtons();
            }
            
            if (state.league && state.season && !state.team) {
                // League and season selected but no team - load teams
                await this.updateTeamsForLeagueSeason(state.league, state.season);
                await this.populateTeamButtons();
            }
        }
        
        // Sync UI to current state
        await this.syncFiltersToState(state);
        this.previousState = { ...state };
        
        // Always trigger content rendering for initial state (even if no state changed)
        // This ensures content is rendered when entering with just database parameter
        console.log('🔄 SimpleFilterManager: Triggering initial content rendering');
        this.dispatchFilterChangeEvent(state);
    }
    
    /**
     * Handle state changes from URL or user interaction
     */
    async handleStateChange(state) {
        console.log('🔄 SimpleFilterManager: State changed:', state);
        
        try {
            // Check if database changed
            const databaseChanged = this.previousState.database && 
                                  state.database && 
                                  this.previousState.database !== state.database;
            
            if (databaseChanged) {
                console.log(`🔄 SimpleFilterManager: Database changed from ${this.previousState.database} to ${state.database}, resetting filters`);
                
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
                    
                    if (teamChanged && state.team) {
                        // Team changed - update seasons
                        await this.updateSeasonsForTeam(state.team);
                        await this.updateSeasonButtonsIfChanged(state);
                    } else if (seasonChanged && state.team && state.season) {
                        // Season changed - update weeks
                        await this.updateWeeksForTeamSeason(state.team, state.season);
                        await this.updateWeekButtonsIfChanged(state);
                    }
                } else {
                    // League mode logic
                    const leagueChanged = this.previousState.league !== state.league;
                    const seasonChanged = this.previousState.season !== state.season;
                    
                    if (leagueChanged && state.league) {
                        // League changed - update seasons for this league
                        await this.updateSeasonsForLeague(state.league);
                        await this.updateSeasonButtonsIfChanged(state);
                    } else if (seasonChanged && state.league && state.season) {
                        // Season changed - update weeks and teams
                        await this.updateWeeksForLeagueSeason(state.league, state.season);
                        await this.updateTeamsForLeagueSeason(state.league, state.season);
                        await this.updateWeekButtonsIfChanged(state);
                        await this.updateTeamButtonsIfChanged(state);
                    }
                }
                
                // Always sync UI to current state (but don't recreate buttons)
                await this.syncFiltersToState(state);
                this.previousState = { ...state };
            }
            
            // Dispatch filter change event for content rendering
            this.dispatchFilterChangeEvent(state);
            
        } catch (error) {
            console.error('❌ SimpleFilterManager: Error handling state change:', error);
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
     * Populate week buttons with available weeks
     */
    async populateWeekButtons(state) {
        const container = document.getElementById('buttonsWeek');
        if (!container) {
            console.warn('SimpleFilterManager: Week buttons container not found');
            return;
        }
        
        if (!this.availableData.weeks || this.availableData.weeks.length === 0) {
            container.innerHTML = '<span class="text-muted">Keine Wochen verfügbar</span>';
            return;
        }
        
        // Get current state to determine which button should be checked
        const currentState = this.urlStateManager.getState();
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
            console.log('📊 SimpleFilterManager: Season data changed, updating buttons');
            await this.populateSeasonButtons(state);
        } else {
            console.log('📊 SimpleFilterManager: Season data unchanged, skipping button update');
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
            console.log('📊 SimpleFilterManager: Week data changed, updating buttons');
            await this.populateWeekButtons(state);
        } else {
            console.log('📊 SimpleFilterManager: Week data unchanged, skipping button update');
        }
    }
    
    /**
     * Populate team buttons with available teams (for league mode)
     */
    async populateTeamButtons(state) {
        const container = document.getElementById('buttonsTeam');
        if (!container) {
            console.warn('SimpleFilterManager: Team buttons container not found');
            return;
        }
        
        if (!this.availableData.teams || this.availableData.teams.length === 0) {
            container.innerHTML = '<span class="text-muted">Keine Teams verfügbar</span>';
            return;
        }
        
        // Get current state to determine which button should be checked
        const currentState = this.urlStateManager.getState();
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
            console.log('📊 SimpleFilterManager: Team data changed, updating buttons');
            await this.populateTeamButtons(state);
        } else {
            console.log('📊 SimpleFilterManager: Team data unchanged, skipping button update');
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
                console.log('🏆 League changed:', league);
                this.updateState({ league, season: '', week: '', team: '' });
            } else if (target.name === 'season') {
                const season = target.value;
                console.log('📅 Season changed:', season);
                this.updateState({ season, week: '' });
            } else if (target.name === 'week') {
                const week = target.value;
                console.log('📆 Week changed:', week);
                this.updateState({ week });
            } else if (target.name === 'team') {
                const team = target.value;
                console.log('🏢 Team changed:', team);
                this.updateState({ team });
            }
        });
        
        // Handle team dropdown for team mode
        if (this.mode === 'team') {
            const teamSelect = document.getElementById('teamSelect');
            if (teamSelect) {
                teamSelect.addEventListener('change', (event) => {
                    const team = event.target.value;
                    console.log('🏢 Team dropdown changed:', team);
                    this.updateState({ team, season: '', week: '' });
                });
            }
        }
        
        console.log('✅ SimpleFilterManager: Button event listeners set up');
    }
    
    /**
     * Update state and trigger URL update
     */
    updateState(newState) {
        const currentState = this.urlStateManager.getState();
        const updatedState = { ...currentState, ...newState };
        this.urlStateManager.setState(updatedState);
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
