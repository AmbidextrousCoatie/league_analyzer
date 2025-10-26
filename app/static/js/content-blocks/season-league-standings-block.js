/**
 * SeasonLeagueStandingsBlock - Shows latest week standings for all leagues in a season
 * Displays when: Season is selected but no League
 */
class SeasonLeagueStandingsBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'season-league-standings',
            containerId: 'seasonLeagueStandingsContainer',
            dataEndpoint: '/league/get_season_league_standings',
            requiredFilters: ['season'],
            title: 'Season League Standings'
        });
        this.dependencies = ['season'];
        this.container = document.getElementById(this.containerId);
    }

    async render(state = {}) {
        try {
            // Check if required dependencies are met and no league is selected
            if (!this.shouldRender(state)) {
                this.hide();
                return;
            }

            this.show();
            const html = this.generateHTML(state);
            this.container.innerHTML = html;
            
            // Load season league standings data
            await this.loadSeasonLeagueStandings(state);
            
            console.log('season-league-standings: Season league standings rendered');
        } catch (error) {
            console.error('Error rendering season league standings:', error);
            this.container.innerHTML = this.renderError('Failed to load season league standings data');
        }
    }

    shouldRender(state) {
        // Show only when season is selected but no league (handle both null and string "null")
        const hasSeason = state.season && state.season !== '' && state.season !== 'null';
        const hasLeague = state.league && state.league !== '' && state.league !== 'null';
        const shouldShow = hasSeason && !hasLeague;
        console.log(`SeasonLeagueStandingsBlock shouldRender: season="${state.season}", league="${state.league}", result=${shouldShow}`);
        return shouldShow;
    }

    generateHTML(state) {
        return `
            <div class="card mb-4">
                <div class="card-header">
                    <h5>Season ${state.season} - Latest Week Standings</h5>
                    <p class="mb-0 text-muted">Current standings across all leagues for the latest week</p>
                </div>
                <div class="card-body">
                    <div id="seasonLeagueStandingsContent">
                        <div class="text-center py-4">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Loading league standings...</span>
                            </div>
                            <p class="text-muted mt-2">Loading league standings...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async loadSeasonLeagueStandings(state) {
        const { season } = state;
        
        try {
            console.log(`Loading season league standings for season: ${season}`);
            
            const response = await fetchWithDatabase(`/league/get_season_league_standings?season=${season}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Season league standings data received:', data);
            
            this.renderSeasonLeagueStandings(data, season);
            
        } catch (error) {
            console.error('Error loading season league standings:', error);
            this.renderError('Failed to load season league standings data');
        }
    }

    renderSeasonLeagueStandings(data, season) {
        const contentContainer = document.getElementById('seasonLeagueStandingsContent');
        
        if (!data || !data.leagues || data.leagues.length === 0) {
            contentContainer.innerHTML = `
                <div class="alert alert-info">
                    <h6>No League Data Available</h6>
                    <p class="mb-0">No league standings found for season ${season}.</p>
                </div>
            `;
            return;
        }

        let html = '';
        
        // Create a card for each league
        data.leagues.forEach(leagueData => {
            const { league, week, standings, honor_scores } = leagueData;
            
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">${league} - Week ${week}</h6>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-8">
                                <h6>League Standings</h6>
                                <div id="tableSeasonLeagueStandings_${league.replace(/\s+/g, '_')}"></div>
                            </div>
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-header">
                                        <h6>Honor Scores</h6>
                                    </div>
                                    <div class="card-body">
                                        <!-- Individual Scores -->
                                        <div class="mb-3" id="individualScoresSection_${league.replace(/\s+/g, '_')}" style="display: none;">
                                            <h6>Top Individual Scores</h6>
                                            <div id="individualScores_${league.replace(/\s+/g, '_')}"></div>
                                        </div>
                                        <!-- Team Scores -->
                                        <div class="mb-3" id="teamScoresSection_${league.replace(/\s+/g, '_')}" style="display: none;">
                                            <h6>Top Team Scores</h6>
                                            <div id="teamScores_${league.replace(/\s+/g, '_')}"></div>
                                        </div>
                                        <!-- Individual Averages -->
                                        <div class="mb-3" id="individualAveragesSection_${league.replace(/\s+/g, '_')}" style="display: none;">
                                            <h6>Best Individual Averages</h6>
                                            <div id="individualAverages_${league.replace(/\s+/g, '_')}"></div>
                                        </div>
                                        <!-- Team Averages -->
                                        <div class="mb-3" id="teamAveragesSection_${league.replace(/\s+/g, '_')}" style="display: none;">
                                            <h6>Best Team Averages</h6>
                                            <div id="teamAverages_${league.replace(/\s+/g, '_')}"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        contentContainer.innerHTML = html;
        
        // Create tables and honor scores for each league
        data.leagues.forEach(leagueData => {
            const { league, standings, honor_scores } = leagueData;
            const tableId = `tableSeasonLeagueStandings_${league.replace(/\s+/g, '_')}`;
            const honorScoresId = `honorScoresSeasonLeague_${league.replace(/\s+/g, '_')}`;
            
            // Create standings table
            if (standings && typeof createTableBootstrap3 === 'function') {
                console.log(`Creating table for league ${league} with ${standings.data ? standings.data.length : 0} rows`);
                createTableBootstrap3(tableId, standings, {
                    disablePositionCircle: false, // Show position circles for league standings
                    enableSpecialRowStyling: true,
                    compact: true
                });
            } else {
                document.getElementById(tableId).innerHTML = `
                    <div class="alert alert-warning">
                        <p class="mb-0">No standings data available for ${league}.</p>
                    </div>
                `;
            }
            
            // Populate honor scores
            this.populateHonorScores(honor_scores, null, league);
        });
    }

    populateHonorScores(honorScoresData, containerId, league) {
        const leagueId = league.replace(/\s+/g, '_');
        
        // Individual Scores
        if (honorScoresData.individual_scores && honorScoresData.individual_scores.length > 0) {
            const individualScoresHtml = honorScoresData.individual_scores
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
                document.getElementById(`individualScores_${leagueId}`).innerHTML = individualScoresHtml;
                document.getElementById(`individualScoresSection_${leagueId}`).style.display = 'block';
            }
        }

        // Team Scores
        if (honorScoresData.team_scores && honorScoresData.team_scores.length > 0) {
            const teamScoresHtml = honorScoresData.team_scores
                .filter(score => score && typeof score === 'object') // Filter out invalid entries
                .map(score => {
                    // Handle the actual API format
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
                document.getElementById(`teamScores_${leagueId}`).innerHTML = teamScoresHtml;
                document.getElementById(`teamScoresSection_${leagueId}`).style.display = 'block';
            }
        }

        // Individual Averages
        if (honorScoresData.individual_averages && honorScoresData.individual_averages.length > 0) {
            const individualAveragesHtml = honorScoresData.individual_averages
                .filter(avg => avg && typeof avg === 'object') // Filter out invalid entries
                .map(avg => {
                    const playerInfo = avg.player || avg.player_name || avg.name || 'Unknown Player';
                    const averageValue = avg.average || avg.value || 'N/A';
                    
                    return `
                        <div class="d-flex justify-content-between">
                            <span>${playerInfo}</span>
                            <strong>${averageValue}</strong>
                        </div>
                    `;
                }).join('');
            
            if (individualAveragesHtml) {
                document.getElementById(`individualAverages_${leagueId}`).innerHTML = individualAveragesHtml;
                document.getElementById(`individualAveragesSection_${leagueId}`).style.display = 'block';
            }
        }

        // Team Averages
        if (honorScoresData.team_averages && honorScoresData.team_averages.length > 0) {
            const teamAveragesHtml = honorScoresData.team_averages
                .filter(avg => avg && typeof avg === 'object') // Filter out invalid entries
                .map(avg => {
                    const teamName = avg.team || avg.team_name || avg.name || 'Unknown Team';
                    const averageValue = avg.average || avg.value || 'N/A';
                    
                    return `
                        <div class="d-flex justify-content-between">
                            <span>${teamName}</span>
                            <strong>${averageValue}</strong>
                        </div>
                    `;
                }).join('');
            
            if (teamAveragesHtml) {
                document.getElementById(`teamAverages_${leagueId}`).innerHTML = teamAveragesHtml;
                document.getElementById(`teamAveragesSection_${leagueId}`).style.display = 'block';
            }
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
        const contentContainer = document.getElementById('seasonLeagueStandingsContent');
        if (contentContainer) {
            contentContainer.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        }
    }
}