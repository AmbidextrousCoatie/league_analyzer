/**
 * Team Stats Application
 * 
 * Main coordinator that orchestrates state management and content rendering
 * Ensures proper connection between UI events and content blocks
 */

class TeamStatsApp {
    constructor() {
        this.urlStateManager = null;
        this.filterManager = null;
        this.contentRenderer = null;
        this.isInitialized = false;
        this.initializationPromise = null;
    }
    
    async initialize() {
        if (this.isInitialized) {
            console.log('TeamStatsApp already initialized');
            return this.initializationPromise;
        }
        
        if (this.initializationPromise) {
            console.log('TeamStatsApp initialization in progress');
            return this.initializationPromise;
        }
        
        console.log('Initializing TeamStatsApp...');
        
        this.initializationPromise = this._doInitialize();
        return this.initializationPromise;
    }
    
    async _doInitialize() {
        try {
            // Signal that we're taking control to prevent legacy conflicts
            window.teamStatsApp = this;
            this.isInitialized = true;
            
            // Initialize URL state manager with content rendering callback
            this.urlStateManager = new URLStateManager({
                onStateChange: (state) => {
                    console.log('🔄 URLStateManager: State changed:', state);
                    if (this.contentRenderer) {
                        this.contentRenderer.renderContent(state);
                    }
                }
            });
            
            // Initialize event system
            this.eventBus = window.EventBus;
            this.smartEventRouter = new SmartEventRouter(this.eventBus);
            
            // Initialize content renderer
            this.contentRenderer = new ContentRenderer(this.urlStateManager, this.eventBus, this.smartEventRouter);
            
            // Initialize filter manager with a short delay to ensure DOM is ready
            await new Promise(resolve => setTimeout(resolve, 100));
            
            this.filterManager = new FilterManager(this.urlStateManager, this.eventBus, this.smartEventRouter);
            await this.filterManager.initialize();
            
            // Set up our own event listeners that properly trigger state changes
            this.setupEventListeners();
            
            console.log('✅ TeamStatsApp initialized successfully');
            
            // Process initial URL state with delay for complete DOM setup
            setTimeout(() => {
                const initialState = this.urlStateManager.getState();
                console.log('🚀 Processing initial state:', initialState);
                
                if (Object.values(initialState).some(value => value && value !== '' && value !== 'main')) {
                    console.log('📊 Initial state from URL found, rendering content');
                    this.contentRenderer.renderContent(initialState);
                } else {
                    console.log('🏁 No initial filters, showing default state');
                    this.contentRenderer.renderContent({});
                }
            }, 200);
            
        } catch (error) {
            console.error('❌ Error initializing TeamStatsApp:', error);
            this.isInitialized = false;
            throw error;
        }
    }
    
    /**
     * Set up event listeners that ensure content blocks update properly
     */
    setupEventListeners() {
        console.log('🔧 Setting up event listeners...');
        
        // Team selection change
        const teamSelect = document.getElementById('teamSelect');
        if (teamSelect) {
            teamSelect.addEventListener('change', (event) => {
                const teamName = event.target.value;
                console.log('🏢 Team changed:', teamName);
                
                if (teamName) {
                    this.setState({
                        team: teamName,
                        season: '', // Clear dependent filters
                        week: ''
                    });
                } else {
                    this.setState({
                        team: '',
                        season: '',
                        week: ''
                    });
                }
            });
            console.log('✅ Team select listener attached');
        }
        
        // Season button changes (delegated event handling)
        document.addEventListener('change', (event) => {
            if (event.target.name === 'season') {
                const season = event.target.value;
                console.log('📅 Season changed:', season);
                
                this.setState({
                    season: season,
                    week: '' // Clear week when season changes
                });
            }
        });
        
        // Week button changes (delegated event handling)
        document.addEventListener('change', (event) => {
            if (event.target.name === 'week') {
                const week = event.target.value;
                console.log('📆 Week changed:', week);
                
                this.setState({
                    week: week
                });
            }
        });
        
        console.log('✅ All event listeners set up');
    }
    
    /**
     * Set state and trigger content updates
     */
    setState(newState) {
        console.log('🔄 Setting new state:', newState);
        
        if (this.urlStateManager) {
            // Update URL state (this will trigger onStateChange callback)
            this.urlStateManager.setState(newState);
            
            // Also manually trigger content rendering to ensure it happens
            const currentState = this.urlStateManager.getState();
            console.log('📊 Current state after update:', currentState);
            
            if (this.contentRenderer) {
                // Force a re-render by clearing the last rendered state
                this.contentRenderer.lastRenderedState = {};
                this.contentRenderer.renderContent(currentState);
            }
        }
    }
    
    getState() {
        return this.urlStateManager ? this.urlStateManager.getState() : {};
    }
    
    clearAllFilters() {
        console.log('🧹 Clearing all filters');
        this.setState({
            team: '',
            season: '',
            week: '',
            league: ''
        });
    }
    
    /**
     * Force refresh content blocks
     */
    refreshContent() {
        console.log('🔄 Force refreshing content...');
        if (this.contentRenderer) {
            const state = this.getState();
            this.contentRenderer.lastRenderedState = {};
            this.contentRenderer.renderContent(state);
        }
    }
    
    /**
     * Test function to set a sample state
     */
    testState() {
        console.log('🧪 Setting test state...');
        this.setState({
            team: 'Team A',
            season: '23/24'
        });
    }
    
    debug() {
        console.log('=== TeamStatsApp Debug Info ===');
        console.log('Initialized:', this.isInitialized);
        console.log('Current State:', this.getState());
        console.log('URL:', window.location.href);
        console.log('Content Renderer Debug:', this.contentRenderer ? this.contentRenderer.debug() : 'Not initialized');
        console.log('URLStateManager callbacks:', this.urlStateManager ? !!this.urlStateManager.callbacks.onStateChange : 'No URLStateManager');
        console.log('====================================');
        
        // Also test state change
        console.log('🧪 Testing state change trigger...');
        if (this.urlStateManager && this.urlStateManager.callbacks.onStateChange) {
            console.log('✅ State change callback is registered');
        } else {
            console.log('❌ State change callback missing!');
        }
    }
}

// Make globally available
window.TeamStatsApp = TeamStatsApp;