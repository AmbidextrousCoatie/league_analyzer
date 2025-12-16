/**
 * API Test Application
 * 
 * Main coordinator for API testing page
 * Uses content block architecture similar to TeamStatsApp and LeagueStatsApp
 */

class APITestApp {
    constructor() {
        this.urlStateManager = null;
        this.buttonManager = null;
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
            
            // Initialize centralized button manager for league mode with content rendering callback
            this.buttonManager = new CentralizedButtonManager(this.urlStateManager, 'league', (state) => {
                console.log('🔄 APITestApp: Button state changed, rendering content:', state);
                this.currentState = { ...state };
                if (this.contentRenderer) {
                    this.contentRenderer.renderContent(state);
                }
            });
            await this.buttonManager.initialize();
            
            // Render initial content
            await this.contentRenderer.renderContent(this.currentState);
            
            this.isInitialized = true;
            console.log('✅ APITestApp initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize APITestApp:', error);
            throw error;
        }
    }
    
    /**
     * Get current state from centralized button manager
     */
    getCurrentState() {
        return this.buttonManager ? this.buttonManager.getState() : this.currentState;
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