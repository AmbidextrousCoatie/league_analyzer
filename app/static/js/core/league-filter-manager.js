/**
 * League Filter Manager
 * 
 * Manages filter state for league statistics page
 * Handles league-specific filter hierarchy: Season → League → Week → Team
 */

class LeagueFilterManager {
    constructor(urlStateManager, eventBus = null, smartEventRouter = null) {
        this.urlStateManager = urlStateManager;
        this.eventBus = eventBus || window.EventBus;
        this.smartEventRouter = smartEventRouter;
        
        this.previousState = {};
        this.isInitialized = false;
        
        // League-specific filter data
        this.filterData = {
            seasons: [],
            leagues: {},
            weeks: {},
            teams: {}
        };
        
        // Set up state change listener
        this.urlStateManager.onStateChange = (state) => {
            this.handleStateChange(state);
        };
        
        // Subscribe to relevant events
        this.setupEventListeners();
    }
    
    /**
     * Set up event listeners for league-specific events
     */
    setupEventListeners() {
        if (this.eventBus) {
            // Listen for block lifecycle events
            this.eventBus.subscribe('block-rendering', this.onBlockRendering.bind(this), this);
            this.eventBus.subscribe('block-rendered', this.onBlockRendered.bind(this), this);
            this.eventBus.subscribe('block-error', this.onBlockError.bind(this), this);
        }
    }
    
    /**
     * Initialize the filter manager
     */
    async initialize() {
        if (this.isInitialized) {
            console.log('LeagueFilterManager already initialized');
            return;
        }
        
        try {
            console.log('Initializing LeagueFilterManager...');
            
            // Load initial filter data
            await this.loadSeasonsData();
            await this.loadLeaguesData();
            await this.loadWeeksData();
            await this.loadTeamsData();
            
            // Initialize from URL
            this.urlStateManager.initializeFromUrl();
            
            this.isInitialized = true;
            console.log('✅ LeagueFilterManager initialized successfully');
            
        } catch (error) {
            console.error('❌ Error initializing LeagueFilterManager:', error);
            if (this.eventBus) {
                this.eventBus.emit('filter-manager-error', { error, context: 'initialization' });
            }
            throw error;
        }
    }
    
    /**
     * Handle state changes
     */
    async handleStateChange(state) {
        try {
            console.log('LeagueFilterManager handling state change:', state);
            
            // Detect specific changes and route them
            this.detectAndRouteChanges(state);
            
            // Update filter UI
            await this.updateFilterUI(state);
            
            // Update content
            await this.updateContent(state);
            
            // Store current state as previous
            this.previousState = { ...state };
            
        } catch (error) {
            console.error('❌ Error handling state change:', error);
            if (this.eventBus) {
                this.eventBus.emit('filter-manager-error', { error, state });
            }
        }
    }
    
    /**
     * Detect specific state changes and route them via SmartEventRouter
     */
    detectAndRouteChanges(newState) {
        if (!this.smartEventRouter) return;
        
        const changes = this.detectStateChanges(this.previousState, newState);
        
        console.log('🔍 LeagueFilterManager: Detected changes:', changes);
        
        // Route each change through the smart event router
        changes.forEach(change => {
            this.smartEventRouter.routeFilterChange(change.filterType, {
                filterType: change.filterType,
                oldValue: change.oldValue,
                newValue: change.newValue,
                fullState: newState,
                timestamp: Date.now()
            });
        });
    }
    
    /**
     * Detect what changed between states
     */
    detectStateChanges(oldState, newState) {
        const changes = [];
        const filterTypes = ['team', 'season', 'week', 'league', 'database'];
        
        filterTypes.forEach(filterType => {
            const oldValue = oldState[filterType] || null;
            const newValue = newState[filterType] || null;
            
            if (oldValue !== newValue) {
                changes.push({
                    filterType,
                    oldValue,
                    newValue
                });
            }
        });
        
        return changes;
    }
    
    /**
     * Load seasons data
     */
    async loadSeasonsData() {
        try {
            console.log('Loading seasons data...');
            const response = await fetchWithDatabase('/league/get_available_seasons');
            this.filterData.seasons = await response.json();
            
                            // Update season buttons
                if (typeof updateSeasonButtons === 'function') {
                    updateSeasonButtons();
                }
            
        } catch (error) {
            console.error('❌ Error loading seasons:', error);
            throw error;
        }
    }
    
    /**
     * Load leagues data  
     */
    async loadLeaguesData() {
        try {
            console.log('Loading leagues data...');
            const currentState = this.urlStateManager.parseUrlParams();
            
            if (currentState.season) {
                const response = await fetchWithDatabase(`/league/get_available_leagues?season=${currentState.season}`);
                this.filterData.leagues[currentState.season] = await response.json();
                
                // Update league buttons
                if (typeof updateLeagueButtons === 'function') {
                    updateLeagueButtons();
                }
            }
            
        } catch (error) {
            console.error('❌ Error loading leagues:', error);
            throw error;
        }
    }
    
