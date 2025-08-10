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
            title: 'League Season Overview'
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
        // Show only when league and season are selected but no week (handle string "null")
        const hasLeague = state.league && state.league !== '' && state.league !== 'null';
        const hasSeason = state.season && state.season !== '' && state.season !== 'null';
        const hasWeek = state.week && state.week !== '' && state.week !== 'null';
        const shouldShow = hasLeague && hasSeason && !hasWeek;
        console.log(`LeagueSeasonOverviewBlock shouldRender: league="${state.league}", season="${state.season}", week="${state.week}", result=${shouldShow}`);
        return shouldShow;
    }

    generateHTML(state) {
        return `
            <div class="card mb-4">
                <div class="card-header">
                    <h5>${state.league} - Season ${state.season}</h5>
                    <p class="mb-0 text-muted">Season overview and timetable</p>
                </div>
                <div class="card-body">
                    <!-- Timetable Section -->
                    <div class="row mb-4">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">
                                    <h6>Season Timetable</h6>
                                    <p class="mb-0 text-muted small">Match day schedule and completion status</p>
                                </div>
                                <div class="card-body">
                                    <div id="seasonTimetable"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- League Standings and Charts Row -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>League Standings</h6>
                                </div>
                                <div class="card-body">
                                    <div id="leagueStandingsTable"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>Individual Averages</h6>
                                </div>
                                <div class="card-body">
                                    <div id="individualAveragesTable"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Charts Section -->
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>Points in Season Progress</h6>
                                </div>
                                <div class="card-body">
                                    <div id="chartTeamPointsCumulated" style="height: 300px;"></div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h6>Position in Season Progress</h6>
                                </div>
                                <div class="card-body">
                                    <div id="chartTeamPositionCumulated" style="height: 300px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Points per Match Day Chart -->
                    <div class="row">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">
                                    <h6>Points per Match Day</h6>
                                </div>
                                <div class="card-body">
                                    <div id="chartTeamPointsWeekly" style="height: 400px;"></div>
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

            const [standingsData, pointsData, positionsData, timetableData, averagesData] = await Promise.all(dataPromises);

            // Create components with available data
            if (timetableData) this.createTimetable(timetableData);
            if (standingsData) this.createStandingsTable(standingsData);
            if (averagesData) this.createAveragesTable(averagesData);
            if (pointsData) {
                this.createPointsChart(pointsData);
                this.createWeeklyPointsChart(pointsData);
            }
            if (positionsData) this.createPositionsChart(positionsData);

        } catch (error) {
            console.error('Error loading season data:', error);
        }
    }

    async loadTimetable(league, season) {
        // TODO: Create endpoint for season timetable
        const response = await fetch(`/league/get_season_timetable?league=${league}&season=${season}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    }

    async loadLeagueStandings(league, season) {
        // Use existing endpoint
        const response = await fetch(`/league/get_league_history?season=${season}&league=${league}`);
        return await response.json();
    }

    async loadIndividualAverages(league, season) {
        // TODO: Create endpoint for individual averages
        const response = await fetch(`/league/get_individual_averages?league=${league}&season=${season}`);
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
        const response = await fetch(`/league/get_team_points?season=${season}&league=${league}`);
        return await response.json();
    }

    async loadTeamPositions(league, season) {
        // Use existing endpoint
        const response = await fetch(`/league/get_team_positions?season=${season}&league=${league}`);
        return await response.json();
    }

    async loadWeeklyPoints(league, season) {
        // Use same data as team points for scatter plot
        const response = await fetch(`/league/get_team_points?season=${season}&league=${league}`);
        return await response.json();
    }

    createTimetable(data) {
        const container = document.getElementById('seasonTimetable');
        if (!container || !data) return;

        // Create a visual timetable showing match days and their status
        let html = '<div class="row">';
        
        if (data.weeks) {
            data.weeks.forEach((week, index) => {
                const isCompleted = week.completed || false;
                const statusClass = isCompleted ? 'bg-success text-white' : 'bg-light text-dark';
                const statusIcon = isCompleted ? '✓' : '○';
                
                html += `
                    <div class="col-md-2 col-sm-3 col-4 mb-2">
                        <div class="card ${statusClass}">
                            <div class="card-body text-center py-2">
                                <small><strong>Week ${week.week}</strong></small><br>
                                <small>${week.date || 'TBD'}</small><br>
                                <span class="badge ${isCompleted ? 'badge-light' : 'badge-secondary'}">${statusIcon}</span>
                            </div>
                        </div>
                    </div>
                `;
            });
        }
        
        html += '</div>';
        container.innerHTML = html;
    }

    createStandingsTable(data) {
        if (typeof createTableBootstrap3 === 'function' && data) {
            createTableBootstrap3('leagueStandingsTable', data, {
                disablePositionCircle: false, // League standings should show team colors
                enableSpecialRowStyling: true
            });
        }
    }

    createAveragesTable(data) {
        if (typeof createTableBootstrap3 === 'function' && data) {
            createTableBootstrap3('individualAveragesTable', data, {
                disablePositionCircle: true, // Individual averages don't need team colors
                enableSpecialRowStyling: true
            });
        }
    }

    createPointsChart(data) {
        if (typeof createLineChart === 'function' && data.data_accumulated) {
            const numWeeks = Object.values(data.data_accumulated)[0].length;
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
        }
    }

    createPositionsChart(data) {
        if (typeof createLineChart === 'function' && data.data) {
            const numWeeks = Object.values(data.data)[0].length;
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
        }
    }

    createWeeklyPointsChart(data) {
        if (typeof createScatterChartMultiAxis === 'function' && data.data) {
            const numWeeks = Object.values(data.data)[0].length;
            const labels = Array.from({length: numWeeks}, (_, i) => `Week ${i + 1}`);
            
            createScatterChartMultiAxis(
                data.data,
                data.sorted_by_total,
                'chartTeamPointsWeekly',
                'Points per Match Day',
                labels
            );
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