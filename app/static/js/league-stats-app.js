/**
 * LeagueStatsApp - Main application coordinator for league statistics page
 * Manages content blocks and state synchronization
 */
class LeagueStatsApp {
    constructor() {
        this.contentBlocks = new Map();
        this.currentState = {
            season: null,
            league: null,
            week: null,
            team: null
        };
        this.urlStateManager = new URLStateManager();
        this.contentRenderer = new LeagueStatsContentRenderer();
        this.filterManager = null;
        
        // Debouncing for content updates
        this.contentUpdateTimeout = null;
        this.isRenderingContent = false;
    }

    async initialize() {
        try {
            console.log('🚀 Initializing LeagueStatsApp...');
            
            // Get initial state from URL (URLStateManager initializes in constructor)
            this.currentState = { ...this.currentState, ...this.urlStateManager.getState() };
            
            // Initialize content blocks
            await this.initializeContentBlocks();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Wait a bit for filter manager to finish processing initial state
            // This ensures the default league is set before we render content
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Get the final state after filter manager processing
            this.currentState = { ...this.currentState, ...this.urlStateManager.getState() };
            
            // Initial render with final state
            await this.renderContent();
            
            console.log('✅ LeagueStatsApp initialized successfully');
        } catch (error) {
            console.error('❌ Error initializing LeagueStatsApp:', error);
            throw error;
        }
    }

    async initializeContentBlocks() {
        console.log('🧱 Initializing content blocks...');
        
        try {
            // Create content blocks FIRST (they initialize in their constructors)
            console.log('🔄 Creating SeasonLeagueStandingsBlock...');
            const seasonLeagueStandingsBlock = new SeasonLeagueStandingsBlock();
            console.log('🔄 Creating LeagueAggregationBlock...');
            const leagueAggregationBlock = new LeagueAggregationBlock();
            console.log('🔄 Creating LeagueSeasonOverviewBlock...');
            const leagueSeasonOverviewBlock = new LeagueSeasonOverviewBlock();
            console.log('🔄 Creating SeasonOverviewBlock...');
            const seasonOverviewBlock = new SeasonOverviewBlock();
            console.log('🔄 Creating MatchDayBlock...');
            const matchDayBlock = new MatchDayBlock();
            console.log('🔄 Creating TeamDetailsBlock...');
            const teamDetailsBlock = new TeamDetailsBlock();
            console.log('🔄 Creating TeamPerformanceBlock...');
            const teamPerformanceBlock = new TeamPerformanceBlock();
            console.log('🔄 Creating TeamWinPercentageBlock...');
            const teamWinPercentageBlock = new TeamWinPercentageBlock();
            
            // Store blocks (no filter-controls block needed anymore)
            this.contentBlocks.set('season-league-standings', seasonLeagueStandingsBlock);
            this.contentBlocks.set('league-aggregation', leagueAggregationBlock);
            this.contentBlocks.set('league-season-overview', leagueSeasonOverviewBlock);
            this.contentBlocks.set('season-overview', seasonOverviewBlock);
            this.contentBlocks.set('matchday', matchDayBlock);
            this.contentBlocks.set('team-details', teamDetailsBlock);
            this.contentBlocks.set('team-performance', teamPerformanceBlock);
            this.contentBlocks.set('team-win-percentage', teamWinPercentageBlock);
            
            console.log('✅ Content blocks initialized');
            
            // Initialize centralized button manager for league mode with content rendering callback
            this.buttonManager = new CentralizedButtonManager(this.urlStateManager, 'league', (state) => {
                console.log('🔄 LeagueStatsApp: Button state changed, rendering content:', state);
                this.currentState = { ...state };
                this.renderContent();
            });
            await this.buttonManager.initialize();
            
        } catch (error) {
            console.error('❌ Error initializing content blocks:', error);
            throw error;
        }
    }

    setupEventListeners() {
        // Listen for filter changes from the filter controls block
        document.addEventListener('filterChange', (event) => {
            this.handleStateChange(event.detail);
        });

        // Listen for external events (data source changes, palette changes)
        window.handleDataSourceChange = () => {
            console.log('📊 Data source changed - refreshing content');
            this.renderContent();
        };
        
        // Listen for database changes
        window.addEventListener('databaseChanged', (event) => {
            console.log('🔄 Database changed event received:', event.detail);
            this.handleDatabaseChange(event.detail.database);
        });
        
        // Listen for language changes
        window.addEventListener('languageChanged', (event) => {
            console.log('🔄 Language changed event received:', event.detail);
            this.handleLanguageChange(event.detail.language);
        });

        window.handlePaletteChange = () => {
            console.log('🎨 Palette changed - refreshing content');
            this.renderContent();
        };

        // For backward compatibility
        window.refreshAllCharts = () => {
            this.renderContent();
        };
    }

