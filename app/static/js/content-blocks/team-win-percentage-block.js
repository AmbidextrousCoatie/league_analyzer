class TeamWinPercentageBlock {
    constructor() {
        this.containerId = 'team-win-percentage';
        this.chartContainerId = 'team-win-percentage-chart';
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
            
            
            if (!data || !data.win_percentage_data || !data.win_percentage_data.data || Object.keys(data.win_percentage_data.data).length === 0) {
                this.renderError(typeof t === 'function' ? t('no_data', 'No win percentage data available for the selected team.') : 'No win percentage data available for the selected team.');
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
                        <h5>${data.team} - ${typeof t === 'function' ? t('ui.win_percentage.title', 'Win Percentage Analysis') : 'Win Percentage Analysis'}</h5>
                        <p class="mb-0 text-muted">${typeof t === 'function' ? t('ui.win_percentage.description', 'Individual player win percentages and team performance') : 'Individual player win percentages and team performance'}</p>
                    </div>
                    <div class="card-body">
                        <!-- Win Percentage Table -->
                        <div class="row mb-4">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h6>${typeof t === 'function' ? t('ui.win_percentage.individual', 'Individual Player Win Percentages') : 'Individual Player Win Percentages'}</h6>
                                        <p class="mb-0 text-muted small">${typeof t === 'function' ? t('ui.win_percentage.individual_desc', 'Player win percentages per week with totals') : 'Player win percentages per week with totals'}</p>
                                    </div>
                                    <div class="card-body">
                                        <div id="team-win-percentage-table"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Win Percentage Chart -->
                        <div class="row">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h6>${typeof t === 'function' ? t('ui.win_percentage.trends', 'Win Percentage Trends') : 'Win Percentage Trends'}</h6>
                                        <p class="mb-0 text-muted small">${typeof t === 'function' ? t('ui.win_percentage.trends_desc', 'Individual player win percentages over time') : 'Individual player win percentages over time'}</p>
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
            this.createWinPercentageTable(data);
            
            // Render the chart
            this.renderChart(data);
            
        } catch (error) {
            console.error('Error rendering team win percentage analysis:', error);
            this.renderError(typeof t === 'function' ? t('error_loading_data', 'Failed to load team win percentage analysis data') : 'Failed to load team win percentage analysis data');
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

    createWinPercentageTable(data) {
        if (typeof createTableBootstrap3 !== 'function') {
            console.error('createTableBootstrap3 function not available');
            return;
        }


        // Extract data from SeriesData format
        const winPercentageData = data.win_percentage_data;
        const weeks = data.weeks;
        
        // Convert SeriesData format to array format for Bootstrap Table 3
        const tableRows = [];
        const teamKey = `${data.team} (Team)`;
        
        // Process individual players first (excluding team)
        Object.keys(winPercentageData.data).forEach(playerName => {
            if (playerName === teamKey) return; // Skip team for now
            
            const playerData = winPercentageData.data[playerName];
            const total = winPercentageData.total[playerName] || 0;
            const average = winPercentageData.average[playerName] || 0;
            
            // Create array row: [player, week1, week2, ..., total_wins, total_matches, total_win_pct]
            const tableRow = [playerName];
            
            // Add week data
            weeks.forEach((week, index) => {
                const weekValue = playerData[index];
                tableRow.push(weekValue === null || weekValue === undefined ? '-' : weekValue);
            });
            
            // Add totals (now correctly calculated from backend)
            const totalMatches = winPercentageData.counts ? winPercentageData.counts[playerName] : 0;
            tableRow.push(total);           // total_wins
            tableRow.push(totalMatches);    // total_matches (actual number of matches)
            tableRow.push(average);         // total_win_pct
            
            tableRows.push(tableRow);
        });
        
        // Add team as the last row
        if (winPercentageData.data[teamKey]) {
            const teamData = winPercentageData.data[teamKey];
            const teamTotal = winPercentageData.total[teamKey] || 0;
            const teamAverage = winPercentageData.average[teamKey] || 0;
            
            // Create array row for team: [player, week1, week2, ..., total_wins, total_matches, total_win_pct]
            const teamRow = [teamKey];
            
            // Add week data
            weeks.forEach((week, index) => {
                const weekValue = teamData[index];
                teamRow.push(weekValue === null || weekValue === undefined ? '-' : weekValue);
            });
            
            // Add totals
            const teamTotalMatches = winPercentageData.counts ? winPercentageData.counts[teamKey] : 0;
            teamRow.push(teamTotal);        // total_wins
            teamRow.push(teamTotalMatches); // total_matches (actual number of matches)
            teamRow.push(teamAverage);      // total_win_pct
            
            tableRows.push(teamRow);
        }

        // Create row metadata for styling (team row should be bold)
        const rowMetadata = [];
        tableRows.forEach((row, index) => {
            if (row[0] === teamKey) {
                // Team row - make it bold
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
            title: `${data.team} - ${typeof t === 'function' ? t('ui.win_percentage.title', 'Win Percentages') : 'Win Percentages'}`,
            description: typeof t === 'function' ? t('ui.win_percentage.individual_desc', 'Individual player win percentages per week with totals') : 'Individual player win percentages per week with totals',
            columns: [
                {
                    title: 'Player',
                    columns: [
                        { title: typeof t === 'function' ? t('ui.win_percentage.player', 'Player') : 'Player', width: '150px', align: 'left' }
                    ]
                },
                {
                    title: typeof t === 'function' ? t('ui.win_percentage.weekly', 'Weekly Win %') : 'Weekly Win %',
                    columns: weeks.map((week, index) => ({
                        title: `Week ${index + 1}`,
                        width: '80px',
                        align: 'center'
                    }))
                },
                {
                    title: typeof t === 'function' ? t('ui.win_percentage.totals', 'Totals') : 'Totals',
                    columns: [
                        { title: typeof t === 'function' ? t('ui.win_percentage.total_wins', 'Total Wins') : 'Total Wins', width: '100px', align: 'center' },
                        { title: typeof t === 'function' ? t('ui.win_percentage.total_matches', 'Total Matches') : 'Total Matches', width: '100px', align: 'center' },
                        { title: typeof t === 'function' ? t('ui.win_percentage.win_percentage', 'Win %') : 'Win %', width: '80px', align: 'center' }
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

        createTableBootstrap3('team-win-percentage-table', tableData, {
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
        const winPercentageData = data.win_percentage_data;
        const labels = data.weeks;
        
        // Convert SeriesData format to chart format
        const chartData = {};
        
        // Process each player/team in the win percentage data
        Object.keys(winPercentageData.data).forEach(playerName => {
            const playerData = winPercentageData.data[playerName];
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
            typeof t === 'function' ? t('ui.win_percentage.trends', 'Player Win Percentage Trends') : 'Player Win Percentage Trends',
            labels,
            false, // don't invert Y axis
            'exact' // use exact Y-axis range for percentages (0-100)
        );
    }

    renderError(message) {
        if (this.container) {
            this.container.innerHTML = `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>${typeof t === 'function' ? t('ui.win_percentage.title', 'Team Win Percentage Analysis') : 'Team Win Percentage Analysis'}</h5>
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
