/**
 * SeasonOverviewBlock - Shows league table and season-wide charts
 * Displays when: Season + League are selected
 */
class SeasonOverviewBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'season-overview',
            containerId: 'seasonOverviewContainer',
            dataEndpoint: '/league/get_league_history',
            requiredFilters: ['season', 'league'],
            title: 'Season Overview'
        });
        this.dependencies = ['season', 'league'];
        this.container = document.getElementById(this.containerId);
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

    renderError(message) {
        return `
            <div class="alert alert-danger" role="alert">
                <h4 class="alert-heading">Error</h4>
                <p>${message}</p>
            </div>
        `;
    }

    async render(state = {}) {
        try {
            // Check if required dependencies are met
            if (!this.shouldRender(state)) {
                this.container.innerHTML = this.renderSelectionMessage();
                this.hide();
                return;
            }

            this.show();
            const html = this.generateHTML(state);
            this.container.innerHTML = html;
            
            // Load data and create charts
            await this.loadSeasonData(state);
            
            console.log('season-overview: Season overview rendered');
        } catch (error) {
            console.error('Error rendering season overview:', error);
            this.container.innerHTML = this.renderError('Failed to load season overview');
        }
    }

    shouldRender(state) {
        // Season overview block is disabled - don't show in any view
        return false;
    }

    generateHTML(state) {
        return `
            <div class="card mb-4">
                <div class="card-header">
                    <h5 data-i18n="season_overview">Season Overview</h5>
                </div>
                
                <!-- League History Table -->
                <div id="leagueTableHistory">
                    <div class="text-center py-3">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Loading table...</span>
                        </div>
                    </div>
                </div>

                <div class="card-body">
                    <!-- Position Charts -->
                    <div class="row">
                        <!-- Positions over the course of the season -->
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-header">
                                    <h5 data-i18n="position_in_season_progress">Position in Season Progress</h5>
                                </div>
                                <div class="card-body">
                                    <div id="chartTeamPositionCumulated" style="width: 100%; min-width: 100%; height: 300px;"></div>
                                </div>
                            </div>
                        </div>            
                        <!-- Points over the course of the season -->
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-header">
                                    <h5 data-i18n="points_in_season_progress">Points in Season Progress</h5>
                                </div>
                                <div class="card-body">
                                    <div id="chartTeamPointsCumulated" style="width: 100%; min-width: 100%; height: 300px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Shared Legend -->
                    <div class="row mt-3">
                        <div class="col-12">
                            <div id="sharedLegend" class="d-flex justify-content-center flex-wrap">
                                <!-- Legend will be dynamically inserted here -->
                            </div>
                        </div>
                    </div>
                    
                    <!-- Points Charts -->
                    <div class="row">
                        <!-- Points per Week Chart -->
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-header">
                                    <h5 data-i18n="points_per_match_day">Points per Match Day</h5>
                                </div>
                                <div class="card-body">
                                    <div id="chartTeamPointsWeekly" style="width: 100%; min-width: 100%; height: 300px;"></div>
                                </div>
                            </div>
                        </div>
                        <!-- Average per Week Chart -->
                        <div class="col-md-6">
                            <div class="card h-100">
                                <div class="card-header">
                                    <h5 data-i18n="average_per_match_day">Average per Match Day</h5>
                                </div>
                                <div class="card-body">
                                    <div id="chartTeamAverageScoreWeekly" style="width: 100%; min-width: 100%; height: 300px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Shared Legend -->
                    <div class="row mt-3">
                        <div class="col-12">
                            <div id="sharedLegendMiddle" class="d-flex justify-content-center flex-wrap">
                                <!-- Legend will be dynamically inserted here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderSelectionMessage() {
        return `
            <div class="card mb-4">
                <div class="card-header">
                    <h5>${typeof t === 'function' ? t('season_overview', 'Season Overview') : 'Season Overview'}</h5>
                </div>
                <div id="selectionMessage" class="alert alert-danger" style="font-size: 1.5rem; font-weight: bold;">
                    ${typeof t === 'function' ? t('msg.please_select.season_league', 'Please select a combination of Season and League.') : 'Please select a combination of Season and League.'}
                </div>
            </div>
        `;
    }

    async loadSeasonData(state) {
        const { season, league } = state;
        
        try {
            // Load league history table
            await this.loadLeagueHistoryTable(season, league);
            
            // Load charts in parallel
            await Promise.all([
                this.loadPositionChart(season, league),
                this.loadPointsCharts(season, league),
                this.loadAverageChart(season, league)
            ]);
            
        } catch (error) {
            console.error('Error loading season data:', error);
        }
    }

    async loadLeagueHistoryTable(season, league) {
        try {
            const response = await fetchWithDatabase(`/league/get_league_history?season=${season}&league=${league}`);
            const tableData = await response.json();
            
            console.log('League history table data:', tableData); // Debug logging
            
            const container = document.getElementById('leagueTableHistory');
            if (container) {
                // Use the proper createTableBootstrap3 function for structured TableData
                if (typeof createTableBootstrap3 === 'function') {
                    console.log('Using createTableBootstrap3 function for TableData');
                    createTableBootstrap3('leagueTableHistory', tableData, { 
                        disablePositionCircle: false, // League history should show team color circles
                        enableSpecialRowStyling: true 
                    });
                } else if (typeof createTable === 'function') {
                    console.log('Fallback: Using createTable function');
                    const tableHTML = createTable(tableData);
                    container.innerHTML = tableHTML;
                } else {
                    console.error('No table creation function available');
                    container.innerHTML = '<div class="alert alert-warning">Table creation function not available</div>';
                }
            }
        } catch (error) {
            console.error('Error loading league history table:', error);
            const container = document.getElementById('leagueTableHistory');
            if (container) {
                container.innerHTML = '<div class="alert alert-danger">Error loading league table</div>';
            }
        }
    }

    async loadPositionChart(season, league) {
        try {
            const response = await fetchWithDatabase(`/league/get_team_positions?season=${season}&league=${league}`);
            const data = await response.json();
            
            console.log('Position chart data:', data); // Debug logging
            
            // Check if data has expected structure
            if (!data || !data.data) {
                console.error('Invalid position data structure:', data);
                return;
            }
            
            // Create labels based on number of weeks
            const numWeeks = Object.values(data.data)[0]?.length || 0;
            const labels = Array.from({length: numWeeks}, (_, i) => `Week ${i + 1}`);
            
            if (typeof createLineChart === 'function') {
                createLineChart(
                    data.data,
                    data.sorted_by_best || data.sorted_by_total || Object.keys(data.data),
                    'chartTeamPositionCumulated',
                    'Position in Season Progress',
                    labels,
                    true, // reverse Y axis for positions
                    'exact' // use exact Y-axis limits for positions
                );
            }
            
            // Update shared legend with safe fallback
            const teams = data.sorted_by_best || data.sorted_by_total || Object.keys(data.data) || [];
            this.updateSharedLegend(teams);
            
        } catch (error) {
            console.error('Error loading position chart:', error);
        }
    }

    async loadPointsCharts(season, league) {
        try {
            const response = await fetchWithDatabase(`/league/get_team_points?season=${season}&league=${league}`);
            const data = await response.json();
            
            // Create labels based on number of weeks
            const numWeeks = Object.values(data.data)[0]?.length || 0;
            const matchDayFormat = window.translations ? 
                (window.translations['match_day_format'] || 'Match Day #{week}') : 
                'Match Day #{week}';
            const labels = Array.from({length: numWeeks}, (_, i) => 
                matchDayFormat.replace('{week}', i + 1)
            );

            if (typeof createScatterChartMultiAxis === 'function') {
                createScatterChartMultiAxis(
                    data.data,
                    data.sorted_by_total,
                    'chartTeamPointsWeekly',
                    'Points per Match Day',
                    labels
                );
            }

            if (typeof createLineChart === 'function') {
                createLineChart(
                    data.data_accumulated,
                    data.sorted_by_total,
                    'chartTeamPointsCumulated',
                    'Points in Season Progress',
                    labels,
                    false, // don't reverse Y axis for points
                    'auto' // use auto Y-axis limits with padding for points
                );
            }
            
        } catch (error) {
            console.error('Error loading points charts:', error);
        }
    }

    async loadAverageChart(season, league) {
        try {
            const response = await fetchWithDatabase(`/league/get_team_averages?season=${season}&league=${league}`);
            const data = await response.json();
            
            // Create labels based on number of weeks
            const numWeeks = Object.values(data.data)[0]?.length || 0;
            const matchDayFormat = window.translations ? 
                (window.translations['match_day_format'] || 'Match Day #{week}') : 
                'Match Day #{week}';
            const labels = Array.from({length: numWeeks}, (_, i) => 
                matchDayFormat.replace('{week}', i + 1)
            );

            if (typeof createLineChart === 'function') {
                createLineChart(
                    data.data,
                    data.sorted_by_average,
                    'chartTeamAverageScoreWeekly',
                    'Average per Match Day',
                    labels,
                    false, // don't reverse Y axis for averages
                    'auto' // use auto Y-axis limits with padding for averages
                );
            }
            
        } catch (error) {
            console.error('Error loading average chart:', error);
        }
    }

    updateSharedLegend(teams) {
        // Safe guard against undefined teams
        if (!teams || !Array.isArray(teams) || teams.length === 0) {
            console.warn('Teams array is empty or invalid:', teams);
            const sharedLegend = document.getElementById('sharedLegend');
            const sharedLegendMiddle = document.getElementById('sharedLegendMiddle');
            
            if (sharedLegend) sharedLegend.innerHTML = '<span class="text-muted">No teams available</span>';
            if (sharedLegendMiddle) sharedLegendMiddle.innerHTML = '<span class="text-muted">No teams available</span>';
            return;
        }
        
        const legendHtml = teams.map(team => `
            <div class="mx-3 mb-2 d-flex align-items-center">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: ${typeof getTeamColor === 'function' ? getTeamColor(team) : '#007bff'}; margin-right: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                    
                </div>
                <span>${team}</span>
            </div>
        `).join('');
        
        const sharedLegend = document.getElementById('sharedLegend');
        const sharedLegendMiddle = document.getElementById('sharedLegendMiddle');
        
        if (sharedLegend) sharedLegend.innerHTML = legendHtml;
        if (sharedLegendMiddle) sharedLegendMiddle.innerHTML = legendHtml;
    }
}