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
            title: typeof t === 'function' ? t('league_standings', 'Season League Standings') : 'Season League Standings'
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
                    <h5>${typeof t === 'function' ? t('league_standings_all_leagues', 'Current Standings in all Leagues') : 'Current Standings in all Leagues'} – ${typeof t === 'function' ? t('season', 'Season') : 'Season'} ${state.season}</h5>
                </div>
                <div class="card-body">
                    <div id="seasonLeagueStandingsContent">
                        <div class="text-center py-4">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">${typeof t === 'function' ? t('status.loading', 'Loading...') : 'Loading...'}</span>
                            </div>
                            <p class="text-muted mt-2">${typeof t === 'function' ? t('loading_data', 'Loading data...') : 'Loading data...'}</p>
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
                    <h6>${typeof t === 'function' ? t('no_league_data_available', 'No league data available') : 'No league data available'}</h6>
                    <p class="mb-0">${typeof t === 'function' ? t('no_data_available_for', 'No data available for') : 'No data available for'} ${season}.</p>
                </div>
            `;
            return;
        }

        let html = '';
        
        // Create a card for each league
        data.leagues.forEach(leagueData => {
            const { league, week, standings, honor_scores } = leagueData;
            const leagueId = league.replace(/\s+/g, '_');
            const tableId = `tableSeasonLeagueStandings_${leagueId}`;
            
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h6 class="mb-0">${league} - ${typeof t === 'function' ? (t('match_day_label', 'Match Day')) : 'Match Day'} ${week}</h6>
                    </div>
                    <div class="card-body">
                        ${typeof window.generateLeagueStandingsCardHTML === 'function' 
                            ? window.generateLeagueStandingsCardHTML({
                                league: league,
                                week: week,
                                season: season,
                                tableId: tableId,
                                honorScoresPrefix: leagueId
                              })
                            : `
                            <div class="row">
                                <div class="col-md-8">
                                    <h6>${typeof t === 'function' ? t('league_standings', 'League Standings') : 'League Standings'}</h6>
                                    <div id="${tableId}"></div>
                                </div>
                                <div class="col-md-4">
                                    <div class="card">
                                        <div class="card-header">
                                            <h6>${typeof t === 'function' ? t('honor_scores', 'Honor Scores') : 'Honor Scores'}</h6>
                                        </div>
                                        <div class="card-body">
                                            <div class="mb-3" id="individualScoresSection_${leagueId}" style="display: none;">
                                                <h6>${typeof t === 'function' ? t('top_individual_scores', 'Top Individual Scores') : 'Top Individual Scores'}</h6>
                                                <div id="individualScores_${leagueId}"></div>
                                            </div>
                                            <div class="mb-3" id="teamScoresSection_${leagueId}" style="display: none;">
                                                <h6>${typeof t === 'function' ? t('top_team_scores', 'Top Team Scores') : 'Top Team Scores'}</h6>
                                                <div id="teamScores_${leagueId}"></div>
                                            </div>
                                            <div class="mb-3" id="individualAveragesSection_${leagueId}" style="display: none;">
                                                <h6>${typeof t === 'function' ? t('best_individual_averages', 'Best Individual Averages') : 'Best Individual Averages'}</h6>
                                                <div id="individualAverages_${leagueId}"></div>
                                            </div>
                                            <div class="mb-3" id="teamAveragesSection_${leagueId}" style="display: none;">
                                                <h6>${typeof t === 'function' ? t('best_team_averages', 'Best Team Averages') : 'Best Team Averages'}</h6>
                                                <div id="teamAverages_${leagueId}"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            `}
                    </div>
                </div>
            `;
        });
        
        contentContainer.innerHTML = html;
        
        // Create tables and honor scores for each league
        // Each league gets its own color cycle starting from position 1
        data.leagues.forEach(leagueData => {
            const { league, standings, honor_scores } = leagueData;
            const leagueId = league.replace(/\s+/g, '_');
            const tableId = `tableSeasonLeagueStandings_${leagueId}`;
            
            // Extract teams for this league and assign colors starting from palette index 0
            // This ensures each league has its own independent color cycle
            if (standings && standings.data && standings.data.length > 0) {
                const leagueTeams = [];
                standings.data.forEach(row => {
                    if (row && row.length > 1 && typeof row[1] === 'string' && row[1].trim() !== '') {
                        leagueTeams.push(row[1]);
                    }
                });
                
                // Remove duplicates
                const uniqueLeagueTeams = [...new Set(leagueTeams)];
                
                // Assign colors to this league's teams starting from palette index 0
                // Clear existing colors for these teams first so they restart the cycle
                if (uniqueLeagueTeams.length > 0) {
                    // Access teamColorMap and getPaletteColor from ColorUtils
                    const teamColorMap = (window.ColorUtils && window.ColorUtils.teamColorMap) || (window.teamColorMap) || {};
                    const getPaletteColor = (window.ColorUtils && window.ColorUtils.getPaletteColor) || 
                                          (window.getPaletteColor) || 
                                          ((idx) => '#888');
                    
                    // Clear colors for this league's teams (so they get reassigned from index 0)
                    uniqueLeagueTeams.forEach(team => {
                        if (teamColorMap[team]) {
                            delete teamColorMap[team];
                        }
                    });
                    
                    // Now assign colors starting from index 0 for this league
                    let paletteIdx = 0;
                    uniqueLeagueTeams.forEach(team => {
                        if (!teamColorMap[team]) {
                            teamColorMap[team] = getPaletteColor(paletteIdx++);
                        }
                    });
                    
                    // Update the global reference if needed
                    if (window.ColorUtils) {
                        window.ColorUtils.teamColorMap = teamColorMap;
                    }
                    if (window.teamColorMap) {
                        window.teamColorMap = teamColorMap;
                    }
                    
                    console.log(`Assigned colors to ${uniqueLeagueTeams.length} teams for league ${league} (starting from palette index 0)`);
                }
            }
            
            // Use shared utility function for standings table
            if (typeof window.renderLeagueStandingsTable === 'function') {
                window.renderLeagueStandingsTable(tableId, standings);
            } else {
                // Fallback
                const container = document.getElementById(tableId);
                if (container && standings) {
                    if (typeof createTableTabulator === 'function') {
                        createTableTabulator(tableId, standings, { 
                            disablePositionCircle: false,
                            enableSpecialRowStyling: true,
                            tooltips: true
                        });
                    } else if (typeof createTableBootstrap3 === 'function') {
                        createTableBootstrap3(tableId, standings, {
                            disablePositionCircle: false,
                            enableSpecialRowStyling: true,
                            compact: true
                        });
                    } else {
                        container.innerHTML = `
                            <div class="alert alert-warning">
                                <p class="mb-0">${typeof t === 'function' ? t('no_data_available_for', 'No data available for') : 'No data available for'} ${league}.</p>
                            </div>
                        `;
                    }
                }
            }
            
            // Use shared utility function for honor scores
            if (typeof window.populateHonorScores === 'function') {
                window.populateHonorScores(honor_scores, leagueId);
            } else {
                console.error('populateHonorScores utility function not available');
            }
        });
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