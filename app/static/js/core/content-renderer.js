/**
 * Content Renderer - Phase 3 Version
 * 
 * Updated to use content blocks instead of legacy functions
 * Gradual migration: starts with team history and league comparison blocks
 */

class ContentRenderer {
    constructor(urlStateManager, eventBus = null, smartEventRouter = null) {
        this.urlStateManager = urlStateManager;
        this.eventBus = eventBus || window.EventBus;
        this.smartEventRouter = smartEventRouter;
        this.lastRenderedState = {};
        this.isRendering = false;
        
        // Content blocks registry
        this.contentBlocks = {};
        
        // Initialize content blocks
        this.initializeContentBlocks();
        
        // Content modes based on filter combinations
        this.contentModes = {
            'no-selection': {
                title: 'Team Overview',
                description: 'Select a team to view detailed statistics',
                blocks: []
            },
            'team-only': {
                title: 'Team Complete History',
                description: 'All seasons overview',
                blocks: ['team-history', 'league-comparison', 'clutch-analysis', 'consistency-metrics', 'special-matches']
            },
            'team-season': {
                title: 'Team Season Analysis',
                description: 'Detailed season performance',
                blocks: ['team-history', 'league-comparison', 'clutch-analysis', 'consistency-metrics', 'special-matches']
            },
            'team-season-week': {
                title: 'Team Week Performance',
                description: 'Week-specific analysis',
                blocks: ['team-history', 'league-comparison', 'clutch-analysis', 'consistency-metrics', 'special-matches']
            }
        };
    }
    
    /**
     * Initialize content blocks
     */
    initializeContentBlocks() {
        console.log('Initializing Phase 3 content blocks...');
        
        // Initialize available content blocks
        try {
            this.contentBlocks['team-history'] = new TeamHistoryBlock();
            console.log('TeamHistoryBlock initialized');
        } catch (error) {
            console.error('Failed to initialize TeamHistoryBlock:', error);
        }
        
        try {
            this.contentBlocks['league-comparison'] = new LeagueComparisonBlock();
            console.log('LeagueComparisonBlock initialized');
        } catch (error) {
            console.error('Failed to initialize LeagueComparisonBlock:', error);
        }
        
        try {
            this.contentBlocks['clutch-analysis'] = new ClutchAnalysisBlock();
            console.log('ClutchAnalysisBlock initialized');
        } catch (error) {
            console.error('Failed to initialize ClutchAnalysisBlock:', error);
        }
        
        try {
            this.contentBlocks['consistency-metrics'] = new ConsistencyMetricsBlock();
            console.log('ConsistencyMetricsBlock initialized');
        } catch (error) {
            console.error('Failed to initialize ConsistencyMetricsBlock:', error);
        }
        
        try {
            this.contentBlocks['special-matches'] = new SpecialMatchesBlock();
            console.log('SpecialMatchesBlock initialized');
        } catch (error) {
            console.error('Failed to initialize SpecialMatchesBlock:', error);
        }
        
        console.log('Content blocks initialized:', Object.keys(this.contentBlocks));
    }
    
    /**
     * Render content based on current state
     */
    async renderContent(state) {
        if (this.isRendering) {
            console.log('Already rendering, skipping...');
            return;
        }
        
        // Check if state actually changed
        if (JSON.stringify(state) === JSON.stringify(this.lastRenderedState)) {
            console.log('State unchanged, skipping render');
            return;
        }
        
        this.isRendering = true;
        this.lastRenderedState = { ...state };
        
        try {
            console.log('ContentRenderer rendering for state:', state);
            
            // Determine content mode based on active filters
            const mode = this.determineContentMode(state);
            console.log('Content mode:', mode);
            
            // Update page title/description if needed
            this.updatePageInfo(mode, state);
            
            // Render content blocks for this mode
            await this.renderContentBlocks(mode, state);
            
        } catch (error) {
            console.error('Error rendering content:', error);
        } finally {
            this.isRendering = false;
        }
    }
    
    /**
     * Determine content mode based on active filters
     */
    determineContentMode(state) {
        if (!state.team) {
            return 'no-selection';
        } else if (state.team && state.season && state.week) {
            return 'team-season-week';
        } else if (state.team && state.season) {
            return 'team-season';
        } else if (state.team) {
            return 'team-only';
        }
        
        return 'no-selection';
    }
    
    /**
     * Update page title and description
     */
    updatePageInfo(mode, state) {
        const modeConfig = this.contentModes[mode];
        
        // Update title if there's a title element
        const titleElement = document.querySelector('.card-header h4');
        if (titleElement && state.team) {
            titleElement.textContent = `${state.team} - ${modeConfig.title}`;
        } else if (titleElement) {
            titleElement.textContent = 'Team Statistics';
        }
        
        console.log(`Mode: ${modeConfig.title} - ${modeConfig.description}`);
    }
    
