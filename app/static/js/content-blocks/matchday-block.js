/**
 * MatchDayBlock - Shows week-specific league results and honor scores
 * Displays when: Season + League + Week are selected
 */
class MatchDayBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'matchday',
            containerId: 'matchdayContainer',
            dataEndpoint: '/league/get_league_week_table',
            requiredFilters: ['season', 'league', 'week'],
            title: 'Match Day Results'
        });
        this.dependencies = ['season', 'league', 'week'];
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
            
            // Load match day data
            await this.loadMatchDayData(state);
            
            console.log('matchday: Match day content rendered');
        } catch (error) {
            console.error('Error rendering match day content:', error);
            this.container.innerHTML = this.renderError('Failed to load match day content');
        }
    }

    shouldRender(state) {
        // Show only when season, league, and week are selected but NO team and NO round is selected
        const hasTeam = state.team && state.team !== '' && state.team !== 'null';
        const hasRound = state.round && state.round !== '' && state.round !== 'null';
        return state.season && state.league && state.week && !hasTeam && !hasRound;
    }

    generateHTML(state) {
        const leagueName = state.league_long || state.league || '';
        const season = state.season || '';
        const week = state.week || '';
        
        // Build title with league, season, and week
        const title = week 
            ? `${leagueName} - ${season} - ${typeof t === 'function' ? t('week', 'Week') : 'Week'} ${week}`
            : `${leagueName} - ${season}`;
        
        return `
            <div class="card mb-4">
                <div class="card-header">
                    <h5>${title}</h5>
                </div>
                <div class="card-body">
                    <!-- Content Area -->
                    <div class="row">
                        <div class="col-md-8">
                            <div id="tableLeagueWeek">
                                <div class="text-center py-3">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">${typeof t === 'function' ? t('status.loading_data', 'Loading results...') : 'Loading results...'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div id="honorScores" class="card">
                                <div class="card-header">
                                    <h5>${typeof t === 'function' ? t('honor_scores', 'Honor Scores') : 'Honor Scores'}</h5>
                                </div>
                                <div class="card-body">
                                    <!-- Loading state -->
                                    <div class="text-center py-3">
                                        <div class="spinner-border spinner-border-sm text-primary" role="status">
                                            <span class="visually-hidden">${typeof t === 'function' ? t('status.loading', 'Loading honor scores...') : 'Loading honor scores...'}</span>
                                        </div>
                                    </div>
                                    
                                    <!-- Content will be populated here -->
                                    <div class="mb-3" id="individualScoresSection" style="display: none;">
                                        <h6>${typeof t === 'function' ? t('top_individual_scores', 'Top Individual Scores') : 'Top Individual Scores'}</h6>
                                        <div id="individualScores"></div>
                                    </div>
                                    <div class="mb-3" id="teamScoresSection" style="display: none;">
                                        <h6>${typeof t === 'function' ? t('top_team_scores', 'Top Team Scores') : 'Top Team Scores'}</h6>
                                        <div id="teamScores"></div>
                                    </div>
                                    <div class="mb-3" id="individualAveragesSection" style="display: none;">
                                        <h6>${typeof t === 'function' ? t('best_individual_averages', 'Best Individual Averages') : 'Best Individual Averages'}</h6>
                                        <div id="individualAverages"></div>
                                    </div>
                                    <div class="mb-3" id="teamAveragesSection" style="display: none;">
                                        <h6>${typeof t === 'function' ? t('best_team_averages', 'Best Team Averages') : 'Best Team Averages'}</h6>
                                        <div id="teamAverages"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Individual Performance Section (Full Width) -->
                    <div class="row mt-4">
                        <div class="col-12">
                            <div id="weekIndividualAveragesCard">
                                <div class="text-center py-3">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">${typeof t === 'function' ? t('status.loading', 'Loading individual averages...') : 'Loading individual averages...'}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Team vs Team Comparison Section (Full Width) -->
                    <div class="row mt-4">
                        <div class="col-12">
                            <div id="team-vs-team-comparison-matchday"></div>
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
                    <h5>${typeof t === 'function' ? t('block.matchday.title', 'League Results - Match Day') : 'League Results - Match Day'}</h5>
                </div>
                <div class="card-body">
                    <!-- Message Area -->
                    <div id="weekMessage" class="alert alert-info">
                        ${typeof t === 'function' ? t('msg.please_select.match_day', 'Please select a match day.') : 'Please select a match day.'}
                    </div>
                </div>
            </div>
        `;
    }

    async loadMatchDayData(state) {
        const { season, league, week } = state;
        
        try {
            // Load table, honor scores, individual averages, and team vs team comparison in parallel
            await Promise.all([
                this.loadLeagueWeekTable(season, league, week),
                this.loadHonorScores(season, league, week),
                this.loadIndividualAverages(state),
                this.loadTeamVsTeamComparison(season, league, week)
            ]);
            
        } catch (error) {
            console.error('Error loading match day data:', error);
        }
    }

    async loadLeagueWeekTable(season, league, week) {
        try {
            const response = await fetchWithDatabase(`/league/get_league_week_table?season=${season}&league=${league}&week=${week}`);
            const tableData = await response.json();
            
            console.log('League week table data:', tableData); // Debug logging
            
            const container = document.getElementById('tableLeagueWeek');
            if (container) {
                // Use Tabulator for structured TableData
                if (typeof createTableTabulator === 'function') {
                    console.log('Using createTableTabulator function for week table');
                    createTableTabulator('tableLeagueWeek', tableData, { 
                        disablePositionCircle: false, // Week standings should show team color circles
                        enableSpecialRowStyling: true,
                        tooltips: true
                    });
                } else if (typeof createTableBootstrap3 === 'function') {
                    console.log('Fallback: Using createTableBootstrap3 function');
                    createTableBootstrap3('tableLeagueWeek', tableData, { 
                        disablePositionCircle: false,
                        enableSpecialRowStyling: true 
                    });
                } else {
                    console.error('No table creation function available');
                    container.innerHTML = `<div class="alert alert-warning">${typeof t === 'function' ? t('no_data', 'Table creation function not available') : 'Table creation function not available'}</div>`;
                }
            }
        } catch (error) {
            console.error('Error loading league week table:', error);
            const container = document.getElementById('tableLeagueWeek');
            if (container) {
                container.innerHTML = `<div class="alert alert-danger">${typeof t === 'function' ? t('error_loading_data', 'Error loading week results') : 'Error loading week results'}</div>`;
            }
        }
    }

    async loadHonorScores(season, league, week) {
        try {
            const response = await fetchWithDatabase(`/league/get_honor_scores?season=${season}&league=${league}&week=${week}`);
            const data = await response.json();
            
            console.log('Honor scores data:', data); // Debug logging
            
            // Populate honor scores sections
            this.populateHonorScores(data);
            
        } catch (error) {
            console.error('Error loading honor scores:', error);
            this.showHonorScoresError();
        }
    }

    populateHonorScores(data) {
        console.log('Populating honor scores with data:', data); // Debug logging
        
        // Individual Scores
        if (data.individual_scores && data.individual_scores.length > 0) {
            const individualScoresHtml = data.individual_scores
                .filter(score => score && typeof score === 'object') // Filter out invalid entries
                .map(score => {
                    // Handle the actual API format: {player: 'Omar Weiß (Schweinfurt 1)', score: 272}
                    const playerInfo = score.player || score.player_name || score.name || 'Unknown Player';
                    const scoreValue = score.score || score.value || 'N/A';
                    
                    return `
                        <div class="d-flex justify-content-between">
                            <span>${playerInfo}</span>
                            <strong>${scoreValue}</strong>
                        </div>
                    `;
                }).join('');
            
            if (individualScoresHtml) {
                document.getElementById('individualScores').innerHTML = individualScoresHtml;
                document.getElementById('individualScoresSection').style.display = 'block';
            }
        }

        // Team Scores
        if (data.team_scores && data.team_scores.length > 0) {
            const teamScoresHtml = data.team_scores
                .filter(score => score && typeof score === 'object') // Filter out invalid entries
                .map(score => {
                    // Handle the actual API format - looks like it's working correctly
                    const teamName = score.team || score.team_name || score.name || 'Unknown Team';
                    const totalScore = score.score || score.total_score || score.value || 'N/A';
                    
                    return `
                        <div class="d-flex justify-content-between">
                            <span>${teamName}</span>
                            <strong>${totalScore}</strong>
                        </div>
                    `;
                }).join('');
            
            if (teamScoresHtml) {
                document.getElementById('teamScores').innerHTML = teamScoresHtml;
                document.getElementById('teamScoresSection').style.display = 'block';
            }
        }

        // Individual Averages
        if (data.individual_averages && data.individual_averages.length > 0) {
            const individualAveragesHtml = data.individual_averages
                .filter(avg => avg && typeof avg === 'object') // Filter out invalid entries
                .map(avg => {
                    // Handle the actual API format: likely {player: 'Player Name (Team)', average: 242.6}
                    const playerInfo = avg.player || avg.player_name || avg.name || 'Unknown Player';
                    const average = typeof avg.average === 'number' ? avg.average.toFixed(1) : (avg.value || 'N/A');
                    
                    return `
                        <div class="d-flex justify-content-between">
                            <span>${playerInfo}</span>
                            <strong>${average}</strong>
                        </div>
                    `;
                }).join('');
            
            if (individualAveragesHtml) {
                document.getElementById('individualAverages').innerHTML = individualAveragesHtml;
                document.getElementById('individualAveragesSection').style.display = 'block';
            }
        }

        // Team Averages
        if (data.team_averages && data.team_averages.length > 0) {
            const teamAveragesHtml = data.team_averages
                .filter(avg => avg && typeof avg === 'object') // Filter out invalid entries
                .map(avg => {
                    // Handle the actual API format - looks like team names are working correctly
                    const teamName = avg.team || avg.team_name || avg.name || 'Unknown Team';
                    const average = typeof avg.average === 'number' ? avg.average.toFixed(1) : (avg.value || 'N/A');
                    
                    return `
                        <div class="d-flex justify-content-between">
                            <span>${teamName}</span>
                            <strong>${average}</strong>
                        </div>
                    `;
                }).join('');
            
            if (teamAveragesHtml) {
                document.getElementById('teamAverages').innerHTML = teamAveragesHtml;
                document.getElementById('teamAveragesSection').style.display = 'block';
            }
        }

        // Hide loading spinner - look specifically in the honor scores card
        const honorScoresCard = document.getElementById('honorScores');
        if (honorScoresCard) {
            const loadingSpinner = honorScoresCard.querySelector('.spinner-border');
            if (loadingSpinner) {
                loadingSpinner.parentElement.style.display = 'none';
            }
        }
    }

    showHonorScoresError() {
        // Hide loading spinner and show error in honor scores card
        const honorScoresCard = document.getElementById('honorScores');
        if (honorScoresCard) {
            const loadingSpinner = honorScoresCard.querySelector('.spinner-border');
            if (loadingSpinner) {
                loadingSpinner.parentElement.innerHTML = `<div class="alert alert-danger alert-sm">${typeof t === 'function' ? t('error_loading_data', 'Error loading honor scores') : 'Error loading honor scores'}</div>`;
            }
        }
    }

    async loadIndividualAverages(state) {
        const { season, league, week } = state;
        
        // Use shared utility function that handles both loading and rendering
        if (typeof loadAndRenderIndividualAverages === 'function') {
            await loadAndRenderIndividualAverages(
                { league, season, week },
                {
                    containerId: 'weekIndividualAveragesCard',
                    tableId: 'weekIndividualAveragesTable',
                    headerLevel: 'h6',
                    disablePositionCircle: true,
                    enableSpecialRowStyling: true,
                    tooltips: true
                },
                typeof t === 'function' ? t('error_loading_individual_averages', 'Error loading individual averages') : 'Error loading individual averages'
            );
        } else {
            console.error('loadAndRenderIndividualAverages utility function not available');
            const container = document.getElementById('weekIndividualAveragesCard');
            if (container) {
                container.innerHTML = `<div class="alert alert-info">${typeof t === 'function' ? t('no_data', 'Individual averages data not available') : 'Individual averages data not available'}</div>`;
            }
        }
    }

    async loadTeamVsTeamComparison(season, league, week) {
        // Use shared utility function
        if (typeof loadAndRenderTeamVsTeamComparison === 'function') {
            await loadAndRenderTeamVsTeamComparison(
                { league, season, week },
                {
                    containerId: 'team-vs-team-comparison-matchday',
                    tableId: 'team-vs-team-comparison-table-matchday',
                    headerLevel: 'h6',
                    disablePositionCircle: false,
                    enableHeatMap: true
                },
                typeof t === 'function' ? t('no_data', 'Team vs team comparison not available for this week') : 'Team vs team comparison not available for this week'
            );
        } else {
            console.error('loadAndRenderTeamVsTeamComparison utility function not available');
            const container = document.getElementById('team-vs-team-comparison-matchday');
            if (container) {
                container.innerHTML = `<div class="alert alert-info">${typeof t === 'function' ? t('no_data', 'Team vs team comparison not available for this week') : 'Team vs team comparison not available for this week'}</div>`;
            }
        }
    }
}