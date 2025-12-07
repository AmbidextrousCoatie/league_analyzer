/**
 * Utility functions for rendering league standings and honor scores cards
 * Used by both matchday-block and season-league-standings-block
 */

/**
 * Generate HTML for a league standings + honor scores card
 * @param {Object} options - Configuration options
 * @param {string} options.league - League name
 * @param {string} options.week - Week number (optional)
 * @param {string} options.season - Season (optional)
 * @param {string} options.tableId - Unique ID for the standings table container
 * @param {string} options.honorScoresPrefix - Prefix for honor scores element IDs (optional, defaults to empty string)
 * @returns {string} HTML string for the card
 */
function generateLeagueStandingsCardHTML(options) {
    const { league, week, season, tableId, honorScoresPrefix = '' } = options;
    
    // Build header title
    let headerTitle = league;
    if (week) {
        headerTitle += ` - ${typeof t === 'function' ? (t('match_day_label', 'Match Day')) : 'Match Day'} ${week}`;
    }
    
    // Build honor scores element IDs with prefix
    const prefix = honorScoresPrefix ? `${honorScoresPrefix}_` : '';
    const individualScoresId = `individualScores${prefix}`;
    const teamScoresId = `teamScores${prefix}`;
    const individualAveragesId = `individualAverages${prefix}`;
    const teamAveragesId = `teamAverages${prefix}`;
    const individualScoresSectionId = `individualScoresSection${prefix}`;
    const teamScoresSectionId = `teamScoresSection${prefix}`;
    const individualAveragesSectionId = `individualAveragesSection${prefix}`;
    const teamAveragesSectionId = `teamAveragesSection${prefix}`;
    
    return `
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
                        <!-- Individual Scores -->
                        <div class="mb-3" id="${individualScoresSectionId}" style="display: none;">
                            <h6>${typeof t === 'function' ? t('top_individual_scores', 'Top Individual Scores') : 'Top Individual Scores'}</h6>
                            <div id="${individualScoresId}"></div>
                        </div>
                        <!-- Team Scores -->
                        <div class="mb-3" id="${teamScoresSectionId}" style="display: none;">
                            <h6>${typeof t === 'function' ? t('top_team_scores', 'Top Team Scores') : 'Top Team Scores'}</h6>
                            <div id="${teamScoresId}"></div>
                        </div>
                        <!-- Individual Averages -->
                        <div class="mb-3" id="${individualAveragesSectionId}" style="display: none;">
                            <h6>${typeof t === 'function' ? t('best_individual_averages', 'Best Individual Averages') : 'Best Individual Averages'}</h6>
                            <div id="${individualAveragesId}"></div>
                        </div>
                        <!-- Team Averages -->
                        <div class="mb-3" id="${teamAveragesSectionId}" style="display: none;">
                            <h6>${typeof t === 'function' ? t('best_team_averages', 'Best Team Averages') : 'Best Team Averages'}</h6>
                            <div id="${teamAveragesId}"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Render league standings table
 * @param {string} tableId - ID of the container element
 * @param {Object} standingsData - TableData object from backend
 * @param {Object} options - Additional options
 */
function renderLeagueStandingsTable(tableId, standingsData, options = {}) {
    const container = document.getElementById(tableId);
    if (!container) {
        console.error(`Container ${tableId} not found`);
        return;
    }
    
    if (!standingsData) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <p class="mb-0">${typeof t === 'function' ? t('no_data_available', 'No data available') : 'No data available'}</p>
            </div>
        `;
        return;
    }
    
    // Use Tabulator for structured TableData
    if (typeof createTableTabulator === 'function') {
        console.log(`Creating Tabulator table ${tableId} with ${standingsData.data ? standingsData.data.length : 0} rows`);
        createTableTabulator(tableId, standingsData, { 
            disablePositionCircle: false, // Show position circles for league standings
            enableSpecialRowStyling: true,
            tooltips: true,
            disableTeamColorUpdate: true, // Disable automatic team color update (handled manually for multiple tables)
            ...options
        });
    } else if (typeof createTableBootstrap3 === 'function') {
        console.log(`Fallback: Using createTableBootstrap3 for ${tableId}`);
        createTableBootstrap3(tableId, standingsData, {
            disablePositionCircle: false,
            enableSpecialRowStyling: true,
            compact: true,
            ...options
        });
    } else {
        console.error('No table creation function available');
        container.innerHTML = `
            <div class="alert alert-warning">
                <p class="mb-0">${typeof t === 'function' ? t('no_data_available', 'Table creation function not available') : 'Table creation function not available'}</p>
            </div>
        `;
    }
}

