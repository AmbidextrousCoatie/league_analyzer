/**
 * API Test Application
 * 
 * Main coordinator for API testing page
 * Uses content block architecture similar to TeamStatsApp and LeagueStatsApp
 */

class APITestApp {
    constructor() {
        this.urlStateManager = null;
        this.filterManager = null;
        this.contentRenderer = null;
        this.eventBus = null;
        this.isInitialized = false;
        this.initializationPromise = null;
        
        // Current state for API testing
        this.currentState = {
            database: '',
            season: '',
            league: '',
            week: '',
            team: '',
            player: ''
        };
    }
    
    async initialize() {
        if (this.isInitialized) {
            console.log('APITestApp already initialized');
            return this.initializationPromise;
        }
        
        if (this.initializationPromise) {
            console.log('APITestApp initialization in progress');
            return this.initializationPromise;
        }
        
        console.log('Initializing APITestApp...');
        
        this.initializationPromise = this._doInitialize();
        return this.initializationPromise;
    }
    
    async _doInitialize() {
        try {
            // Initialize URL state manager with API test parameters
            this.urlStateManager = new URLStateManager({
                onStateChange: (state) => {
                    console.log('API Test URL state changed:', state);
                    this.currentState = { ...this.currentState, ...state };
                    
                    // Update global currentState for legacy compatibility
                    if (typeof window.currentState !== 'undefined') {
                        Object.assign(window.currentState, state);
                    } else {
                        window.currentState = { ...this.currentState };
                    }
                    
                    if (this.contentRenderer) {
                        this.contentRenderer.renderContent(this.currentState);
                    }
                    
                    // Update filter controls
                    this.updateFilterDisplays();
                }
            });
            
            // Get initial state from URL
            this.currentState = { ...this.currentState, ...this.urlStateManager.getState() };
            window.currentState = { ...this.currentState };
            
            // Initialize content renderer
            this.contentRenderer = new APITestContentRenderer(this.urlStateManager);
            
            // Load initial filter options
            await this.loadInitialData();
            
            // Render initial content
            await this.contentRenderer.renderContent(this.currentState);
            
            // Setup filter event listeners
            this.setupFilterEventListeners();
            
            this.isInitialized = true;
            console.log('✅ APITestApp initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize APITestApp:', error);
            throw error;
        }
    }
    
