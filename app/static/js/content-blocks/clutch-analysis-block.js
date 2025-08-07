/**
 * Clutch Analysis Content Block
 * 
 * Replaces the legacy updateClutchAnalysis() function
 * Shows clutch performance chart and statistics for close games
 */

class ClutchAnalysisBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'clutch-analysis',
            containerId: 'chartClutchPerformance',
            dataEndpoint: '/team/get_clutch_analysis',
            requiredFilters: ['team'],
            optionalFilters: ['season'],
            title: 'Clutch Performance',
            description: 'Performance in close games (<10 point margin)'
        });
        
        // Chart instance reference
        this.chartInstance = null;
        
        // Stats container ID
        this.statsContainerId = 'clutchStats';
    }
    
    /**
     * Render the clutch analysis chart and statistics
     */
    async render(data, filterState) {
        console.log(`${this.id}: render() called with:`, {
            hasData: !!data,
            hasOpponentClutch: !!(data && data.opponent_clutch),
            filterState: filterState,
            dataKeys: data ? Object.keys(data) : 'no data'
        });
        
        if (!data || !data.opponent_clutch) {
            console.error(`${this.id}: No clutch analysis data available:`, data);
            throw new Error('No clutch analysis data available');
        }
        
        console.log('ClutchAnalysisBlock: Rendering clutch analysis with data:', data);
        
        // Render chart
        await this.renderChart(data, filterState);
        
        // Render statistics
        this.renderStatistics(data);
        
        console.log(`${this.id}: Rendered chart and statistics successfully`);
    }
    
    /**
     * Render the clutch performance chart
     */
    async renderChart(data, filterState) {
        const container = this.getContainer();
        if (!container) {
            throw new Error('Chart container not found');
        }
        
        const opponentClutch = data.opponent_clutch;
        
        if (!opponentClutch || Object.keys(opponentClutch).length === 0) {
            console.log(`${this.id}: No opponent data to chart`);
            this.showEmptyChart();
            return;
        }
        
        console.log(`${this.id}: Creating clutch performance chart with opponents:`, Object.keys(opponentClutch));
        
        // Destroy existing chart
        this.destroyChart();
        
        // Use the existing clutch performance chart function
        if (typeof createClutchPerformanceChart === 'function') {
            try {
                createClutchPerformanceChart(
                    opponentClutch,
                    this.containerId,
                    'Clutch Games Performance per Opponent (<10 point margin)'
                );
                
                // Store reference to the chart instance created by the legacy function
                this.chartInstance = window[this.containerId + 'Instance'];
                
                console.log(`${this.id}: Chart created successfully`);
            } catch (error) {
                console.error(`${this.id}: Error creating clutch performance chart:`, error);
                throw error;
            }
        } else {
            throw new Error('createClutchPerformanceChart function not available');
        }
    }
    
    /**
     * Render the clutch statistics
     */
    renderStatistics(data) {
        const statsContainer = document.getElementById(this.statsContainerId);
        if (!statsContainer) {
            console.warn(`${this.id}: Stats container not found, skipping stats render`);
            return;
        }
        
        const statsHtml = `
            <div class="row text-center">
                <div class="col-md-3">
                    <div class="card bg-light">
                        <div class="card-body">
                            <h6>Total Games</h6>
                            <h4>${data.total_games || 0}</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light">
                        <div class="card-body">
                            <h6>Clutch Games</h6>
                            <h4>${data.total_clutch_games || 0}</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light">
                        <div class="card-body">
                            <h6>Clutch Wins</h6>
                            <h4 class="text-success">${data.total_clutch_wins || 0}</h4>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light">
                        <div class="card-body">
                            <h6>Win %</h6>
                            <h4 class="text-primary">${data.clutch_percentage || 0}%</h4>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        statsContainer.innerHTML = statsHtml;
        console.log(`${this.id}: Statistics rendered successfully`);
    }
    
    /**
     * Show empty chart message
     */
    showEmptyChart() {
        const container = this.getContainer();
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted p-4" style="height: 300px; display: flex; flex-direction: column; justify-content: center;">
                    <i class="fas fa-chart-bar fa-2x mb-2"></i>
                    <p>No clutch games data available for the selected filters</p>
                    <small>Try selecting a different team or season</small>
                </div>
            `;
        }
    }
    
    /**
     * Destroy the chart instance
     */
    destroyChart() {
        // Destroy our tracked instance
        if (this.chartInstance instanceof Chart) {
            try {
                this.chartInstance.destroy();
            } catch (error) {
                console.warn(`${this.id}: Error destroying chart instance:`, error);
            }
            this.chartInstance = null;
        }
        
        // Clean up global reference for legacy chart functions
        const globalRef = window[this.containerId + 'Instance'];
        if (globalRef instanceof Chart) {
            try {
                globalRef.destroy();
            } catch (error) {
                console.warn(`${this.id}: Error destroying global chart reference:`, error);
            }
            window[this.containerId + 'Instance'] = null;
        }
        
        // Also clear the container in case it's not a canvas-based chart
        const container = this.getContainer();
        if (container) {
            // If container has canvas, handle it specially
            const canvas = container.querySelector('canvas');
            if (canvas) {
                // Clear any Chart.js instances on the canvas
                this.clearOrphanedCharts();
            } else {
                // For non-canvas containers, just clear content
                container.innerHTML = '';
            }
        }
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        const container = this.getContainer();
        if (container) {
            container.innerHTML = `
                <div class="d-flex justify-content-center align-items-center" style="height: 300px;">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span class="ms-2">Loading clutch analysis...</span>
                </div>
            `;
        }
        
        // Show loading for stats too
        const statsContainer = document.getElementById(this.statsContainerId);
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="text-center p-3">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span class="ms-2">Loading clutch statistics...</span>
                </div>
            `;
        }
    }
    
    /**
     * Show placeholder for both chart and stats
     */
    showPlaceholder() {
        const container = this.getContainer();
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted p-4" style="height: 300px; display: flex; flex-direction: column; justify-content: center;">
                    <i class="fas fa-chart-bar fa-2x mb-2"></i>
                    <p>Select a team to view clutch performance</p>
                </div>
            `;
        }
        
        // Show placeholder in stats too
        const statsContainer = document.getElementById(this.statsContainerId);
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="text-center text-muted p-3">
                    <i class="fas fa-table fa-lg mb-2"></i>
                    <p class="mb-0">Clutch statistics will appear here</p>
                </div>
            `;
        }
    }
    
    /**
     * Show error in both containers
     */
    showError(error) {
        super.showError(error);
        
        // Show error in stats container too
        const statsContainer = document.getElementById(this.statsContainerId);
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="alert alert-warning" role="alert">
                    <small>Unable to load clutch statistics: ${error.message}</small>
                </div>
            `;
        }
    }
    
    /**
     * Clear both chart and stats
     */
    clear() {
        this.destroyChart();
        
        // Clear stats container
        const statsContainer = document.getElementById(this.statsContainerId);
        if (statsContainer) {
            statsContainer.innerHTML = '';
        }
        
        this.lastRenderedState = {};
        this.lastData = null;
    }
    
    /**
     * Cleanup resources
     */
    cleanup() {
        this.destroyChart();
    }
    
    /**
     * Check if stats container exists
     */
    hasStatsContainer() {
        return !!document.getElementById(this.statsContainerId);
    }
    
    /**
     * Debug information
     */
    debug() {
        const baseDebug = super.debug();
        return {
            ...baseDebug,
            statsContainerId: this.statsContainerId,
            hasStatsContainer: this.hasStatsContainer(),
            chartInstance: !!this.chartInstance
        };
    }
}

// Make ClutchAnalysisBlock globally available
window.ClutchAnalysisBlock = ClutchAnalysisBlock;