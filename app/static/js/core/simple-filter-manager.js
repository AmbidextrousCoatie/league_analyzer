/**
 * Simple Filter Manager
 * 
 * Simplified version without complex event bus system
 * Just manages filter state and UI synchronization
 */

class SimpleFilterManager {
    constructor(urlStateManager) {
        this.urlStateManager = urlStateManager;
        this.isInitializing = false;
        this.previousState = {};
        this.availableData = {
            teams: [],
            seasons: [],
            weeks: []
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
            
            // Sync UI to current state
            const currentState = this.urlStateManager.getState();
            await this.syncFiltersToState(currentState);
            
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
            
            // Load teams for the current database
            const teamsResponse = await fetch(`/team/get_teams?database=${database}`);
            if (teamsResponse.ok) {
                this.availableData.teams = await teamsResponse.json();
                
                // Populate team dropdown
                this.populateTeamDropdown();
            }
            
            console.log(`📊 SimpleFilterManager: Loaded initial data for database: ${database}`);
        } catch (error) {
            console.error('❌ SimpleFilterManager: Failed to load initial data:', error);
        }
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
                // Normal state change - just sync UI
                await this.syncFiltersToState(state);
                this.previousState = { ...state };
            }
            
        } catch (error) {
            console.error('❌ SimpleFilterManager: Error handling state change:', error);
        }
    }
    
    /**
     * Sync UI filters to match current state
     */
    async syncFiltersToState(state) {
        // Update team select
        const teamSelect = document.getElementById('teamSelect');
        if (teamSelect) {
            teamSelect.value = state.team || '';
        }
        
        // Update season buttons
        const seasonButtons = document.querySelectorAll('input[name="season"]');
        seasonButtons.forEach(button => {
            button.checked = button.value === state.season;
        });
        
        // Update week buttons
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
}

// Make globally available
window.SimpleFilterManager = SimpleFilterManager;
