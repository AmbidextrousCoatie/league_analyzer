/**
 * Team History Content Block
 * 
 * Replaces the legacy updateTeamHistory() function
 * Shows team position history across seasons with league level visualization
 */

class TeamHistoryBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'team-history',
            containerId: 'chartTeamHistory',
            dataEndpoint: '/team/get_team_history',
            requiredFilters: ['team'],
            title: 'Team Position History',
            description: 'Team position across seasons and league levels'
        });
        
        // Chart.js instance reference
        this.chartInstance = null;
    }
    
    /**
     * Render the team history chart
     */
    async render(data, filterState) {
        const container = this.getContainer();
        if (!container) {
            throw new Error('Chart container not found');
        }
        
        // Ensure container is a canvas
        let canvas = container.querySelector('canvas');
        if (!canvas) {
            canvas = container;
        }
        
        if (canvas.tagName !== 'CANVAS') {
            throw new Error('Container must be a canvas element');
        }
        
        // Wait for canvas to be properly sized
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Ensure canvas has dimensions
        if (canvas.offsetWidth === 0 || canvas.offsetHeight === 0) {
            console.warn(`${this.id}: Canvas has zero dimensions, setting defaults`);
            canvas.style.width = '100%';
            canvas.style.height = '400px';
            // Wait for style application
            await new Promise(resolve => setTimeout(resolve, 50));
        }
        
        // Process data for chart
        const seasons = Object.keys(data);
        const combinedPositions = seasons.map(season => {
            const leagueLevel = data[season].league_level;
            const position = data[season].final_position;
            return (leagueLevel - 1) * 10 + position;
        });
        
        // Destroy existing chart
        this.destroyChart();
        
        // Create new chart
        const ctx = canvas.getContext('2d');
        
        this.chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: seasons,
                datasets: [{
                    label: filterState.team,
                    data: combinedPositions,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'transparent',
                    tension: 0.1,
                    pointRadius: 15,
                    pointHoverRadius: 17,
                    pointStyle: 'circle',
                    pointBackgroundColor: 'white',
                    pointBorderColor: 'rgba(255, 99, 132, 1)',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        reverse: true,
                        beginAtZero: false,
                        min: 1,
                        max: 70,
                        ticks: {
                            autoSkip: false,
                            stepSize: 1,
                            callback: function(value) {
                                const midPoints = [5, 15, 25, 35, 45, 55, 65];
                                if (midPoints.includes(value)) {
                                    const leagueNames = {
                                        1: "1. Bundesliga",
                                        2: "2. Bundesliga",
                                        3: "Bayernliga",
                                        4: "Landesliga",
                                        5: "Bezirksoberliga",
                                        6: "Bezirksliga",
                                        7: "Kreisliga"
                                    };
                                    const leagueLevel = Math.floor((value - 1) / 10) + 1;
                                    return leagueNames[leagueLevel];
                                }
                                return '';
                            },
                            font: {
                                size: 12
                            },
                            color: '#000'
                        },
                        grid: {
                            color: (context) => {
                                const value = context.tick.value;
                                return value % 10 === 0 ? 'rgba(0, 0, 0, 0.1)' : 'transparent';
                            }
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Platzierungsverlauf'
                    },
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            afterLabel: function(context) {
                                const seasonData = data[seasons[context.dataIndex]];
                                return [
                                    `Liga: ${seasonData.league_name}`,
                                    `Endplatz: ${seasonData.final_position}`
                                ];
                            }
                        }
                    },
                    legend: {
                        display: true
                    }
                }
            },
            plugins: [{
                id: 'positionLabels',
                afterDatasetsDraw: (chart) => {
                    const {ctx} = chart;
                    const meta = chart.getDatasetMeta(0);
                    
                    meta.data.forEach((point, index) => {
                        const season = seasons[index];
                        const position = data[season].final_position;
                        
                        ctx.save();
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.font = 'bold 12px Arial';
                        ctx.fillStyle = this.getTeamColor(filterState.team);
                        ctx.fillText(position.toString(), point.x, point.y);
                        ctx.restore();
                    });
                }
            }]
        });
        
        // Set global reference for compatibility
        window.teamHistoryChart = this.chartInstance;
        window.currentTeamName = filterState.team;
        
        console.log(`${this.id}: Chart rendered successfully with ${seasons.length} seasons`);
    }
    
    /**
     * Get team color (fallback to simple color if team color map not available)
     */
    getTeamColor(teamName) {
        if (typeof getTeamColorForBlock === 'function') {
            return getTeamColorForBlock(teamName);
        }
        if (typeof getTeamColor === 'function') {
            return getTeamColor(teamName);
        }
        return 'rgba(255, 99, 132, 1)'; // Default red
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
        
        // Clean up global reference
        if (window.teamHistoryChart) {
            try {
                if (window.teamHistoryChart instanceof Chart) {
                    window.teamHistoryChart.destroy();
                }
            } catch (error) {
                console.warn(`${this.id}: Error destroying global chart reference:`, error);
            }
            window.teamHistoryChart = null;
        }
        
        // Find and destroy any Chart.js instance attached to the canvas
        if (container) {
            let canvas = container.querySelector('canvas');
            if (!canvas) {
                canvas = container;
            }
            
            if (canvas && canvas.tagName === 'CANVAS') {
                // Chart.js stores chart instances in Chart.instances
                // Find and destroy any chart using this canvas
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
     * Show loading state with chart-specific styling
     */
    showLoading() {
        const container = this.getContainer();
        if (container) {
            // For canvas containers, we need to handle differently
            const parent = container.parentElement;
            if (parent) {
                const loadingDiv = document.createElement('div');
                loadingDiv.className = 'chart-loading';
                loadingDiv.innerHTML = `
                    <div class="d-flex justify-content-center align-items-center" style="height: 300px;">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading...</span>
                        </div>
                        <span class="ms-2">Loading team history...</span>
                    </div>
                `;
                
                // Hide canvas and show loading
                container.style.display = 'none';
                parent.appendChild(loadingDiv);
            }
        }
    }
    
    /**
     * Hide loading state
     */
    hideLoading() {
        const container = this.getContainer();
        if (container) {
            container.style.display = 'block';
            
            // Remove loading div
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
     * Override render pipeline to handle canvas-specific loading
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
     * Cleanup chart resources
     */
    cleanup() {
        this.destroyChart();
    }
    
    /**
     * Show placeholder for canvas
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
                        <i class="fas fa-chart-line fa-2x mb-2"></i>
                        <p>Select a team to view position history</p>
                    </div>
                `;
                
                parent.appendChild(placeholderDiv);
            }
        }
    }
    
    /**
     * Override clear to handle canvas-specific cleanup
     */
    clear() {
        this.destroyChart();
        
        const container = this.getContainer();
        if (container) {
            container.style.display = 'block';
            
            const parent = container.parentElement;
            if (parent) {
                // Remove loading and placeholder divs
                parent.querySelectorAll('.chart-loading, .chart-placeholder').forEach(el => el.remove());
            }
        }
        
        this.lastRenderedState = {};
        this.lastData = null;
    }
}

// Make TeamHistoryBlock globally available
window.TeamHistoryBlock = TeamHistoryBlock;