    /**
     * Load initial data for filters
     */
    async loadInitialData() {
        try {
            // Load available seasons
            const seasons = await this.fetchData('/league/get_available_seasons');
            this.updateSeasonOptions(seasons);
            
            // Load available leagues (all)
            const leagues = await this.fetchData('/league/get_available_leagues');
            this.updateLeagueOptions(leagues);
            
            // If we have initial season and league from URL, load dependent data
            if (this.currentState.season && this.currentState.league) {
                console.log('Loading initial dependent data for:', this.currentState);
                await this.updateWeekOptions();
                await this.updateTeamOptions();
            }
            
            // Select initial values from URL state
            this.selectInitialValues();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }
    
    /**
     * Fetch data from API
     */
    async fetchData(endpoint, params = {}) {
        const url = new URL(endpoint, window.location.origin);
        Object.entries(params).forEach(([key, value]) => {
            if (value) url.searchParams.append(key, value);
        });
        
        const response = await fetchWithDatabase(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    /**
     * Update season options
     */
    updateSeasonOptions(seasons) {
        const container = document.getElementById('seasonSelector');
        if (!container) return;
        
        const options = ['All', ...seasons];
        container.innerHTML = options.map(season => `
            <input type="radio" class="btn-check" name="season" id="season_${season}" 
                   value="${season === 'All' ? '' : season}">
            <label class="btn btn-outline-primary" for="season_${season}">${season}</label>
        `).join('');
        
        // Select "All" by default
        const allOption = container.querySelector('input[value=""]');
        if (allOption) allOption.checked = true;
    }
    
    /**
     * Update league options
     */
    updateLeagueOptions(leagues) {
        const container = document.getElementById('leagueSelector');
        if (!container) return;
        
        container.innerHTML = leagues.map(league => `
            <input type="radio" class="btn-check" name="league" id="league_${league}" 
                   value="${league}">
            <label class="btn btn-outline-primary" for="league_${league}">${league}</label>
        `).join('');
    }
    
    /**
     * Update week options
     */
    async updateWeekOptions() {
        const container = document.getElementById('weekSelector');
        if (!container) {
            console.warn('Week selector container not found');
            return;
        }
        
        console.log('Updating week options for:', { season: this.currentState.season, league: this.currentState.league });
        
        if (!this.currentState.season || !this.currentState.league) {
            container.innerHTML = '<span class="text-muted">Select season and league first</span>';
            return;
        }
        
        try {
            container.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm" role="status"></div></div>';
            
            const weeks = await this.fetchData('/league/get_available_weeks', {
                season: this.currentState.season,
                league: this.currentState.league
            });
            
            console.log('Loaded weeks:', weeks);
            
            container.innerHTML = weeks.map(week => `
                <input type="radio" class="btn-check" name="week" id="week_${week}" 
                       value="${week}">
                <label class="btn btn-outline-primary" for="week_${week}">${week}</label>
            `).join('');
            
        } catch (error) {
            console.error('Error loading weeks:', error);
            container.innerHTML = '<span class="text-danger">Error loading weeks</span>';
        }
    }
    
    /**
     * Update team options
     */
    async updateTeamOptions() {
        const container = document.getElementById('teamSelector');
        if (!container) return;
        
        if (!this.currentState.season || !this.currentState.league) {
            container.innerHTML = '<span class="text-muted">Select season and league first</span>';
            return;
        }
        
        try {
            const teams = await this.fetchData('/team/get_teams', {
                season: this.currentState.season,
                league: this.currentState.league
            });
            
            container.innerHTML = teams.map(team => `
                <input type="radio" class="btn-check" name="team" id="team_${team}" 
                       value="${team}">
                <label class="btn btn-outline-primary" for="team_${team}">${team}</label>
            `).join('');
            
        } catch (error) {
            console.error('Error loading teams:', error);
            container.innerHTML = '<span class="text-danger">Error loading teams</span>';
        }
    }
    
    /**
     * Setup filter event listeners
     */
    setupFilterEventListeners() {
        document.addEventListener('change', async (event) => {
            const { name, value } = event.target;
            
            console.log('Filter changed:', { name, value });
            
            if (['season', 'league', 'week', 'team', 'player'].includes(name)) {
                const oldValue = this.currentState[name];
                this.currentState[name] = value;
                
                console.log('Updated state:', this.currentState);
                
                // Update URL state
                this.urlStateManager.setState({ [name]: value });
                
                // Update dependent filters
                if (name === 'season' || name === 'league') {
                    console.log(`${name} changed from '${oldValue}' to '${value}', updating dependent filters...`);
                    
                    // Clear dependent selections first
                    if (name === 'season') {
                        this.clearSelection('league');
                        this.clearSelection('week');
                        this.clearSelection('team');
                    } else if (name === 'league') {
                        this.clearSelection('week');
                        this.clearSelection('team');
                    }
                    
                    // Then update options
                    await this.updateWeekOptions();
                    await this.updateTeamOptions();
                }
                
                // Re-render content
                if (this.contentRenderer) {
                    await this.contentRenderer.renderContent(this.currentState);
                }
            }
        });
    }
    
    /**
     * Clear a filter selection
     */
    clearSelection(filterName) {
        this.currentState[filterName] = '';
        
        const radios = document.querySelectorAll(`input[name="${filterName}"]`);
        radios.forEach(radio => radio.checked = false);
    }
    
    /**
     * Select initial values from URL state
     */
    selectInitialValues() {
        console.log('Selecting initial values:', this.currentState);
        
        ['season', 'league', 'week', 'team'].forEach(filterName => {
            const value = this.currentState[filterName];
            if (value) {
                const input = document.querySelector(`input[name="${filterName}"][value="${value}"]`);
                if (input) {
                    input.checked = true;
                    console.log(`Selected ${filterName}: ${value}`);
                } else {
                    console.warn(`Could not find input for ${filterName}: ${value}`);
                }
            }
        });
        
        // Update filter displays
        this.updateFilterDisplays();
    }
    
    /**
     * Update filter displays
     */
    updateFilterDisplays() {
        // Update any displays that show current filter state
        const filterDisplays = document.querySelectorAll('.current-filters .filter-display');
        filterDisplays.forEach(display => {
            const filters = ['database', 'season', 'league', 'week', 'team'];
            const activeFilters = filters.filter(filter => this.currentState[filter]);
            
            if (activeFilters.length === 0) {
                display.innerHTML = '<span class="text-muted">No filters selected</span>';
            } else {
                display.innerHTML = activeFilters
                    .map(filter => `
                        <span class="badge bg-secondary me-1">
                            ${filter}: ${this.currentState[filter]}
                        </span>
                    `).join('');
            }
        });
    }
    
    /**
     * Get current state
     */
    getCurrentState() {
        return { ...this.currentState };
    }
    
    /**
     * Debug function
     */
    debug() {
        console.log('=== API Test App Debug ===');
        console.log('Current State:', this.currentState);
        console.log('URL State Manager:', this.urlStateManager);
        console.log('Content Renderer:', this.contentRenderer);
        console.log('Initialized:', this.isInitialized);
    }
}

/**
 * API Test Content Renderer
 * 
 * Specialized content renderer for API testing
 */
class APITestContentRenderer {
    constructor(urlStateManager) {
        this.urlStateManager = urlStateManager;
        this.contentBlocks = {};
        this.lastRenderedState = {};
        this.isRendering = false;
        
        // Initialize content blocks
        this.initializeContentBlocks();
    }
    
    /**
     * Initialize content blocks
     */
    initializeContentBlocks() {
        console.log('Initializing API test content blocks...');
        
        try {
            this.contentBlocks['route-test'] = new RouteTestBlock();
            console.log('RouteTestBlock initialized');
        } catch (error) {
            console.error('Failed to initialize RouteTestBlock:', error);
        }
        
        try {
            this.contentBlocks['response-display'] = new ResponseDisplayBlock();
            console.log('ResponseDisplayBlock initialized');
        } catch (error) {
            console.error('Failed to initialize ResponseDisplayBlock:', error);
        }
    }
    
    /**
     * Render content based on current state
     */
    async renderContent(state) {
        if (this.isRendering) {
            console.log('Already rendering, skipping...');
            return;
        }
        
        this.isRendering = true;
        
        try {
            console.log('API Test rendering content for state:', state);
            
            // Render all available blocks
            const renderPromises = Object.values(this.contentBlocks).map(async (block) => {
                try {
                    if (block.canRender(state)) {
                        console.log(`Rendering block: ${block.id}`);
                        await block.render(null, state);
                    } else {
                        console.log(`Block ${block.id} cannot render with current state`);
                    }
                } catch (error) {
                    console.error(`Error rendering block ${block.id}:`, error);
                }
            });
            
            await Promise.all(renderPromises);
            
            this.lastRenderedState = { ...state };
            console.log('✅ API Test content rendering complete');
            
        } catch (error) {
            console.error('❌ Error during API test content rendering:', error);
        } finally {
            this.isRendering = false;
        }
    }
    
    /**
     * Get a specific content block
     */
    getContentBlock(blockId) {
        return this.contentBlocks[blockId];
    }
}