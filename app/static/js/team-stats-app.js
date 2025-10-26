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
        
        // Track currently selected buttons for deselection detection
        this.selectedButtons = new Map(); // Map of filter type to value
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
            
            // Initialize content renderer (simplified - no event bus)
            this.contentRenderer = new ContentRenderer(this.urlStateManager);
            
            // Initialize filter manager with a short delay to ensure DOM is ready
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Centralized button manager for team mode with content rendering callback
            this.buttonManager = new CentralizedButtonManager(this.urlStateManager, 'team', (state) => {
                console.log('🔄 TeamStatsApp: Button state changed, rendering content:', state);
                this.currentState = { ...state };
                if (this.contentRenderer) {
                    this.contentRenderer.renderContent(state);
                }
            });
            await this.buttonManager.initialize();
            
            // Set up our own event listeners that properly trigger state changes
            this.setupEventListeners();
            
            console.log('✅ TeamStatsApp initialized successfully');
            
            // Process initial URL state with delay for complete DOM setup
            setTimeout(() => {
                const initialState = this.urlStateManager.getState();
                console.log('🚀 Processing initial state:', initialState);
                
                // Initialize tracking map with URL parameters
                this.updateTrackingMap(initialState);
                
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
                this.selectedButtons.set('season', season);
                
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
                this.selectedButtons.set('week', week);
                
                this.setState({
                    week: week
                });
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
            
            // Check if clicked element is a radio button filter
            if (radioInput && radioInput.type === 'radio' && ['season', 'week'].includes(radioInput.name)) {
                const buttonName = radioInput.name;
                const buttonValue = radioInput.value;
                const currentlySelected = this.selectedButtons.get(buttonName);
                
                console.log(`🔍 TeamStats: Click detected on ${buttonName} button: ${buttonValue}, currently selected: ${currentlySelected}`);
                
                // Check if clicking the same button that was already selected
                if (currentlySelected === buttonValue) {
                    console.log(`🎯 TeamStats: Deselecting ${buttonName}: ${buttonValue}`);
                    
                    // Prevent the default radio button behavior by unchecking it
                    event.preventDefault();
                    event.stopPropagation();
                    radioInput.checked = false;
                    
                    // Update our tracking map
                    this.selectedButtons.delete(buttonName);
                    
                    // Trigger the appropriate state update for deselection
                    if (buttonName === 'season') {
                        console.log('📅 Season deselected');
                        this.setState({ season: '', week: '' });
                    } else if (buttonName === 'week') {
                        console.log('📆 Week deselected');
                        this.setState({ week: '' });
                    }
                    
                    return;
                }
                
                // If this is not a deselection, the change event will handle updating the tracking
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
                // Update tracking map to match new state
                this.updateTrackingMap(currentState);
                
                // Force a re-render by clearing the last rendered state
                this.contentRenderer.lastRenderedState = {};
                this.contentRenderer.renderContent(currentState);
            }
        }
    }
    
    getState() {
        return this.urlStateManager ? this.urlStateManager.getState() : {};
    }
    
    /**
     * Update the tracking map to match the current state
     */
    updateTrackingMap(state) {
        // Clear tracking map and repopulate with current selections
        this.selectedButtons.clear();
        
        if (state.season) this.selectedButtons.set('season', state.season);
        if (state.week) this.selectedButtons.set('week', state.week);
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
    
    /**
     * Update clutch threshold display only (for slider feedback)
     */
    updateClutchThresholdDisplay(newThreshold) {
        // Update the display value without triggering a full refresh
        const valueDisplay = document.getElementById('clutchThresholdValue');
        if (valueDisplay) {
            valueDisplay.textContent = newThreshold;
        }
    }
    
    /**
     * Update clutch threshold and trigger refresh
     */
    updateClutchThreshold(newThreshold) {
        console.log('🎚️ Updating clutch threshold to:', newThreshold);
        
        // Find the clutch analysis block and update its threshold
        if (this.contentRenderer && this.contentRenderer.contentBlocks) {
            const clutchBlock = this.contentRenderer.contentBlocks['clutch-analysis'];
            if (clutchBlock) {
                clutchBlock.updateThreshold(newThreshold);
                
                // Force a re-render of the clutch analysis block with new threshold
                const currentState = this.getState();
                console.log('🔄 Re-rendering clutch analysis with new threshold:', newThreshold);
                clutchBlock.renderWithData(currentState);
            }
        }
    }
    
    /**
     * Refresh clutch analysis with current threshold
     */
    refreshClutchAnalysis() {
        console.log('🔄 Refreshing clutch analysis...');
        
        if (this.contentRenderer && this.contentRenderer.contentBlocks) {
            const clutchBlock = this.contentRenderer.contentBlocks['clutch-analysis'];
            if (clutchBlock) {
                // Clear the last rendered state to force a refresh
                clutchBlock.lastRenderedState = {};
                clutchBlock.lastData = null;
                
                // Force a re-render of the clutch analysis block
                const currentState = this.getState();
                console.log('🔄 Re-rendering clutch analysis with state:', currentState);
                clutchBlock.renderWithData(currentState);
            }
        }
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