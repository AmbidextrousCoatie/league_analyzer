class TeamPerformanceBlock {
    constructor() {
        this.containerId = 'team-performance';
        this.chartContainerId = 'team-performance-chart';
        this.container = document.getElementById(this.containerId);
    }

    shouldRender(state) {
        return state.league && state.season && state.team && !state.week;
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
            
            
            if (!data || !data.performance_data || !data.performance_data.data || Object.keys(data.performance_data.data).length === 0) {
                this.renderError(typeof t === 'function' ? t('no_data', 'No performance data available for the selected team.') : 'No performance data available for the selected team.');
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
                        <h5>${data.team} - ${typeof t === 'function' ? t('ui.team_performance.title', 'Performance Analysis') : 'Performance Analysis'}</h5>
                        <p class="mb-0 text-muted">${typeof t === 'function' ? t('ui.team_performance.description', 'Individual player scores and team performance over time') : 'Individual player scores and team performance over time'}</p>
                    </div>
                    <div class="card-body">
                        <!-- Performance Table -->
                        <div class="row mb-4">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h6>${typeof t === 'function' ? t('ui.team_performance.individual', 'Individual Player Performance') : 'Individual Player Performance'}</h6>
                                        <p class="mb-0 text-muted small">${typeof t === 'function' ? t('ui.team_performance.individual_desc', 'Player scores per week with totals and averages per game') : 'Player scores per week with totals and averages per game'}</p>
                                    </div>
                                    <div class="card-body">
                                        <div id="team-performance-table"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Performance Chart -->
                        <div class="row">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h6>${typeof t === 'function' ? t('ui.team_performance.trends', 'Performance Trends') : 'Performance Trends'}</h6>
                                        <p class="mb-0 text-muted small">${typeof t === 'function' ? t('ui.team_performance.trends_desc', 'Individual player performance over time') : 'Individual player performance over time'}</p>
                                    </div>
                                    <div class="card-body">
                                        <div id="${this.chartContainerId}" style="height: 400px;"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Create table using createTableBootstrap3
            this.createPerformanceTable(data);
            
            // Render the chart
            this.renderChart(data);
            
        } catch (error) {
            console.error('Error rendering team performance analysis:', error);
            this.renderError(typeof t === 'function' ? t('error_loading_data', 'Failed to load team performance analysis data') : 'Failed to load team performance analysis data');
        }
    }

    async fetchData(filterState) {
        const url = new URL('/league/get_team_analysis', window.location.origin);
        
        // Add required parameters
        url.searchParams.append('league', filterState.league);
        url.searchParams.append('season', filterState.season);
        url.searchParams.append('team', filterState.team);
        
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

    createPerformanceTable(data) {
        if (typeof createTableBootstrap3 !== 'function') {
            console.error('createTableBootstrap3 function not available');
            return;
        }

        // Extract data from SeriesData format
        const performanceData = data.performance_data;
        const weeks = data.weeks;
        
        // Convert SeriesData format to array format for Bootstrap Table 3
        const tableRows = [];
        const teamAverageKey = `${data.team} (Team Average)`;
        
        // Process individual players first (excluding team average)
        Object.keys(performanceData.data).forEach(playerName => {
            if (playerName === teamAverageKey) return; // Skip team average for now
            
            const playerData = performanceData.data[playerName];
            const total = performanceData.total[playerName] || 0;
            const average = performanceData.average[playerName] || 0;
            
            // Create array row: [player, week1, week2, ..., total_score, total_games, average_score]
            const tableRow = [playerName];
            
            // Add week data
            weeks.forEach((week, index) => {
                const weekValue = playerData[index];
                tableRow.push(weekValue === null || weekValue === undefined ? '-' : weekValue);
            });
            
            // Add totals (now correctly calculated from backend)
            const totalGames = performanceData.counts ? performanceData.counts[playerName] : 0;
            tableRow.push(Math.round(total * 100) / 100);          // total_score (rounded to 2 decimals)
            tableRow.push(totalGames);                             // total_games (actual number of games)
            tableRow.push(Math.round(average * 100) / 100);        // average_score (rounded to 2 decimals)
            
            tableRows.push(tableRow);
        });
        
        // Add team average as the last row
        if (performanceData.data[teamAverageKey]) {
            const teamData = performanceData.data[teamAverageKey];
            const teamTotal = performanceData.total[teamAverageKey] || 0;
            const teamAverage = performanceData.average[teamAverageKey] || 0;
            
            // Create array row for team average: [player, week1, week2, ..., total_score, total_games, average_score]
            const teamRow = [teamAverageKey];
            
            // Add week data
            weeks.forEach((week, index) => {
                const weekValue = teamData[index];
                teamRow.push(weekValue === null || weekValue === undefined ? '-' : weekValue);
            });
            
            // Add totals
            const teamTotalGames = performanceData.counts ? performanceData.counts[teamAverageKey] : 0;
            teamRow.push(Math.round(teamTotal * 100) / 100);       // total_score (rounded to 2 decimals)
            teamRow.push(teamTotalGames);                          // total_games (actual number of games)
            teamRow.push(Math.round(teamAverage * 100) / 100);     // average_score (rounded to 2 decimals)
            
            tableRows.push(teamRow);
        }
        
        // Create row metadata for styling (team average row should be bold)
        const rowMetadata = [];
        tableRows.forEach((row, index) => {
            if (row[0] === teamAverageKey) {
                // Team average row - make it bold
                rowMetadata[index] = {
                    styling: {
                        fontWeight: 'bold',
                        backgroundColor: window.ColorUtils?.getThemeColor('background') || '#f8f9fa'
                    }
                };
            } else {
                // Regular player row
                rowMetadata[index] = {};
            }
        });

        // Prepare table data for createTableBootstrap3 (array format)
        const tableData = {
            title: `${data.team} - ${typeof t === 'function' ? t('ui.team_performance.player_performance', 'Player Performance') : 'Player Performance'}`,
            description: typeof t === 'function' ? t('ui.team_performance.player_perf_desc', 'Individual player average scores per game with totals and averages') : 'Individual player average scores per game with totals and averages',
            columns: [
                {
                    title: typeof t === 'function' ? t('player', 'Player') : 'Player',
                    columns: [
                        { title: typeof t === 'function' ? t('player', 'Player') : 'Player', width: '150px', align: 'left' }
                    ]
                },
                {
                    title: typeof t === 'function' ? t('ui.team_performance.weekly_avg_game', 'Weekly Avg/Game') : 'Weekly Avg/Game',
                    columns: weeks.map((week, index) => ({
                        title: `${typeof t === 'function' ? t('match_day_label', 'Week') : 'Week'} ${index + 1}`,
                        width: '80px',
                        align: 'center'
                    }))
                },
                {
                    title: typeof t === 'function' ? t('ui.win_percentage.totals', 'Totals') : 'Totals',
                    columns: [
                        { title: typeof t === 'function' ? t('ui.team_performance.total_score', 'Total Score') : 'Total Score', width: '100px', align: 'center' },
                        { title: typeof t === 'function' ? t('games', 'Games') : 'Games', width: '80px', align: 'center' },
                        { title: typeof t === 'function' ? t('ui.team_performance.avg_per_game', 'Avg/Game') : 'Avg/Game', width: '100px', align: 'center' }
                    ]
                }
            ],
            data: tableRows,
            row_metadata: rowMetadata,
            config: {
                striped: true,
                hover: true,
                compact: true,
                stickyHeader: true
            }
        };

        // Check if container exists
        const tableContainer = document.getElementById('team-performance-table');
        if (!tableContainer) {
            console.error('Table container not found!');
            return;
        }

        createTableBootstrap3('team-performance-table', tableData, {
            disablePositionCircle: true,
            enableSpecialRowStyling: true
        });
    }

    renderChart(data) {
        const chartContainer = document.getElementById(this.chartContainerId);
        if (!chartContainer) {
            console.error(`${this.containerId}: Chart container not found`);
            return;
        }

        if (typeof createLineChart !== 'function') {
            console.error('createLineChart function not available');
            return;
        }

        // Extract data from SeriesData format
        const performanceData = data.performance_data;
        const labels = data.weeks;
        
        // Convert SeriesData format to chart format
        const chartData = {};
        
        // Process each player/team in the performance data
        Object.keys(performanceData.data).forEach(playerName => {
            const playerData = performanceData.data[playerName];
            // Filter out null/undefined values for chart display
            chartData[playerName] = playerData.map(value => 
                value === null || value === undefined ? null : value
            );
        });

        // Create chart using existing function
        createLineChart(
            chartData,
            Object.keys(chartData),
            this.chartContainerId,
            (typeof t === 'function' ? t('ui.team_performance.trends', 'Player Performance Trends') : 'Player Performance Trends'),
            labels,
            false, // don't invert Y axis
            'auto' // auto Y-axis range
        );
    }

    renderError(message) {
        if (this.container) {
            this.container.innerHTML = `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>${typeof t === 'function' ? t('block.team_performance.title', 'Team Performance Analysis') : 'Team Performance Analysis'}</h5>
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
