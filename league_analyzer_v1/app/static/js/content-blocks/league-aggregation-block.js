/**
 * LeagueAggregationBlock - Shows league-wide aggregated data over all years
 * Displays when: League is selected but no Season
 */
class LeagueAggregationBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'league-aggregation',
            containerId: 'leagueAggregationContainer',
            dataEndpoint: null, // Multiple endpoints used
            requiredFilters: ['league'],
            title: typeof t === 'function' ? t('ui.league.aggregation.title', 'League Aggregation') : 'League Aggregation'
        });
        this.dependencies = ['league'];
        this.container = document.getElementById(this.containerId);
    }

    async render(state = {}) {
        try {
            // Check if required dependencies are met and no season is selected
            if (!this.shouldRender(state)) {
                this.hide();
                return;
            }

            this.show();
            const html = this.generateHTML(state);
            this.container.innerHTML = html;
            
            // Load aggregated data
            await this.loadAggregatedData(state);
            
            console.log('league-aggregation: League aggregation rendered');
        } catch (error) {
            console.error('Error rendering league aggregation:', error);
            this.container.innerHTML = this.renderError('Failed to load league aggregation data');
        }
    }

    shouldRender(state) {
        // Show only when league is selected but no season (handle both null and string "null")
        const hasLeague = state.league && state.league !== '' && state.league !== 'null';
        const hasSeason = state.season && state.season !== '' && state.season !== 'null';
        const shouldShow = hasLeague && !hasSeason;
        console.log(`LeagueAggregationBlock shouldRender: league="${state.league}", season="${state.season}", result=${shouldShow}`);
        return shouldShow;
    }

    generateHTML(state) {
        const leagueName = state.league_long || state.league || '';
        return `
            <div class="card mb-4">
                <div class="card-header">
                    <h5>${leagueName} - ${typeof t === 'function' ? t('ui.league.all_time', 'All-Time Statistics') : 'All-Time Statistics'}</h5>
                    <p class="mb-0 text-muted">${typeof t === 'function' ? t('ui.league.performance_all_seasons', 'League performance across all seasons') : 'League performance across all seasons'}</p>
                </div>
                <div class="card-body">
                    <!-- League Averages Section -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>${typeof t === 'function' ? t('ui.league.averages_over_time', 'League Averages Over Time') : 'League Averages Over Time'}</h6>
                                </div>
                                <div class="card-body">
                                    <div id="chartLeagueAverages" style="height: 300px;"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>${typeof t === 'function' ? t('ui.league.points_to_win', 'League Points to Win') : 'League Points to Win'}</h6>
                                </div>
                                <div class="card-body">
                                    <div id="chartPointsToWin" style="height: 300px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- High Performance Tables -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>${typeof t === 'function' ? t('top_team_performances', 'Top Team Performances') : 'Top Team Performances'}</h6>
                                </div>
                                <div class="card-body">
                                    <div id="tableTopTeams"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>${typeof t === 'function' ? t('top_individual_performances', 'Top Individual Performances') : 'Top Individual Performances'}</h6>
                                </div>
                                <div class="card-body">
                                    <div id="tableTopIndividuals"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Record Games Section -->
                    <div class="row">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>${typeof t === 'function' ? t('record_individual_games', 'Record Individual Games') : 'Record Individual Games'}</h6>
                                </div>
                                <div class="card-body">
                                    <div id="tableRecordIndividualGames"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>${typeof t === 'function' ? t('record_team_games', 'Record Team Games') : 'Record Team Games'}</h6>
                                </div>
                                <div class="card-body">
                                    <div id="tableRecordTeamGames"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadAggregatedData(state) {
        const { league } = state;
        
        try {
            // Load all aggregated data in parallel
            const [averagesData, pointsData, topTeamsData, topIndividualsData, recordIndividualGamesData, recordTeamGamesData] = await Promise.all([
                this.loadLeagueAverages(league),
                this.loadPointsToWin(league),
                this.loadTopTeams(league),
                this.loadTopIndividuals(league),
                this.loadRecordIndividualGames(league),
                this.loadRecordTeamGames(league)
            ]);

            // Create charts and tables
            this.createLeagueAveragesChart(averagesData);
            this.createPointsToWinChart(pointsData);
            this.createTopTeamsTable(topTeamsData);
            this.createTopIndividualsTable(topIndividualsData);
            this.createRecordIndividualGamesTable(recordIndividualGamesData);
            this.createRecordTeamGamesTable(recordTeamGamesData);

        } catch (error) {
            console.error('Error loading aggregated data:', error);
        }
    }

    async loadLeagueAverages(league) {
        // TODO: Create endpoint for league averages over time
        const response = await fetchWithDatabase(`/league/get_league_averages_history?league=${league}`);
        return await response.json();
    }

    async loadPointsToWin(league) {
        try {
            //console.log(`DEBUG: loadPointsToWin called for league: ${league}`);
            const url = `/league/get_points_to_win_history?league=${league}`;
            //console.log(`DEBUG: Fetching from: ${url}`);
            
            const response = await fetchWithDatabase(url);
            //console.log(`DEBUG: Response status: ${response.status}, ok: ${response.ok}`);
            
            if (!response.ok) {
                console.error(`DEBUG: Response not ok: ${response.status} ${response.statusText}`);
                return null;
            }
            
            const data = await response.json();
            //console.log(`DEBUG: Points to win data received:`, data);
            return data;
        } catch (error) {
            //console.error('DEBUG: Error in loadPointsToWin:', error);
            return null;
        }
    }

    async loadTopTeams(league) {
        // TODO: Create endpoint for top team performances
        const response = await fetchWithDatabase(`/league/get_top_team_performances?league=${league}`);
        return await response.json();
    }

    async loadTopIndividuals(league) {
        try {
            //console.log(`DEBUG: loadTopIndividuals called for league: ${league}`);
            const url = `/league/get_top_individual_performances?league=${league}`;
            c//onsole.log(`DEBUG: Fetching from: ${url}`);
            
            const response = await fetchWithDatabase(url);
            //console.log(`DEBUG: Response status: ${response.status}, ok: ${response.ok}`);
            
            if (!response.ok) {
                console.error(`DEBUG: Response not ok: ${response.status} ${response.statusText}`);
                const errorText = await response.text();
                console.error(`DEBUG: Error response body: ${errorText}`);
                return null;
            }
            
            const data = await response.json();
            //console.log(`DEBUG: Top individuals data received:`, data);
            c//onsole.log(`DEBUG: Data structure - columns: ${data.columns ? data.columns.length : 'none'}, data: ${data.data ? data.data.length : 'none'} rows`);
            
            return data;
        } catch (error) {
            console.error('DEBUG: Error in loadTopIndividuals:', error);
            return null;
        }
    }

    async loadRecordIndividualGames(league) {
        try {
            //console.log(`DEBUG: loadRecordIndividualGames called for league: ${league}`);
            const url = `/league/get_record_individual_games?league=${league}`;
            //console.log(`DEBUG: Fetching from: ${url}`);
            
            const response = await fetchWithDatabase(url);
            //console.log(`DEBUG: Response status: ${response.status}, ok: ${response.ok}`);
            
            if (!response.ok) {
                console.error(`DEBUG: Response not ok: ${response.status} ${response.statusText}`);
                return null;
            }
            
            const data = await response.json();
            //console.log(`DEBUG: Record individual games data received:`, data);
            return data;
        } catch (error) {
            console.error('DEBUG: Error in loadRecordIndividualGames:', error);
            return null;
        }
    }

    async loadRecordTeamGames(league) {
        try {
            //console.log(`DEBUG: loadRecordTeamGames called for league: ${league}`);
            const url = `/league/get_record_team_games?league=${league}`;
            //console.log(`DEBUG: Fetching from: ${url}`);
            
            const response = await fetchWithDatabase(url);
            //console.log(`DEBUG: Response status: ${response.status}, ok: ${response.ok}`);
            
            if (!response.ok) {
                console.error(`DEBUG: Response not ok: ${response.status} ${response.statusText}`);
                return null;
            }
            
            const data = await response.json();
            //console.log(`DEBUG: Record team games data received:`, data);
            return data;
        } catch (error) {
            console.error('DEBUG: Error in loadRecordTeamGames:', error);
            return null;
        }
    }

    async loadRecordGames(league) {
        // Legacy method - now returns individual games
        return this.loadRecordIndividualGames(league);
    }

    createLeagueAveragesChart(data) {
        // Create line chart showing league averages over seasons
        console.log('createLeagueAveragesChart called with data:', data);
        if (typeof createLineChart === 'function' && data && data.data) {
            console.log('Creating league averages chart with data:', data.data);
            
            createLineChart(
                data.data,                              // {League Average: [240.1, 235.8, ...]}
                Object.keys(data.data),                 // ['League Average']
                'chartLeagueAverages',                  // container ID
                'League Average by Season',             // title
                data.labels || data.seasons,            // x-axis labels
                false,                                  // invertYAxis
                'auto'                                  // yAxisRange
            );
        } else {
            console.warn('Cannot create league averages chart:', {
                hasCreateLineChart: typeof createLineChart === 'function',
                hasData: !!data,
                hasDataProperty: data && !!data.data,
                data: data
            });
        }
    }

    createPointsToWinChart(data) {
        // Create line chart showing points needed to win each season
        console.log('createPointsToWinChart called with data:', data);
        if (typeof createLineChart === 'function' && data && data.data) {
            console.log('Creating points to win chart with data:', data.data);
            console.log('Chart container ID: chartPointsToWin');
            console.log('Labels:', data.labels || data.seasons);
            
            // Check if container exists
            const container = document.getElementById('chartPointsToWin');
            console.log('Container found:', !!container);
            
            createLineChart(
                data.data,                              // {Points to Win: [169.2, 176.3, ...]}
                Object.keys(data.data),                 // ['Points to Win']
                'chartPointsToWin',                     // container ID
                'League Points Needed to Win by Season', // title
                data.labels || data.seasons,            // x-axis labels
                false,                                  // invertYAxis
                'auto'                                  // yAxisRange
            );
        } else {
            console.warn('Cannot create points to win chart:', {
                hasCreateLineChart: typeof createLineChart === 'function',
                hasData: !!data,
                hasDataProperty: data && !!data.data,
                data: data
            });
        }
    }

    createTopTeamsTable(data) {
        // Create table for top team performances
        if (typeof createTableTabulator === 'function' && data) {
            createTableTabulator('tableTopTeams', data, {
                disablePositionCircle: true, // No color circles for top performances ranking
                enableSpecialRowStyling: true,
                tooltips: true
            });
        }
    }

    createTopIndividualsTable(data) {
        // Create table for top individual performances
        console.log(`DEBUG: createTopIndividualsTable called with data:`, data);
        console.log(`DEBUG: createTableTabulator function available: ${typeof createTableTabulator === 'function'}`);
        console.log(`DEBUG: Data is truthy: ${!!data}`);
        
        if (typeof createTableTabulator === 'function' && data) {
            console.log(`DEBUG: Creating top individuals table with ${data.data ? data.data.length : 'unknown'} rows`);
            createTableTabulator('tableTopIndividuals', data, {
                disablePositionCircle: true, // Individual players don't need color circles
                enableSpecialRowStyling: true,
                tooltips: true
            });
            console.log(`DEBUG: Top individuals table creation completed`);
        } else {
            console.warn(`DEBUG: Cannot create top individuals table - function available: ${typeof createTableTabulator === 'function'}, data: ${!!data}`);
        }
    }

    createRecordIndividualGamesTable(data) {
        // Create table for record individual games
        console.log(`DEBUG: createRecordIndividualGamesTable called with data:`, data);
        if (typeof createTableTabulator === 'function' && data) {
            console.log(`DEBUG: Creating record individual games table with ${data.data ? data.data.length : 'unknown'} rows`);
            createTableTabulator('tableRecordIndividualGames', data, {
                disablePositionCircle: true, // Record games don't need position circles
                enableSpecialRowStyling: true,
                tooltips: true
            });
            console.log(`DEBUG: Record individual games table creation completed`);
        } else {
            console.warn(`DEBUG: Cannot create record individual games table - function available: ${typeof createTableTabulator === 'function'}, data: ${!!data}`);
        }
    }

    createRecordTeamGamesTable(data) {
        // Create table for record team games
        console.log(`DEBUG: createRecordTeamGamesTable called with data:`, data);
        if (typeof createTableTabulator === 'function' && data) {
            console.log(`DEBUG: Creating record team games table with ${data.data ? data.data.length : 'unknown'} rows`);
            createTableTabulator('tableRecordTeamGames', data, {
                disablePositionCircle: true, // Record games don't need position circles
                enableSpecialRowStyling: true,
                tooltips: true
            });
            console.log(`DEBUG: Record team games table creation completed`);
        } else {
            console.warn(`DEBUG: Cannot create record team games table - function available: ${typeof createTableTabulator === 'function'}, data: ${!!data}`);
        }
    }

    createRecordGamesTable(data) {
        // Legacy method - now creates individual games table
        return this.createRecordIndividualGamesTable(data);
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
        return `<div class="alert alert-danger">${message}</div>`;
    }
}