/**
 * Populate honor scores sections
 * @param {Object} honorScoresData - Honor scores data from backend
 * @param {string} prefix - Prefix for element IDs (optional, for multiple leagues)
 */
function populateHonorScores(honorScoresData, prefix = '') {
    if (!honorScoresData) {
        return;
    }
    
    const idPrefix = prefix ? `${prefix}_` : '';
    
    // Individual Scores
    if (honorScoresData.individual_scores && honorScoresData.individual_scores.length > 0) {
        const individualScoresHtml = honorScoresData.individual_scores
            .filter(score => score && typeof score === 'object')
            .map(score => {
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
            const scoresElement = document.getElementById(`individualScores${idPrefix}`);
            const sectionElement = document.getElementById(`individualScoresSection${idPrefix}`);
            if (scoresElement && sectionElement) {
                scoresElement.innerHTML = individualScoresHtml;
                sectionElement.style.display = 'block';
            }
        }
    }

    // Team Scores
    if (honorScoresData.team_scores && honorScoresData.team_scores.length > 0) {
        const teamScoresHtml = honorScoresData.team_scores
            .filter(score => score && typeof score === 'object')
            .map(score => {
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
            const scoresElement = document.getElementById(`teamScores${idPrefix}`);
            const sectionElement = document.getElementById(`teamScoresSection${idPrefix}`);
            if (scoresElement && sectionElement) {
                scoresElement.innerHTML = teamScoresHtml;
                sectionElement.style.display = 'block';
            }
        }
    }

    // Individual Averages
    if (honorScoresData.individual_averages && honorScoresData.individual_averages.length > 0) {
        const individualAveragesHtml = honorScoresData.individual_averages
            .filter(avg => avg && typeof avg === 'object')
            .map(avg => {
                const playerInfo = avg.player || avg.player_name || avg.name || 'Unknown Player';
                const averageValue = typeof avg.average === 'number' ? avg.average.toFixed(1) : (avg.value || 'N/A');
                
                return `
                    <div class="d-flex justify-content-between">
                        <span>${playerInfo}</span>
                        <strong>${averageValue}</strong>
                    </div>
                `;
            }).join('');
        
        if (individualAveragesHtml) {
            const averagesElement = document.getElementById(`individualAverages${idPrefix}`);
            const sectionElement = document.getElementById(`individualAveragesSection${idPrefix}`);
            if (averagesElement && sectionElement) {
                averagesElement.innerHTML = individualAveragesHtml;
                sectionElement.style.display = 'block';
            }
        }
    }

    // Team Averages
    if (honorScoresData.team_averages && honorScoresData.team_averages.length > 0) {
        const teamAveragesHtml = honorScoresData.team_averages
            .filter(avg => avg && typeof avg === 'object')
            .map(avg => {
                const teamName = avg.team || avg.team_name || avg.name || 'Unknown Team';
                const averageValue = typeof avg.average === 'number' ? avg.average.toFixed(1) : (avg.value || 'N/A');
                
                return `
                    <div class="d-flex justify-content-between">
                        <span>${teamName}</span>
                        <strong>${averageValue}</strong>
                    </div>
                `;
            }).join('');
        
        if (teamAveragesHtml) {
            const averagesElement = document.getElementById(`teamAverages${idPrefix}`);
            const sectionElement = document.getElementById(`teamAveragesSection${idPrefix}`);
            if (averagesElement && sectionElement) {
                averagesElement.innerHTML = teamAveragesHtml;
                sectionElement.style.display = 'block';
            }
        }
    }
}

// Expose functions globally for use in content blocks
if (typeof window !== 'undefined') {
    window.generateLeagueStandingsCardHTML = generateLeagueStandingsCardHTML;
    window.renderLeagueStandingsTable = renderLeagueStandingsTable;
    window.populateHonorScores = populateHonorScores;
}
