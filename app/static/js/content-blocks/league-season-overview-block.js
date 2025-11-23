/**
 * LeagueSeasonOverviewBlock - Shows league+season specific data
 * Displays when: League and Season are selected but no Week
 */
class LeagueSeasonOverviewBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'league-season-overview',
            containerId: 'leagueSeasonOverviewContainer',
            dataEndpoint: null, // Multiple endpoints used
            requiredFilters: ['league', 'season'],
            title: typeof t === 'function' ? t('ui.league.season_overview.title', 'League Season Overview') : 'League Season Overview'
        });
        this.dependencies = ['league', 'season'];
        this.container = document.getElementById(this.containerId);
    }

    async render(state = {}) {
        try {
            // Check if required dependencies are met and no week is selected
            if (!this.shouldRender(state)) {
                this.hide();
                return;
            }

            this.show();
            const html = this.generateHTML(state);
            this.container.innerHTML = html;
            
            // Load season-specific data
            await this.loadSeasonData(state);
            
            console.log('league-season-overview: League season overview rendered');
        } catch (error) {
            console.error('Error rendering league season overview:', error);
            this.container.innerHTML = this.renderError('Failed to load league season overview');
        }
    }

    shouldRender(state) {
        // Show only when league and season are selected but no week AND no team (handle string "null")
        const hasLeague = state.league && state.league !== '' && state.league !== 'null';
        const hasSeason = state.season && state.season !== '' && state.season !== 'null';
        const hasWeek = state.week && state.week !== '' && state.week !== 'null';
        const hasTeam = state.team && state.team !== '' && state.team !== 'null';
        const shouldShow = hasLeague && hasSeason && !hasWeek && !hasTeam;
        console.log(`LeagueSeasonOverviewBlock shouldRender: league="${state.league}", season="${state.season}", week="${state.week}", team="${state.team}", result=${shouldShow}`);
        return shouldShow;
    }

    generateHTML(state) {
        return `
            <div class="card mb-4">
                <div class="card-header">
                    <h5>${state.league} - ${typeof t === 'function' ? t('season', 'Season') : 'Season'} ${state.season}</h5>
                    <p class="mb-0 text-muted">${typeof t === 'function' ? t('season_overview', 'Season Overview') : 'Season Overview'}</p>
                </div>
                <div class="card-body">
                    <!-- 1st Row: League Standings (Full Width) -->
                    <div class="row mb-4">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">
                                    <h6>${typeof t === 'function' ? t('league_standings', 'League Standings') : 'League Standings'}</h6>
                                    <p class="mb-0 text-muted small">${typeof t === 'function' ? t('standings', 'Standings') : 'Standings'}</p>
                                </div>
                                <div class="card-body">
                                    <div id="leagueStandingsTable"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 2nd Row: Timetable + Position in Season Progress -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>${typeof t === 'function' ? t('season_timetable', 'Season Timetable') : 'Season Timetable'}</h6>
                                    <p class="mb-0 text-muted small">${typeof t === 'function' ? t('match_schedule', 'Match Schedule') : 'Match Schedule'}</p>
                                </div>
                                <div class="card-body">
                                    <div id="seasonTimetable"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>${typeof t === 'function' ? t('position_in_season_progress', 'Position in Season Progress') : 'Position in Season Progress'}</h6>
                                </div>
                                <div class="card-body">
                                    <div id="chartTeamPositionCumulated" style="height: 300px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 3rd Row: Points per Match Day + Points in Season Progress -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>${typeof t === 'function' ? t('points_per_match_day', 'Points per Match Day') : 'Points per Match Day'}</h6>
                                </div>
                                <div class="card-body">
                                    <div id="chartTeamPointsWeekly" style="height: 300px;"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>${typeof t === 'function' ? t('points_in_season_progress', 'Points in Season Progress') : 'Points in Season Progress'}</h6>
                                </div>
                                <div class="card-body">
                                    <div id="chartTeamPointsCumulated" style="height: 300px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- 4th Row: Team vs Team Comparison Matrix (Full Width) -->
                    <div class="row mb-4">
                        <div class="col-12">
                            <div id="team-vs-team-comparison-inline"></div>
                        </div>
                    </div>

                    <!-- 5th Row: Individual Averages (Full Width) -->
                    <div class="row">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">
                                    <h6>${typeof t === 'function' ? t('individual_averages', 'Individual Averages') : 'Individual Averages'}</h6>
                                    <p class="mb-0 text-muted small">${typeof t === 'function' ? t('individual_performance', 'Individual Performance') : 'Individual Performance'}</p>
                                </div>
                                <div class="card-body">
                                    <div id="individualAveragesTable"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadSeasonData(state) {
        const { league, season } = state;
        
        try {
            // Load existing endpoints first, handle missing ones gracefully
            const dataPromises = [];
            
            // Always try to load league standings (existing endpoint)
            dataPromises.push(
                this.loadLeagueStandings(league, season).catch(error => {
                    console.warn('Could not load league standings:', error);
                    return null;
                })
            );
            
            // Always try to load team points (existing endpoint)
            dataPromises.push(
                this.loadTeamPoints(league, season).catch(error => {
                    console.warn('Could not load team points:', error);
                    return null;
                })
            );
            
            // Always try to load team positions (existing endpoint)
            dataPromises.push(
                this.loadTeamPositions(league, season).catch(error => {
                    console.warn('Could not load team positions:', error);
                    return null;
                })
            );
            
            // Try optional endpoints with fallbacks
            dataPromises.push(
                this.loadTimetable(league, season).catch(error => {
                    console.warn('Timetable endpoint not available, creating placeholder');
                    return this.createMockTimetable(season);
                })
            );
            
            dataPromises.push(
                this.loadIndividualAverages(league, season).catch(error => {
                    console.warn('Individual averages endpoint not available');
                    return null;
                })
            );

            // Load team vs team comparison
            dataPromises.push(
                this.loadTeamVsTeamComparison(league, season).catch(error => {
                    console.warn('Team vs team comparison endpoint not available');
                    return null;
                })
            );

            const [standingsData, pointsData, positionsData, timetableData, averagesData, teamVsTeamData] = await Promise.all(dataPromises);

            // Create components with available data
            if (timetableData) this.createTimetable(timetableData);
            if (standingsData) this.createStandingsTable(standingsData);
            if (averagesData) this.createAveragesTable(averagesData);
            if (pointsData) {
                this.createPointsChart(pointsData);
                this.createWeeklyPointsChart(pointsData);
            }
            if (positionsData) this.createPositionsChart(positionsData);
            if (teamVsTeamData) this.createTeamVsTeamComparison(teamVsTeamData);

        } catch (error) {
            console.error('Error loading season data:', error);
        }
    }

    async loadTimetable(league, season) {
        // TODO: Create endpoint for season timetable
        const response = await fetchWithDatabase(`/league/get_season_timetable?league=${league}&season=${season}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    }

    async loadLeagueStandings(league, season) {
        // Use existing endpoint
        const response = await fetchWithDatabase(`/league/get_league_history?season=${season}&league=${league}`);
        return await response.json();
    }

    async loadIndividualAverages(league, season) {
        // TODO: Create endpoint for individual averages
        const response = await fetchWithDatabase(`/league/get_individual_averages?league=${league}&season=${season}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    }

    createMockTimetable(season) {
        // Create a mock timetable with placeholder data
        const weeks = [];
        for (let i = 1; i <= 10; i++) {
            weeks.push({
                week: i,
                date: 'TBD',
                completed: false
            });
        }
        return { weeks };
    }

    async loadTeamPoints(league, season) {
        // Use existing endpoint
        const response = await fetchWithDatabase(`/league/get_team_points?season=${season}&league=${league}`);
        return await response.json();
    }

    async loadTeamPositions(league, season) {
        // Use existing endpoint
        const response = await fetchWithDatabase(`/league/get_team_positions?season=${season}&league=${league}`);
        return await response.json();
    }

    async loadWeeklyPoints(league, season) {
        // Use same data as team points for scatter plot
        const response = await fetchWithDatabase(`/league/get_team_points?season=${season}&league=${league}`);
        return await response.json();
    }

    createTimetable(data) {
        console.log('DEBUG: createTimetable called with data:', data);
        const container = document.getElementById('seasonTimetable');
        if (!container || !data) {
            console.warn('No container or data for timetable');
            return;
        }

        // Use Tabulator renderer for structured table data
        if (typeof createTableTabulator === 'function' && data.columns && data.data) {
            console.log('Creating timetable using Tabulator');
            createTableTabulator('seasonTimetable', data, { 
                disablePositionCircle: true,
                enableSpecialRowStyling: true,
                tooltips: true
            });
        } else {
            console.warn('createTableTabulator not available or invalid data format, falling back');
            // Fallback for legacy format
            let html = '<div class="alert alert-info">Timetable data not available in expected format</div>';
            container.innerHTML = html;
        }
    }

    createStandingsTable(data) {
        if (typeof createTableTabulator === 'function' && data?.columns) {
            createTableTabulator('leagueStandingsTable', data, {
                disablePositionCircle: false,
                enableSpecialRowStyling: true,
                tooltips: true
            });
        }
    }

    createAveragesTable(data) {
        if (typeof createTableTabulator === 'function' && data?.columns) {
            createTableTabulator('individualAveragesTable', data, {
                disablePositionCircle: true,
                enableSpecialRowStyling: true,
                tooltips: true
            });
        }
    }

    createPointsChart(data) {
        console.log('DEBUG: createPointsChart called with data:', data);
        
        if (typeof createLineChart === 'function' && data && data.data_accumulated) {
            const firstTeamData = Object.values(data.data_accumulated)[0];
            if (firstTeamData && Array.isArray(firstTeamData)) {
                const numWeeks = firstTeamData.length;
                const labels = Array.from({length: numWeeks}, (_, i) => `Week ${i + 1}`);
                
                createLineChart(
                    data.data_accumulated,
                    data.sorted_by_total,
                    'chartTeamPointsCumulated',
                    'Points in Season Progress',
                    labels,
                    false,
                    'auto'
                );
            } else {
                console.warn('createPointsChart: data.data_accumulated does not contain valid array data');
            }
        } else {
            console.warn('createPointsChart: createLineChart not available or data.data_accumulated missing', {
                hasCreateLineChart: typeof createLineChart === 'function',
                hasData: !!data,
                hasDataAccumulated: data && !!data.data_accumulated
            });
        }
    }

    createPositionsChart(data) {
        console.log('DEBUG: createPositionsChart called with data:', data);
        
        if (typeof createLineChart === 'function' && data && data.data) {
            const firstTeamData = Object.values(data.data)[0];
            if (firstTeamData && Array.isArray(firstTeamData)) {
                const numWeeks = firstTeamData.length;
                const labels = Array.from({length: numWeeks}, (_, i) => `Week ${i + 1}`);
                
                createLineChart(
                    data.data,
                    data.sorted_by_best || data.sorted_by_total || Object.keys(data.data),
                    'chartTeamPositionCumulated',
                    'Position in Season Progress',
                    labels,
                    true, // reverse Y axis for positions
                    'exact' // use exact Y-axis limits for positions
                );
            } else {
                console.warn('createPositionsChart: data.data does not contain valid array data');
            }
        } else {
            console.warn('createPositionsChart: createLineChart not available or data.data missing', {
                hasCreateLineChart: typeof createLineChart === 'function',
                hasData: !!data,
                hasDataProperty: data && !!data.data
            });
        }
    }

    createWeeklyPointsChart(data) {
        console.log('DEBUG: createWeeklyPointsChart called with data:', data);
        
        if (typeof createScatterChartMultiAxis === 'function' && data && data.data) {
            const firstTeamData = Object.values(data.data)[0];
            if (firstTeamData && Array.isArray(firstTeamData)) {
                const numWeeks = firstTeamData.length;
                const labels = Array.from({length: numWeeks}, (_, i) => `Week ${i + 1}`);
                
                createScatterChartMultiAxis(
                    data.data,
                    data.sorted_by_total,
                    'chartTeamPointsWeekly',
                    'Points per Match Day',
                    labels
                );
            } else {
                console.warn('createWeeklyPointsChart: data.data does not contain valid array data');
            }
        } else {
            console.warn('createWeeklyPointsChart: createScatterChartMultiAxis not available or data.data missing', {
                hasCreateScatterChartMultiAxis: typeof createScatterChartMultiAxis === 'function',
                hasData: !!data,
                hasDataProperty: data && !!data.data
            });
        }
    }

    async loadTeamVsTeamComparison(league, season) {
        const url = new URL('/league/get_team_vs_team_comparison', window.location.origin);
        url.searchParams.append('league', league);
        url.searchParams.append('season', season);
        
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

    createTeamVsTeamComparison(data) {
        if (!data || !data.columns || !data.data) {
            console.warn('No team vs team comparison data available');
            return;
        }

        const container = document.getElementById('team-vs-team-comparison-inline');
        if (!container) {
            console.error('Team vs team comparison container not found');
            return;
        }

        // Create the team vs team comparison card
        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h6>${data.title || 'Team vs Team Comparison Matrix'}</h6>
                    <p class="mb-0 text-muted small">${data.description || 'Matrix showing team performance against each opponent'}</p>
                </div>
                <div class="card-body">
                    <div id="team-vs-team-comparison-table-inline"></div>
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
                                                <div class="heat-map-legend me-2" style="background: #d9596a; width: 20px; height: 20px;"></div>
                                                <span class="me-2">High:</span>
                                                <div class="heat-map-legend" style="background: #1b8da7; width: 20px; height: 20px;"></div>
                                            </div>
                                            <small class="text-muted">Range: ${data.metadata?.score_range?.min || 'N/A'} - ${data.metadata?.score_range?.max || 'N/A'}</small>
                                        </div>
                                        <div class="col-md-6">
                                            <h6>Points Heat Map</h6>
                                            <div class="d-flex align-items-center">
                                                <span class="me-2">Low:</span>
                                                <div class="heat-map-legend me-2" style="background: #d9596a; width: 20px; height: 20px;"></div>
                                                <span class="me-2">High:</span>
                                                <div class="heat-map-legend" style="background: #1b8da7; width: 20px; height: 20px;"></div>
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

        // Create table using Tabulator
        if (typeof createTableTabulator === 'function') {
            createTableTabulator('team-vs-team-comparison-table-inline', data, {
                disablePositionCircle: true,
                enableSpecialRowStyling: true,
                tooltips: true
            });
        } else {
            console.error('createTableTabulator function not available');
        }
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