    async handleStateChange(newState) {
        console.log('🔄 State changed:', newState);
        
        // Check if state actually changed to prevent unnecessary updates
        const stateChanged = JSON.stringify(this.currentState) !== JSON.stringify(newState);
        
        // Update current state
        this.currentState = { ...newState };
        
        // Always render content on initial load or if state changed
        if (!stateChanged && Object.values(this.currentState).some(val => val && val !== '')) {
            console.log('Initial load with state, rendering content');
        } else if (!stateChanged) {
            console.log('State unchanged, skipping update');
            return;
        }
        
        // Update URL (debounced)
        this.urlStateManager.setState(this.currentState);
        
        // Debounce content rendering to prevent excessive updates
        if (this.contentUpdateTimeout) {
            clearTimeout(this.contentUpdateTimeout);
        }
        
        this.contentUpdateTimeout = setTimeout(() => {
            this.renderContent();
        }, 200); // 200ms debounce for content updates
    }
    
    /**
     * Handle database changes
     */
    async handleDatabaseChange(newDatabase) {
        console.log('🔄 Handling database change to:', newDatabase);
        
        try {
            // Update URL state with new database
            const currentState = this.urlStateManager.getState();
            const newState = {
                ...currentState,
                database: newDatabase,
                team: '', // Reset team selection
                season: '', // Reset season selection
                week: '', // Reset week selection
                league: '' // Reset league selection
            };
            
            // Update URL state
            this.urlStateManager.setState(newState);
            
            // Reinitialize button manager with new state
            if (this.buttonManager) {
                await this.buttonManager.handleStateChange(newState);
            }
            
            // Render content with new state
            this.renderContent();
            
            console.log('✅ Database change handled successfully');
            
        } catch (error) {
            console.error('❌ Error handling database change:', error);
        }
    }
    
    /**
     * Handle language changes
     */
    async handleLanguageChange(newLanguage) {
        console.log('🔄 Handling language change to:', newLanguage);
        
        try {
            // Re-render all content to update translations
            this.renderContent();
            
            console.log('✅ Language change handled successfully');
            
        } catch (error) {
            console.error('❌ Error handling language change:', error);
        }
    }

    async renderContent() {
        if (this.isRenderingContent) {
            console.log('Content rendering already in progress, skipping');
            return;
        }
        
        try {
            this.isRenderingContent = true;
            console.log('🎨 Rendering content for state:', this.currentState);
            console.log('🎨 Available content blocks:', Array.from(this.contentBlocks.keys()));
            
            // Check if we have any content blocks
            if (this.contentBlocks.size === 0) {
                console.warn('⚠️ LeagueStatsApp: No content blocks available for rendering');
                return;
            }
            
            // Render all content blocks in parallel for better performance
            const renderPromises = Array.from(this.contentBlocks.entries()).map(async ([blockName, block]) => {
                try {
                    console.log(`🔄 Rendering block: ${blockName}`);
                    await block.render(this.currentState);
                    console.log(`✅ Rendered block: ${blockName}`);
                } catch (error) {
                    console.error(`❌ Error rendering block ${blockName}:`, error);
                }
            });
            
            await Promise.all(renderPromises);
            console.log('✅ Content rendering complete');
            
        } catch (error) {
            console.error('❌ Error during content rendering:', error);
        } finally {
            this.isRenderingContent = false;
        }
    }

    // Public methods for external access
    getCurrentState() {
        return { ...this.currentState };
    }

    async setState(newState) {
        await this.handleStateChange(newState);
    }

    getContentBlock(blockName) {
        return this.contentBlocks.get(blockName);
    }
}

/**
 * LeagueStatsContentRenderer - Specialized content renderer for league stats
 */
class LeagueStatsContentRenderer {
    constructor() {
        this.contentBlocks = [];
    }

    addContentBlock(block) {
        this.contentBlocks.push(block);
    }

    async renderContent(state) {
        const renderPromises = this.contentBlocks.map(async (block) => {
            try {
                await block.render(state);
            } catch (error) {
                console.error(`Error rendering content block:`, error);
            }
        });

        await Promise.all(renderPromises);
    }
}

// Global initialization
let leagueStatsApp;

document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('📄 DOM loaded, initializing LeagueStatsApp...');
        
        leagueStatsApp = new LeagueStatsApp();
        await leagueStatsApp.initialize();
        
        // Make app globally accessible for debugging
        window.leagueStatsApp = leagueStatsApp;
        
    } catch (error) {
        console.error('❌ Failed to initialize LeagueStatsApp:', error);
        
        // Show error message to user
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger" role="alert">
                    <h4 class="alert-heading">${typeof t === 'function' ? t('status.initialization_error.title', 'Initialization Error') : 'Initialization Error'}</h4>
                    <p>${typeof t === 'function' ? t('status.initialization_error.message', 'Failed to initialize the league statistics application. Please refresh the page.') : 'Failed to initialize the league statistics application. Please refresh the page.'}</p>
                    <hr>
                    <p class="mb-0">Error: ${error.message}</p>
                </div>
            `;
        }
    }
});