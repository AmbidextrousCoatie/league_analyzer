/**
 * Filter Manager
 * 
 * Manages filter state coordination and cascading updates
 * Calls existing legacy functions while adding state management
 */

class FilterManager {
    constructor(urlStateManager) {
        this.urlStateManager = urlStateManager;
        this.isInitializing = false;
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
     * Handle state changes from URL or user interaction
     */
    async handleStateChange(state) {
        console.log('FilterManager handling state change:', state);
        
        try {
            // Update UI filters to match state
            await this.syncFiltersToState(state);
            
            // Update content based on current state
            this.updateContent(state);
            
        } catch (error) {
            console.error('Error handling state change:', error);
        }
    }
    
    /**
     * Sync UI filters to match current state
     */
    async syncFiltersToState(state) {
        // Update team selection
        if (state.team) {
            const teamSelect = document.getElementById('teamSelect');
            if (teamSelect && teamSelect.value !== state.team) {
                // Load teams if not already loaded
                if (this.availableData.teams.length === 0) {
                    await this.loadTeamsData();
                }
                teamSelect.value = state.team;
                
                // Load seasons for this team
                await this.loadSeasonsData(state.team);
            }
        }
        
        // Update season selection
        if (state.season) {
            const seasonInput = document.querySelector(`input[name="season"][value="${state.season}"]`);
            if (seasonInput && !seasonInput.checked) {
                seasonInput.checked = true;
                
                // Load weeks for this team/season
                if (state.team) {
                    await this.loadWeeksData(state.team, state.season);
                }
            }
        } else {
            // Select "All" season by default
            const allSeasonInput = document.querySelector('input[name="season"][value=""]');
            if (allSeasonInput && !allSeasonInput.checked) {
                allSeasonInput.checked = true;
            }
        }
        
        // Update week selection
        if (state.week) {
            const weekInput = document.querySelector(`input[name="week"][value="${state.week}"]`);
            if (weekInput && !weekInput.checked) {
                weekInput.checked = true;
            }
        }
        
        // Update message visibility
        this.updateMessageVisibility(state);
    }
    
    /**
     * Load teams data using existing function
     */
    async loadTeamsData() {
        try {
            const response = await fetch('/team/get_teams');
            const teams = await response.json();
            this.availableData.teams = teams;
            
            // Use existing function to populate dropdown
            updateTeamSelect(teams);
            
            return teams;
        } catch (error) {
            console.error('Error loading teams:', error);
            return [];
        }
    }
    
    /**
     * Load seasons data using existing function
     */
    async loadSeasonsData(teamName) {
        try {
            const response = await fetch(`/team/get_available_seasons?team_name=${teamName}`);
            const seasons = await response.json();
            this.availableData.seasons = seasons;
            
            // Use existing function to populate buttons
            updateSeasonButtons(teamName);
            
            return seasons;
        } catch (error) {
            console.error('Error loading seasons:', error);
            return [];
        }
    }
    
    /**
     * Load weeks data using existing function
     */
    async loadWeeksData(teamName, season) {
        try {
            const response = await fetch(`/team/get_available_weeks?team_name=${teamName}&season=${season}`);
            const weeks = await response.json();
            this.availableData.weeks = weeks;
            
            // Use existing function to populate buttons
            updateWeekButtons(teamName, season);
            
            return weeks;
        } catch (error) {
            console.error('Error loading weeks:', error);
            return [];
        }
    }
    
    /**
     * Update content based on current state
     */
    updateContent(state) {
        console.log('Updating content for state:', state);
        
        // Call existing legacy functions based on state
        if (state.team) {
            // Team selected - show team-specific content
            updateTeamHistory(state.team);
            updateLeagueComparison(state.team);
            
            if (state.season && state.season !== '') {
                // Team + specific season selected
                updateClutchAnalysis(state.team, state.season);
                updateConsistencyMetrics(state.team, state.season);
                loadSpecialMatchesForSeason(state.team, state.season);
            } else {
                // Team only selected (all seasons)
                updateClutchAnalysis(state.team, null);
                updateConsistencyMetrics(state.team, null);
                loadSpecialMatches(state.team);
            }
        } else {
            // No team selected - show all teams overview
            updateAllTeamsStats();
        }
    }
    
    /**
     * Update message visibility based on state
     */
    updateMessageVisibility(state) {
        const message = document.getElementById('selectionMessage');
        if (message) {
            if (state.team) {
                message.style.display = 'none';
            } else {
                message.style.display = 'block';
            }
        }
    }
    
    /**
     * Handle team selection change
     */
    async handleTeamChange(teamName) {
        console.log('Team changed to:', teamName);
        
        if (teamName) {
            // Clear dependent filters when team changes
            const newState = {
                team: teamName,
                season: '',
                week: ''
            };
            
            this.urlStateManager.setState(newState);
            
            // Load seasons for new team
            await this.loadSeasonsData(teamName);
        } else {
            // No team selected
            this.urlStateManager.setState({
                team: '',
                season: '',
                week: ''
            });
        }
    }
    
    /**
     * Handle season selection change
     */
    async handleSeasonChange(season) {
        console.log('Season changed to:', season);
        
        const currentState = this.urlStateManager.getState();
        
        if (currentState.team) {
            const newState = {
                season: season,
                week: '' // Clear week when season changes
            };
            
            this.urlStateManager.setState(newState);
            
            // Load weeks for this team/season combination
            if (season && season !== '') {
                await this.loadWeeksData(currentState.team, season);
            }
        }
    }
    
    /**
     * Handle week selection change
     */
    handleWeekChange(week) {
        console.log('Week changed to:', week);
        
        this.urlStateManager.setState({
            week: week
        });
    }
    
    /**
     * Initialize filter manager
     */
    async initialize() {
        this.isInitializing = true;
        
        try {
            // Load initial teams data
            await this.loadTeamsData();
            
            // Setup event listeners for filter changes
            this.setupEventListeners();
            
            // Initialize from URL state
            this.urlStateManager.initializeFromUrl();
            
        } catch (error) {
            console.error('Error initializing FilterManager:', error);
        } finally {
            this.isInitializing = false;
        }
    }
    
    /**
     * Setup event listeners for filter UI elements
     */
    setupEventListeners() {
        // Team select dropdown
        const teamSelect = document.getElementById('teamSelect');
        if (teamSelect) {
            teamSelect.addEventListener('change', (event) => {
                if (!this.isInitializing) {
                    this.handleTeamChange(event.target.value);
                }
            });
        }
        
        // Season buttons (delegated event handling)
        document.addEventListener('change', (event) => {
            if (event.target.name === 'season' && !this.isInitializing) {
                this.handleSeasonChange(event.target.value);
            }
        });
        
        // Week buttons (delegated event handling)
        document.addEventListener('change', (event) => {
            if (event.target.name === 'week' && !this.isInitializing) {
                this.handleWeekChange(event.target.value);
            }
        });
    }
}

// Make FilterManager globally available
window.FilterManager = FilterManager;