class TeamVsTeamComparisonBlock {
    constructor() {
        this.containerId = 'team-vs-team-comparison';
        this.container = document.getElementById(this.containerId);
    }

    shouldRender(state) {
        // Show when league is selected, season and week are optional
        return state.league && !state.team;
    }

    async render(state = {}) {
        try {
            // Check if required dependencies are met
            if (!this.shouldRender(state)) {
                this.hide();
                return;
            }

            this.show();
            
            // Fetch data
            const data = await this.fetchData(state);
            
            if (!data || !data.columns || !data.data) {
                this.renderError('No team vs team comparison data available.');
                return;
            }

            if (!this.container) {
                console.error(`${this.containerId}: Container not found`);
                return;
            }

            // Create the card structure
            this.container.innerHTML = `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>${data.title || 'Team vs Team Comparison'}</h5>
                        <p class="mb-0 text-muted">${data.description || 'Matrix showing team performance against each opponent'}</p>
                    </div>
                    <div class="card-body">
                        <!-- Team vs Team Comparison Table -->
                        <div class="row">
                            <div class="col-12">
                                <div id="team-vs-team-comparison-table"></div>
                            </div>
                        </div>
                        
                        <!-- Heat Map Legend -->
                        <div class="row mt-3">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h6>Heat Map Legend</h6>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-md-6">
                                                <h6>Score Heat Map</h6>
                                                <div class="d-flex align-items-center">
                                                    <span class="me-2">Low:</span>
                                                    <div class="heat-map-legend me-2" style="background: #a9e9f9; width: 20px; height: 20px;"></div>
                                                    <span class="me-2">High:</span>
                                                    <div class="heat-map-legend" style="background: #06313c; width: 20px; height: 20px;"></div>
                                                </div>
                                                <small class="text-muted">Range: ${data.metadata?.score_range?.min || 'N/A'} - ${data.metadata?.score_range?.max || 'N/A'}</small>
                                            </div>
                                            <div class="col-md-6">
                                                <h6>Points Heat Map</h6>
                                                <div class="d-flex align-items-center">
                                                    <span class="me-2">Low:</span>
                                                    <div class="heat-map-legend me-2" style="background: #a9e9f9; width: 20px; height: 20px;"></div>
                                                    <span class="me-2">High:</span>
                                                    <div class="heat-map-legend" style="background: #06313c; width: 20px; height: 20px;"></div>
                                                </div>
                                                <small class="text-muted">Range: ${data.metadata?.points_range?.min || 'N/A'} - ${data.metadata?.points_range?.max || 'N/A'}</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Create table using createTableBootstrap3
            this.createComparisonTable(data);
            
        } catch (error) {
            console.error('Error rendering team vs team comparison:', error);
            this.renderError('Failed to load team vs team comparison data');
        }
    }

    async fetchData(filterState) {
        const url = new URL('/league/get_team_vs_team_comparison', window.location.origin);
        
        // Add required parameters
        url.searchParams.append('league', filterState.league);
        url.searchParams.append('season', filterState.season);
        
        // Add optional week parameter
        if (filterState.week) {
            url.searchParams.append('week', filterState.week);
        }
        
        // Add database parameter
        const database = getCurrentDatabase();
        if (database) {
            url.searchParams.append('database', database);
        }

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(`API Error: ${data.error}`);
        }
        
        return data;
    }

    hide() {
        if (this.container) {
            this.container.style.display = 'none';
        }
    }

    show() {
        if (this.container) {
            this.container.style.display = 'block';
        }
    }

    createComparisonTable(data) {
        if (typeof createTableBootstrap3 !== 'function') {
            console.error('createTableBootstrap3 function not available');
            return;
        }

        // Check if container exists
        const tableContainer = document.getElementById('team-vs-team-comparison-table');
        if (!tableContainer) {
            console.error('Table container not found!');
            return;
        }

        // Create table with heat map support
        createTableBootstrap3('team-vs-team-comparison-table', data, {
            disablePositionCircle: true,
            enableSpecialRowStyling: true,
            enableHeatMap: true
        });
    }

    renderError(message) {
        if (this.container) {
            this.container.innerHTML = `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Team vs Team Comparison</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-warning" role="alert">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            ${message}
                        </div>
                    </div>
                </div>
            `;
        }
    }
}
