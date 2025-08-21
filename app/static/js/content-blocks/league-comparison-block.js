/**
 * League Comparison Content Block
 * 
 * Replaces the legacy updateLeagueComparison() function
 * Shows team performance vs league average with area chart and comparison table
 */

class LeagueComparisonBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'league-comparison',
            containerId: 'chartLeagueComparison',
            dataEndpoint: '/team/get_league_comparison',
            requiredFilters: ['team'],
            title: 'League Comparison',
            description: 'Team performance vs league average'
        });
        
        // Chart.js instance reference
        this.chartInstance = null;
    }
    
    /**
     * Render the league comparison chart and table
     */
    async render(data, filterState) {
        if (!data || Object.keys(data).length === 0) {
            throw new Error('No league comparison data available');
        }
        
        // Render chart
        await this.renderChart(data, filterState);
        
        // Render comparison table
        this.renderComparisonTable(data);
        
        console.log(`${this.id}: Rendered chart and table successfully`);
    }
    
    /**
     * Render the area chart
     */
    async renderChart(data, filterState) {
        const container = this.getContainer();
        if (!container) {
            throw new Error('Chart container not found');
        }
        
        // Get the canvas element
        let canvas = container.querySelector('canvas');
        if (!canvas) {
            canvas = container;
        }
        
        if (canvas.tagName !== 'CANVAS') {
            throw new Error('Container must contain a canvas element');
        }
        
        const seasons = Object.keys(data).sort();
        const teamScores = seasons.map(season => data[season].team_performance.team_average_score);
        const leagueScores = seasons.map(season => data[season].league_averages.average_score);
        
        // Destroy existing chart
        this.destroyChart();
        
        // Wait a bit to ensure canvas is properly sized
        await new Promise(resolve => setTimeout(resolve, 50));
        
        // Use the new canvas-compatible area chart function
        if (typeof createAreaChart_forContentBlock === 'function') {
            this.chartInstance = createAreaChart_forContentBlock(
                leagueScores,  // Reference data (league averages)
                teamScores,    // Actual data (team averages)
                canvas,        // Canvas element (not ID)
                'Team vs League Performance by Season',
                seasons        // Labels (seasons)
            );
            
            if (!this.chartInstance) {
                throw new Error('Failed to create area chart');
            }
            
            // Also store in global reference for compatibility
            window[this.containerId + 'Instance'] = this.chartInstance;
            
        } else {
            throw new Error('createAreaChart_forContentBlock function not available - check chart-adapters.js is loaded');
        }
    }
    
    /**
     * Render the comparison table
     */
    renderComparisonTable(data) {
        const tableContainer = document.getElementById('tableLeagueComparison');
        if (!tableContainer) {
            console.warn('Table container not found, skipping table render');
            return;
        }
        
        const seasons = Object.keys(data).sort();
        
        // Create comparison table data
        const tableData = seasons.map(season => {
            const seasonData = data[season];
            return [
                season,
                seasonData.league_name,
                seasonData.performance_rank,
                seasonData.team_performance.team_average_score,
                seasonData.league_averages.average_score,
                seasonData.team_performance.vs_league_score > 0 ? 
                    `+${seasonData.team_performance.vs_league_score}` : 
                    seasonData.team_performance.vs_league_score
            ];
        });

        const tableConfig = {
            data: tableData,
            columns: [
                { title: 'Saison' },
                { title: 'Liga' },
                { title: 'Platz' },
                { title: 'Team Ø' },
                { title: 'Liga Ø' },
                { title: 'Differenz' }
            ],
            headerGroups: []
        };

        // Use existing table creation function
        if (typeof createTable === 'function') {
            tableContainer.innerHTML = createTable(tableConfig);
        } else {
            console.warn('createTable function not available, rendering simple table');
            this.renderSimpleTable(tableContainer, tableData);
        }
    }
    
    /**
     * Fallback simple table rendering
     */
    renderSimpleTable(container, tableData) {
        const tableHtml = `
            <table class="table table-sm">
                <thead>
                    <tr>
                        <th>Saison</th>
                        <th>Liga</th>
                        <th>Platz</th>
                        <th>Team Ø</th>
                        <th>Liga Ø</th>
                        <th>Differenz</th>
                    </tr>
                </thead>
                <tbody>
                    ${tableData.map(row => `
                        <tr>
                            ${row.map(cell => `<td>${cell}</td>`).join('')}
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        container.innerHTML = tableHtml;
    }
    
    /**
     * Destroy the chart instance
     */
    destroyChart() {
        const container = this.getContainer();
        
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
        
        // Find and destroy any Chart.js instance attached to the canvas
        if (container) {
            let canvas = container.querySelector('canvas');
            if (!canvas) {
                canvas = container;
            }
            
            if (canvas && canvas.tagName === 'CANVAS') {
                // Chart.js stores chart instances in Chart.instances
                if (typeof Chart !== 'undefined' && Chart.instances) {
                    Object.values(Chart.instances).forEach(chartInstance => {
                        if (chartInstance && chartInstance.canvas === canvas) {
                            try {
                                console.log(`${this.id}: Destroying orphaned chart instance`);
                                chartInstance.destroy();
                            } catch (error) {
                                console.warn(`${this.id}: Error destroying orphaned chart:`, error);
                            }
                        }
                    });
                }
                
                // Also try to get chart instance from canvas context
                const ctx = canvas.getContext('2d');
                if (ctx && ctx.chart) {
                    try {
                        console.log(`${this.id}: Destroying chart from canvas context`);
                        ctx.chart.destroy();
                    } catch (error) {
                        console.warn(`${this.id}: Error destroying chart from context:`, error);
                    }
                }
            }
        }
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        const container = this.getContainer();
        if (container) {
            const parent = container.parentElement;
            if (parent) {
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'chart-loading';
                loadingDiv.innerHTML = `
                    <div class="d-flex justify-content-center align-items-center" style="height: 300px;">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <span class="ms-2">Loading league comparison...</span>
                    </div>
                `;
                
                container.style.display = 'none';
                parent.appendChild(loadingDiv);
            }
        }
        
        // Show loading for table too
        const tableContainer = document.getElementById('tableLeagueComparison');
        if (tableContainer) {
            tableContainer.innerHTML = `
                <div class="text-center p-3">
                    <div class="spinner-border spinner-border-sm text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span class="ms-2">Loading comparison data...</span>
                </div>
            `;
        }
    }
    
    /**
     * Hide loading state
     */
    hideLoading() {
        const container = this.getContainer();
        if (container) {
            container.style.display = 'block';
            
            const parent = container.parentElement;
            if (parent) {
                const loadingDiv = parent.querySelector('.chart-loading');
                if (loadingDiv) {
                    loadingDiv.remove();
                }
            }
        }
    }
    
    /**
     * Override render pipeline for dual container handling
     */
    async renderWithData(filterState) {
        if (this.isRendering) {
            console.log(`${this.id}: Already rendering, skipping...`);
            return;
        }
        
        if (JSON.stringify(filterState) === JSON.stringify(this.lastRenderedState)) {
            console.log(`${this.id}: State unchanged, skipping render`);
            return;
        }
        
        if (!this.canRender(filterState)) {
            console.log(`${this.id}: Cannot render with current state:`, filterState);
            this.showPlaceholder();
            return;
        }
        
        this.isRendering = true;
        this.lastRenderedState = { ...filterState };
        
        try {
            this.showLoading();
            
            const data = await this.fetchData(filterState);
            
            this.hideLoading();
            await this.render(data, filterState);
            
            console.log(`${this.id}: Rendered successfully`);
            
        } catch (error) {
            console.error(`${this.id}: Render error:`, error);
            this.hideLoading();
            this.showError(error);
        } finally {
            this.isRendering = false;
        }
    }
    
    /**
     * Show placeholder for both chart and table
     */
    showPlaceholder() {
        const container = this.getContainer();
        if (container) {
            const parent = container.parentElement;
            if (parent) {
                container.style.display = 'none';
                
                const placeholderDiv = document.createElement('div');
                placeholderDiv.className = 'chart-placeholder';
                placeholderDiv.innerHTML = `
                    <div class="text-center text-muted p-4" style="height: 300px; display: flex; flex-direction: column; justify-content: center;">
                        <i class="fas fa-chart-area fa-2x mb-2"></i>
                        <p>Select a team to view league comparison</p>
                    </div>
                `;
                
                parent.appendChild(placeholderDiv);
            }
        }
        
        // Show placeholder in table too
        const tableContainer = document.getElementById('tableLeagueComparison');
        if (tableContainer) {
            tableContainer.innerHTML = `
                <div class="text-center text-muted p-3">
                    <i class="fas fa-table fa-lg mb-2"></i>
                    <p class="mb-0">Comparison data will appear here</p>
                </div>
            `;
        }
    }
    
    /**
     * Show error in both containers
     */
    showError(error) {
        super.showError(error);
        
        // Show error in table container too
        const tableContainer = document.getElementById('tableLeagueComparison');
        if (tableContainer) {
            tableContainer.innerHTML = `
                <div class="alert alert-warning" role="alert">
                    <small>Unable to load comparison table: ${error.message}</small>
                </div>
            `;
        }
    }
    
    /**
     * Clear both chart and table
     */
    clear() {
        this.destroyChart();
        
        const container = this.getContainer();
        if (container) {
            container.style.display = 'block';
            
            const parent = container.parentElement;
            if (parent) {
                parent.querySelectorAll('.chart-loading, .chart-placeholder').forEach(el => el.remove());
            }
        }
        
        // Clear table
        const tableContainer = document.getElementById('tableLeagueComparison');
        if (tableContainer) {
            tableContainer.innerHTML = '';
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
}

// Make LeagueComparisonBlock globally available
window.LeagueComparisonBlock = LeagueComparisonBlock;