    /**
     * Render content blocks for the current mode
     */
    async renderContentBlocks(mode, state) {
        const modeConfig = this.contentModes[mode];
        console.log(`ContentRenderer: Rendering blocks for ${mode}:`, modeConfig.blocks);
        
        if (mode === 'no-selection') {
            // Clear all content areas when no team selected
            this.clearAllContent();
            return;
        }
        
        // Render blocks based on mode configuration
        const renderPromises = [];
        
        // Phase 3: Use content blocks for team-history and league-comparison
        if (modeConfig.blocks.includes('team-history') && this.contentBlocks['team-history']) {
            renderPromises.push(this.contentBlocks['team-history'].renderWithData(state));
        }
        
        if (modeConfig.blocks.includes('league-comparison') && this.contentBlocks['league-comparison']) {
            renderPromises.push(this.contentBlocks['league-comparison'].renderWithData(state));
        }
        
        // Phase 3: Use content block for clutch analysis
        if (modeConfig.blocks.includes('clutch-analysis') && this.contentBlocks['clutch-analysis']) {
            console.log('ContentRenderer: Adding clutch-analysis block to render queue');
            renderPromises.push(this.contentBlocks['clutch-analysis'].renderWithData(state));
        } else {
            console.log('ContentRenderer: Clutch analysis block skipped - included:', modeConfig.blocks.includes('clutch-analysis'), 'available:', !!this.contentBlocks['clutch-analysis']);
        }
        
        // Phase 3: Use content block for consistency metrics
        if (modeConfig.blocks.includes('consistency-metrics') && this.contentBlocks['consistency-metrics']) {
            renderPromises.push(this.contentBlocks['consistency-metrics'].renderWithData(state));
        }
        
        // Phase 3: Use content block for special matches
        if (modeConfig.blocks.includes('special-matches') && this.contentBlocks['special-matches']) {
            console.log('ContentRenderer: Adding special-matches block to render queue');
            renderPromises.push(this.contentBlocks['special-matches'].renderWithData(state));
        } else {
            console.log('ContentRenderer: Special matches block skipped - included:', modeConfig.blocks.includes('special-matches'), 'available:', !!this.contentBlocks['special-matches']);
        }
        
        // Wait for all content to render
        await Promise.allSettled(renderPromises);
        
        console.log('All content blocks rendered');
    }
    
    /**
     * Legacy fallback for clutch analysis
     */
    async renderClutchAnalysisLegacy(state) {
        if (!state.team) return;
        
        try {
            console.log('Rendering clutch analysis (legacy) for:', state.team, state.season);
            if (typeof updateClutchAnalysis === 'function') {
                updateClutchAnalysis(state.team, state.season || null);
            }
        } catch (error) {
            console.error('Error rendering clutch analysis (legacy):', error);
        }
    }
    
    /**
     * Legacy fallback for consistency metrics
     */
    async renderConsistencyMetricsLegacy(state) {
        if (!state.team) return;
        
        try {
            console.log('Rendering consistency metrics (legacy) for:', state.team, state.season);
            if (typeof updateConsistencyMetrics === 'function') {
                updateConsistencyMetrics(state.team, state.season || null);
            }
        } catch (error) {
            console.error('Error rendering consistency metrics (legacy):', error);
        }
    }
    
    /**
     * Legacy fallback for special matches
     */
    async renderSpecialMatchesLegacy(state) {
        if (!state.team) return;
        
        try {
            console.log('Rendering special matches (legacy) for:', state.team, state.season);
            if (state.season && state.season !== '') {
                if (typeof loadSpecialMatchesForSeason === 'function') {
                    loadSpecialMatchesForSeason(state.team, state.season);
                }
            } else {
                if (typeof loadSpecialMatches === 'function') {
                    loadSpecialMatches(state.team);
                }
            }
        } catch (error) {
            console.error('Error rendering special matches (legacy):', error);
        }
    }
    
    /**
     * Clear all content areas
     */
    clearAllContent() {
        console.log('Clearing all content areas');
        
        // Clear content blocks
        Object.values(this.contentBlocks).forEach(block => {
            try {
                block.clear();
            } catch (error) {
                console.error('Error clearing content block:', error);
            }
        });
        
        // Clear legacy content areas
        const contentAreas = [
            'chartClutchPerformance',
            'clutchStats',
            'consistencyMetrics',
            'highestScoresBody',
            'lowestScoresBody',
            'biggestWinsBody',
            'biggestLossesBody'
        ];
        
        contentAreas.forEach(areaId => {
            const element = document.getElementById(areaId);
            if (element) {
                element.innerHTML = '';
            }
        });
        
        console.log('All content areas cleared');
    }
    
    /**
     * Get current content mode
     */
    getCurrentMode() {
        const state = this.urlStateManager.getState();
        return this.determineContentMode(state);
    }
    
    /**
     * Debug information
     */
    debug() {
        return {
            lastRenderedState: this.lastRenderedState,
            isRendering: this.isRendering,
            currentMode: this.getCurrentMode(),
            contentBlocks: Object.keys(this.contentBlocks),
            availableBlocks: Object.keys(this.contentBlocks).map(key => ({
                id: key,
                hasContainer: this.contentBlocks[key].hasContainer(),
                debug: this.contentBlocks[key].debug()
            }))
        };
    }
}

// Make ContentRenderer globally available
window.ContentRenderer = ContentRenderer;