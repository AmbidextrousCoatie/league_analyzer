/**
 * Team Stats Application - Fixed Version
 * 
 * Main coordinator that properly manages Phase 2 components
 * Fixes initialization timing and event handler conflicts
 */

class TeamStatsApp {
    constructor() {
        this.urlStateManager = null;
        this.filterManager = null;
        this.contentRenderer = null;
        this.isInitialized = false;
        this.initializationPromise = null;
    }
    
    /**
     * Initialize the application
     */
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
            // Mark as initialized early to prevent legacy handlers
            this.isInitialized = true;
            
            // Initialize URL state manager first
            this.urlStateManager = new URLStateManager({
                onStateChange: (state) => {
                    console.log('State changed:', state);
                    // Content renderer will handle the state change
                    if (this.contentRenderer) {
                        this.contentRenderer.renderContent(state);
                    }
                }
            });
            
            // Initialize content renderer
            this.contentRenderer = new ContentRenderer(this.urlStateManager);
            
            // Initialize filter manager (this loads teams and sets up events)
            this.filterManager = new FilterManager(this.urlStateManager);
            await this.filterManager.initialize();
            
            // Setup global error handling
            this.setupErrorHandling();
            
            console.log('TeamStatsApp initialized successfully');
            
            // Small delay to ensure DOM is ready, then process initial URL state
            setTimeout(() => {
                const initialState = this.urlStateManager.getState();
                console.log('Processing initial state:', initialState);
                
                if (Object.values(initialState).some(value => value && value !== '' && value !== 'main')) {
                    console.log('Initial state from URL found, rendering content');
                    this.contentRenderer.renderContent(initialState);
                } else {
                    console.log('No initial state, waiting for user interaction');
                }
            }, 100);
            
        } catch (error) {
            console.error('Error initializing TeamStatsApp:', error);
            this.isInitialized = false; // Reset on failure
            this.handleInitializationError(error);
            throw error;
        }
    }
    
    /**
     * Setup global error handling
     */
    setupErrorHandling() {
        // Handle fetch errors gracefully
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch.apply(window, args);
                
                if (!response.ok) {
                    console.error(`Fetch error: ${response.status} ${response.statusText} for ${args[0]}`);
                    this.showErrorMessage(`Failed to load data: ${response.status}`);
                }
                
                return response;
            } catch (error) {
                console.error('Network error:', error);
                this.showErrorMessage('Network error occurred. Please check your connection.');
                throw error;
            }
        };
    }
    
    /**
     * Handle initialization errors
     */
    handleInitializationError(error) {
        console.error('Failed to initialize app:', error);
        
        // Reset initialization flag
        this.isInitialized = false;
        
        // Fallback to legacy initialization
        console.log('Falling back to legacy initialization...');
        try {
            if (typeof initializeTeamStatsPage === 'function') {
                initializeTeamStatsPage();
            }
        } catch (legacyError) {
            console.error('Legacy initialization also failed:', legacyError);
            this.showErrorMessage('Application failed to initialize. Please refresh the page.');
        }
    }
    
    /**
     * Show error message to user
     */
    showErrorMessage(message) {
        // Try to find an existing alert container or create one
        let alertContainer = document.getElementById('errorAlerts');
        
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.id = 'errorAlerts';
            alertContainer.className = 'position-fixed top-0 end-0 p-3';
            alertContainer.style.zIndex = '1050';
            document.body.appendChild(alertContainer);
        }
        
        const alertHtml = `
            <div class="alert alert-warning alert-dismissible fade show" role="alert">
                <strong>Warning:</strong> ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alerts = alertContainer.querySelectorAll('.alert');
            if (alerts.length > 0) {
                alerts[0].remove();
            }
        }, 5000);
    }
    
    /**
     * Get current application state
     */
    getState() {
        return this.urlStateManager ? this.urlStateManager.getState() : {};
    }
    
    /**
     * Set application state programmatically
     */
    setState(newState) {
        if (this.urlStateManager) {
            this.urlStateManager.setState(newState);
        }
    }
    
    /**
     * Navigate to a specific state (useful for programmatic navigation)
     */
    navigateTo(state) {
        this.setState(state);
    }
    
    /**
     * Clear all filters
     */
    clearAllFilters() {
        this.setState({
            team: '',
            season: '',
            week: '',
            league: ''
        });
    }
    
    /**
     * Get information about current content mode
     */
    getContentInfo() {
        if (this.contentRenderer) {
            return {
                mode: this.contentRenderer.getCurrentMode(),
                state: this.getState()
            };
        }
        return null;
    }
    
    /**
     * Refresh current content (useful for manual refresh)
     */
    refreshContent() {
        if (this.contentRenderer && this.urlStateManager) {
            const currentState = this.urlStateManager.getState();
            this.contentRenderer.lastRenderedState = {}; // Force re-render
            this.contentRenderer.renderContent(currentState);
        }
    }
    
    /**
     * Debug method to log current state
     */
    debug() {
        console.log('=== TeamStatsApp Debug Info ===');
        console.log('Initialized:', this.isInitialized);
        console.log('Current State:', this.getState());
        console.log('Content Info:', this.getContentInfo());
        console.log('URL:', window.location.href);
        console.log('URLStateManager:', this.urlStateManager);
        console.log('FilterManager:', this.filterManager);
        console.log('ContentRenderer:', this.contentRenderer);
        console.log('================================');
    }
}

// Create global app instance
window.teamStatsApp = new TeamStatsApp();

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing TeamStatsApp...');
    
    // Add a small delay to ensure all scripts are loaded
    setTimeout(() => {
        window.teamStatsApp.initialize().catch(error => {
            console.error('Failed to initialize TeamStatsApp:', error);
        });
    }, 50);
});

// Make classes globally available for debugging
window.TeamStatsApp = TeamStatsApp;

// Expose helpful debug functions
window.debugTeamStats = () => window.teamStatsApp.debug();
window.refreshTeamStats = () => window.teamStatsApp.refreshContent();