    /**
     * Load weeks data
     */
    async loadWeeksData() {
        try {
            console.log('Loading weeks data...');
            const currentState = this.urlStateManager.parseUrlParams();
            
            if (currentState.season && currentState.league) {
                const response = await fetchWithDatabase(`/league/get_available_weeks?season=${currentState.season}&league=${currentState.league}`);
                const key = `${currentState.season}-${currentState.league}`;
                this.filterData.weeks[key] = await response.json();
                
                // Update week buttons
                if (typeof updateWeekButtons === 'function') {
                    updateWeekButtons();
                }
            }
            
        } catch (error) {
            console.error('❌ Error loading weeks:', error);
            throw error;
        }
    }
    
    /**
     * Load teams data
     */
    async loadTeamsData() {
        try {
            console.log('Loading teams data...');
            const currentState = this.urlStateManager.parseUrlParams();
            
            if (currentState.season && currentState.league) {
                const response = await fetchWithDatabase(`/league/get_available_teams?season=${currentState.season}&league=${currentState.league}`);
                const key = `${currentState.season}-${currentState.league}`;
                this.filterData.teams[key] = await response.json();
                
                // Update team buttons (league-specific function)
                if (typeof updateLeagueTeamButtons === 'function') {
                    updateLeagueTeamButtons(this.filterData.teams[key]);
                }
            }
            
        } catch (error) {
            console.error('❌ Error loading teams:', error);
            // Don't throw - teams are optional in league context
        }
    }
    
    /**
     * Update filter UI based on current state
     */
    async updateFilterUI(state) {
        try {
            // Update seasons if needed
            if (!this.filterData.seasons.length) {
                await this.loadSeasonsData();
            }
            
            // Update leagues if season is selected
            if (state.season && !this.filterData.leagues[state.season]) {
                await this.loadLeaguesData();
            }
            
            // Update weeks if season and league are selected
            if (state.season && state.league) {
                const key = `${state.season}-${state.league}`;
                if (!this.filterData.weeks[key]) {
                    await this.loadWeeksData();
                }
            }
            
            // Update teams if season and league are selected
            if (state.season && state.league) {
                const key = `${state.season}-${state.league}`;
                if (!this.filterData.teams[key]) {
                    await this.loadTeamsData();
                }
            }
            
            // Update active button states
            this.updateActiveButtons(state);
            
        } catch (error) {
            console.error('❌ Error updating filter UI:', error);
        }
    }
    
    /**
     * Update active button states
     */
    updateActiveButtons(state) {
        // Update season buttons
        document.querySelectorAll('#buttonsSeason .btn').forEach(btn => {
            btn.classList.toggle('active', btn.textContent.trim() === state.season);
        });
        
        // Update league buttons
        document.querySelectorAll('#buttonsLeague .btn').forEach(btn => {
            btn.classList.toggle('active', btn.textContent.trim() === state.league);
        });
        
        // Update week buttons
        document.querySelectorAll('#buttonsWeek .btn').forEach(btn => {
            btn.classList.toggle('active', btn.textContent.trim() === state.week);
        });
        
        // Update team buttons
        document.querySelectorAll('#buttonsTeam .btn').forEach(btn => {
            btn.classList.toggle('active', btn.textContent.trim() === state.team);
        });
    }
    
    /**
     * Update content based on current state (calls legacy functions for now)
     */
    async updateContent(state) {
        try {
            console.log('Updating league content for state:', state);
            
            // In Phase 2, we call legacy functions
            // In Phase 3, this will be replaced with content block coordination
            
            // For now, just log what would be updated
            console.log('Content update would call legacy functions based on state:', state);
            
        } catch (error) {
            console.error('❌ Error updating content:', error);
            if (this.eventBus) {
                this.eventBus.emit('content-update-error', { error, state });
            }
        }
    }
    
    /**
     * Event handlers for block lifecycle
     */
    onBlockRendering(data) {
        console.log('🔄 Block rendering:', data.blockId);
    }
    
    onBlockRendered(data) {
        console.log('✅ Block rendered:', data.blockId);
    }
    
    onBlockError(data) {
        console.error('❌ Block error:', data.blockId, data.error);
    }
    
    /**
     * Get current filter data
     */
    getFilterData() {
        return this.filterData;
    }
    
    /**
     * Debug method
     */
    debug() {
        console.log('=== LeagueFilterManager Debug Info ===');
        console.log('Initialized:', this.isInitialized);
        console.log('Previous State:', this.previousState);
        console.log('Current State:', this.urlStateManager.parseUrlParams());
        console.log('Filter Data:', this.filterData);
        console.log('Event Bus:', !!this.eventBus);
        console.log('Smart Event Router:', !!this.smartEventRouter);
    }
}

// Make LeagueFilterManager globally available
window.LeagueFilterManager = LeagueFilterManager;