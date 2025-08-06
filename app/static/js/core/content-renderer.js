/**
 * Content Renderer
 * 
 * Orchestrates content display based on current filter state
 * Acts as coordinator between state management and legacy functions
 */

class ContentRenderer {
    constructor(urlStateManager) {
        this.urlStateManager = urlStateManager;
        this.lastRenderedState = {};
        this.isRendering = false;
        
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
                blocks: ['team-history', 'league-comparison', 'consistency-metrics', 'special-matches']
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
        
        // You could add a description element here if desired
        console.log(`Mode: ${modeConfig.title} - ${modeConfig.description}`);
    }
    
    /**
     * Render content blocks for the current mode
     */
    async renderContentBlocks(mode, state) {
        const modeConfig = this.contentModes[mode];
        
        if (mode === 'no-selection') {
            // Clear all content areas when no team selected
            this.clearAllContent();
            return;
        }
        
        // Show loading states
        this.showLoadingStates(modeConfig.blocks);
        
        // Render blocks based on mode configuration
        const renderPromises = [];
        
        if (modeConfig.blocks.includes('team-history')) {
            renderPromises.push(this.renderTeamHistory(state));
        }
        
        if (modeConfig.blocks.includes('league-comparison')) {
            renderPromises.push(this.renderLeagueComparison(state));
        }
        
        if (modeConfig.blocks.includes('clutch-analysis')) {
            renderPromises.push(this.renderClutchAnalysis(state));
        }
        
        if (modeConfig.blocks.includes('consistency-metrics')) {
            renderPromises.push(this.renderConsistencyMetrics(state));
        }
        
        if (modeConfig.blocks.includes('special-matches')) {
            renderPromises.push(this.renderSpecialMatches(state));
        }
        
        // Wait for all content to render
        await Promise.allSettled(renderPromises);
        
        // Hide loading states
        this.hideLoadingStates();
    }
    
    /**
     * Render team history chart
     */
    async renderTeamHistory(state) {
        if (!state.team) return;
        
        try {
            console.log('Rendering team history for:', state.team);
            // Call existing legacy function
            updateTeamHistory(state.team);
        } catch (error) {
            console.error('Error rendering team history:', error);
        }
    }
    
    /**
     * Render league comparison
     */
    async renderLeagueComparison(state) {
        if (!state.team) return;
        
        try {
            console.log('Rendering league comparison for:', state.team);
            // Call existing legacy function
            updateLeagueComparison(state.team);
        } catch (error) {
            console.error('Error rendering league comparison:', error);
        }
    }
    
    /**
     * Render clutch analysis
     */
    async renderClutchAnalysis(state) {
        if (!state.team) return;
        
        try {
            console.log('Rendering clutch analysis for:', state.team, state.season);
            // Call existing legacy function
            updateClutchAnalysis(state.team, state.season || null);
        } catch (error) {
            console.error('Error rendering clutch analysis:', error);
        }
    }
    
    /**
     * Render consistency metrics
     */
    async renderConsistencyMetrics(state) {
        if (!state.team) return;
        
        try {
            console.log('Rendering consistency metrics for:', state.team, state.season);
            // Call existing legacy function
            updateConsistencyMetrics(state.team, state.season || null);
        } catch (error) {
            console.error('Error rendering consistency metrics:', error);
        }
    }
    
    /**
     * Render special matches
     */
    async renderSpecialMatches(state) {
        if (!state.team) return;
        
        try {
            console.log('Rendering special matches for:', state.team, state.season);
            // Call existing legacy function
            if (state.season && state.season !== '') {
                loadSpecialMatchesForSeason(state.team, state.season);
            } else {
                loadSpecialMatches(state.team);
            }
        } catch (error) {
            console.error('Error rendering special matches:', error);
        }
    }
    
    /**
     * Clear all content areas
     */
    clearAllContent() {
        const contentAreas = [
            'chartTeamHistory',
            'chartLeagueComparison', 
            'tableLeagueComparison',
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
        
        // Destroy charts if they exist
        if (window.teamHistoryChart instanceof Chart) {
            window.teamHistoryChart.destroy();
            window.teamHistoryChart = null;
        }
        
        console.log('All content areas cleared');
    }
    
    /**
     * Show loading states for specified blocks
     */
    showLoadingStates(blocks) {
        // You could add loading spinners here
        console.log('Showing loading states for blocks:', blocks);
    }
    
    /**
     * Hide loading states
     */
    hideLoadingStates() {
        // You could hide loading spinners here
        console.log('Hiding loading states');
    }
    
    /**
     * Get current content mode
     */
    getCurrentMode() {
        const state = this.urlStateManager.getState();
        return this.determineContentMode(state);
    }
}

// Make ContentRenderer globally available
window.ContentRenderer = ContentRenderer;