/**
 * League Content Renderer
 * 
 * Orchestrates league content rendering based on filter state
 * Uses different filter hierarchy than team stats: Season → League → Week → Team
 */

class LeagueContentRenderer {
    constructor(urlStateManager, eventBus = null) {
        this.urlStateManager = urlStateManager;
        this.eventBus = eventBus || window.EventBus;
        this.lastRenderedState = {};
        this.isRendering = false;
        
        // Content blocks registry (will be populated in Phase 3)
        this.contentBlocks = {};
        
        // Initialize content blocks (placeholder for now)
        this.initializeContentBlocks();
        
        // League content modes based on filter combinations
        this.contentModes = {
            'no-selection': {
                title: 'League Statistics',
                description: 'Select season and league to view statistics',
                blocks: []
            },
            'season-only': {
                title: 'Season Overview',
                description: 'Historical data across all leagues',
                blocks: ['season-overview', 'honor-scores']
            },
            'season-league': {
                title: 'League Analysis',
                description: 'Comprehensive league performance analysis',
                blocks: ['season-overview', 'position-progress', 'points-progress', 'honor-scores']
            },
            'season-league-week': {
                title: 'Week Analysis', 
                description: 'Current week standings and performance',
                blocks: ['week-standings', 'match-day-points', 'match-day-averages', 'match-day-positions', 'points-vs-average']
            },
            'season-league-week-team': {
                title: 'Team Analysis',
                description: 'Detailed team performance analysis',
                blocks: ['team-details', 'week-standings', 'points-vs-average']
            }
        };
    }
    
    /**
     * Initialize content blocks (placeholder for Phase 3)
     */
    initializeContentBlocks() {
        console.log('League content blocks will be initialized in Phase 3...');
        
        // For now, just log the planned blocks
        const plannedBlocks = [
            'season-overview', 'position-progress', 'points-progress',
            'match-day-points', 'match-day-averages', 'match-day-positions',
            'points-vs-average', 'week-standings', 'honor-scores', 'team-details'
        ];
        
        console.log('Planned league content blocks:', plannedBlocks);
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
            console.log('LeagueContentRenderer rendering for state:', state);
            
            // Determine content mode based on active filters
            const mode = this.determineContentMode(state);
            console.log('League content mode:', mode);
            
            // Update page title/description if needed
            this.updatePageInfo(mode, state);
            
            // For Phase 2, call legacy functions
            // In Phase 3, this will be replaced with content blocks
            await this.renderLegacyContent(mode, state);
            
        } catch (error) {
            console.error('Error rendering league content:', error);
        } finally {
            this.isRendering = false;
        }
    }
    
    /**
     * Determine content mode based on active filters (league hierarchy)
     */
    determineContentMode(state) {
        if (!state.season) {
            return 'no-selection';
        } else if (state.season && state.league && state.week && state.team) {
            return 'season-league-week-team';
        } else if (state.season && state.league && state.week) {
            return 'season-league-week';
        } else if (state.season && state.league) {
            return 'season-league';
        } else if (state.season) {
            return 'season-only';
        }
        
        return 'no-selection';
    }
    
    /**
     * Update page information based on current mode
     */
    updatePageInfo(mode, state) {
        const modeConfig = this.contentModes[mode];
        
        // Update title if there's a title element
        const titleElement = document.querySelector('.card-header h4');
        if (titleElement) {
            if (state.season && state.league) {
                const leagueName = state.league_long || state.league || '';
                titleElement.textContent = `${leagueName} ${state.season} - ${modeConfig.title}`;
            } else if (state.season) {
                titleElement.textContent = `Season ${state.season} - ${modeConfig.title}`;
            } else {
                titleElement.textContent = 'League Statistics';
            }
        }
        
        console.log(`League Mode: ${modeConfig.title} - ${modeConfig.description}`);
    }
    
    /**
     * Render legacy content (Phase 2 implementation)
     * This will be replaced with content blocks in Phase 3
     */
    async renderLegacyContent(mode, state) {
        console.log('Rendering legacy league content for mode:', mode);
        
        // Call legacy functions based on mode
        switch (mode) {
            case 'no-selection':
                // Clear all content areas
                this.clearAllContent();
                break;
                
            case 'season-only':
                if (typeof updateTableLeagueHistory === 'function') {
                    updateTableLeagueHistory();
                }
                break;
                
            case 'season-league':
                if (typeof updatePositionChart === 'function') {
                    updatePositionChart();
                }
                if (typeof updateTableLeagueHistory === 'function') {
                    updateTableLeagueHistory();
                }
                break;
                
            case 'season-league-week':
                if (typeof updatePositionChart === 'function') {
                    updatePositionChart();
                }
                if (typeof updateTableLeagueWeek === 'function') {
                    updateTableLeagueWeek();
                }
                break;
                
            case 'season-league-week-team':
                if (typeof updateTableLeagueWeek === 'function') {
                    updateTableLeagueWeek();
                }
                if (typeof updateTableTeamDetails === 'function') {
                    updateTableTeamDetails();
                }
                break;
        }
    }
    
    /**
     * Clear all content areas when no selection is made
     */
    clearAllContent() {
        // Clear tables
        const tableIds = ['leagueTableHistory', 'tableLeagueWeek', 'teamTableWeekDetails', 'positionHistoryTable'];
        tableIds.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.innerHTML = '';
            }
        });
        
        // Clear charts
        if (typeof destroyAllCharts === 'function') {
            destroyAllCharts();
        }
        
        // Show selection messages
        const selectionMessage = document.getElementById('selectionMessage');
        if (selectionMessage) {
            selectionMessage.style.display = 'block';
        }
        
        const weekMessage = document.getElementById('weekMessage');
        if (weekMessage) {
            weekMessage.style.display = 'block';
            weekMessage.innerHTML = '<div class="alert alert-info">Please select season, league, and week to view standings.</div>';
        }
    }
    
    /**
     * Get current content mode for debugging
     */
    getCurrentMode(state) {
        return this.determineContentMode(state);
    }
    
    /**
     * Debug method to show current state
     */
    debugInfo() {
        console.log('=== LeagueContentRenderer Debug Info ===');
        console.log('Content Modes:', this.contentModes);
        console.log('Planned Content Blocks:', Object.keys(this.contentBlocks));
        console.log('Is Rendering:', this.isRendering);
        console.log('Last Rendered State:', this.lastRenderedState);
    }
}

// Make LeagueContentRenderer globally available
window.LeagueContentRenderer = LeagueContentRenderer;