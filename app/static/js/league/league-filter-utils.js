/**
 * League Filter Utilities
 * 
 * @deprecated This file is deprecated. Use CentralizedButtonManager instead.
 * 
 * UI update functions for league filter controls
 * Extracted from monolithic league stats template
 * 
 * MIGRATION GUIDE:
 * - Replace SimpleFilterManager with CentralizedButtonManager
 * - Remove manual button update calls
 * - The centralized system handles all button management automatically
 */

/**
 * Update all filter buttons
 */
function updateAllButtons() {
    updateSeasonButtons();
    updateLeagueButtons();
    updateWeekButtons();
    updateTeamButtons();
}

/**
 * Update season buttons
 */
function updateSeasonButtons() {
    fetchWithDatabase('/league/get_available_seasons')
        .then(response => response.json())
        .then(seasons => {
            const buttonsSeason = seasons.map(season => `
                <input type="radio" class="btn-check" name="season" id="season_${season}" 
                       value="${season}" ${season === currentState.season ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="season_${season}">${season}</label>
            `).join('');
            document.getElementById('buttonsSeason').innerHTML = buttonsSeason;
            
            // Auto-select if none selected
            const seasonInputs = document.querySelectorAll('input[name="season"]');
            if (![...seasonInputs].some(input => input.checked) && seasonInputs.length > 0) {
                seasonInputs[0].checked = true;
                currentState.season = seasonInputs[0].value;
            }
        })
        .catch(error => {
            console.error('Error loading seasons:', error);
            document.getElementById('buttonsSeason').innerHTML = `
                <div class="alert alert-danger">
                    <strong>${typeof t === 'function' ? t('error_loading_data', 'Error loading data') : 'Error loading data'}:</strong> ${error.message || 'Unknown error'}
                </div>
            `;
        });
}

/**
 * Update league buttons
 */
function updateLeagueButtons() {
    if (!currentState.season) return;
    
    fetchWithDatabase(`/league/get_available_leagues?season=${currentState.season}`)
        .then(response => response.json())
        .then(leagues => {
            const buttonsLeague = leagues.map(league => `
                <input type="radio" class="btn-check" name="league" id="league_${league}" 
                       value="${league}" ${league === currentState.league ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="league_${league}">${league}</label>
            `).join('');
            document.getElementById('buttonsLeague').innerHTML = buttonsLeague;
            
            // Auto-select highest league if none selected
            const leagueInputs = document.querySelectorAll('input[name="league"]');
            if (![...leagueInputs].some(input => input.checked) && leagues.length > 0) {
                const sortedLeagues = leagues.sort();
                const highestLeague = sortedLeagues[sortedLeagues.length - 1];
                const highestInput = document.querySelector(`input[name="league"][value="${highestLeague}"]`);
                if (highestInput) {
                    highestInput.checked = true;
                    currentState.league = highestLeague;
                }
            }
        })
        .catch(error => {
            console.error('Error loading leagues:', error);
            document.getElementById('buttonsLeague').innerHTML = `
                <div class="alert alert-danger">
                    <strong>${typeof t === 'function' ? t('error_loading_data', 'Error loading data') : 'Error loading data'}:</strong> ${error.message || 'Unknown error'}
                </div>
            `;
        });
}

/**
 * Update week buttons
 */
function updateWeekButtons() {
    if (!currentState.season || !currentState.league) {
        // Clear week buttons if prerequisites not met
        const container = document.getElementById('buttonsWeek');
        if (container) {
            container.innerHTML = `<span class="text-muted">${typeof t === 'function' ? t('msg.please_select.season_league', 'Please select a season and league first.') : 'Please select a season and league first.'}</span>`;
        }
        return;
    }
    
    fetchWithDatabase(`/league/get_available_weeks?season=${currentState.season}&league=${currentState.league}`)
        .then(response => response.json())
        .then(weeks => {
            const weekButtons = weeks.map(week => `
                <input type="radio" class="btn-check" name="week" id="week_${week}" 
                       value="${week}" ${week == currentState.week ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="week_${week}">${week}</label>
            `).join('');
            document.getElementById('buttonsWeek').innerHTML = weekButtons;
            
            // Auto-select latest week if none selected
            const weekInputs = document.querySelectorAll('input[name="week"]');
            if (![...weekInputs].some(input => input.checked) && weeks.length > 0) {
                const latestWeek = Math.max(...weeks);
                const latestInput = document.querySelector(`input[name="week"][value="${latestWeek}"]`);
                if (latestInput) {
                    latestInput.checked = true;
                    currentState.week = latestWeek;
                }
            }
        })
        .catch(error => {
            console.error('Error loading weeks:', error);
            document.getElementById('buttonsWeek').innerHTML = `
                <div class="alert alert-danger">
                    <strong>${typeof t === 'function' ? t('error_loading_data', 'Error loading data') : 'Error loading data'}:</strong> ${error.message || 'Unknown error'}
                </div>
            `;
        });
}

/**
 * Update team buttons
 */
function updateTeamButtons() {
    if (!currentState.season || !currentState.league || !currentState.week) {
        // Clear team buttons if prerequisites not met
        const container = document.getElementById('buttonsTeam');
        if (container) {
            container.innerHTML = `<span class="text-muted">${typeof t === 'function' ? t('msg.please_select.match_day', 'Please select a match day.') : 'Please select a match day.'}</span>`;
        }
        return;
    }
    
    fetchWithDatabase(`/league/get_available_teams?season=${currentState.season}&league=${currentState.league}`)
        .then(response => response.json())
        .then(teams => {
            const teamButtons = teams.map(team => `
                <input type="radio" class="btn-check" name="team" id="team_${team.replace(/\s+/g, '_')}" 
                       value="${team}" ${team === currentState.team ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="team_${team.replace(/\s+/g, '_')}">${team}</label>
            `).join('');
            document.getElementById('buttonsTeam').innerHTML = teamButtons;
            
            // Select first team by default if none selected
            let teamInput = document.querySelector('input[name="team"]:checked');
            if (!teamInput && teams.length > 0) {
                teamInput = document.querySelector(`input[name="team"][value="${teams[0]}"]`);
                if (teamInput) {
                    teamInput.checked = true;
                    currentState.team = teams[0];
                }
            }
        })
        .catch(error => {
            console.error('Error loading teams:', error);
            document.getElementById('buttonsTeam').innerHTML = `
                <div class="alert alert-danger">
                    <strong>${typeof t === 'function' ? t('error_loading_data', 'Error loading data') : 'Error loading data'}:</strong> ${error.message || 'Unknown error'}
                </div>
            `;
        });
}

/**
 * Update buttons for specific button type
 */
function updateButtonsForButtonType(buttonType) {
    switch(buttonType) {
        case 'season':
            updateLeagueButtons();
            updateWeekButtons();
            updateTeamButtons();
            break;
        case 'league':
            updateWeekButtons();
            updateTeamButtons();
            break;
        case 'week':
            // Week change doesn't affect other buttons
            break;
        case 'team':
            // Team change doesn't affect other buttons
            break;
    }
}

/**
 * Update message visibility based on selection state
 */
function updateMessageVisibility() {
    const messageArea = document.getElementById('weekMessage');
    const standingsTable = document.getElementById('tableLeagueWeek');
    
    if (!currentState.season || !currentState.league || !currentState.week) {
        if (messageArea) {
            messageArea.style.display = 'block';
            const msg = typeof t === 'function'
                ? (!currentState.season || !currentState.league
                    ? t('msg.please_select.season_league', 'Please select a season and league first.')
                    : t('msg.please_select.match_day', 'Please select a match day.'))
                : 'Please select season, league, and week to view standings.';
            messageArea.innerHTML = `<div class="alert alert-info">${msg}</div>`;
        }
        if (standingsTable) standingsTable.style.display = 'none';
    } else {
        if (messageArea) messageArea.style.display = 'none';
        if (standingsTable) standingsTable.style.display = 'block';
    }
}

/**
 * Alias for updateTeamButtons - used by SimpleFilterManager
 */
function updateLeagueTeamButtons(teams) {
    if (teams) {
        // If teams array is provided, use it directly 
        console.log('Updating league team buttons with provided teams:', teams);
        const currentState = { season: '', league: '', week: '', team: '' }; // Get from URL or state
        
        const teamButtons = teams.map(team => `
            <input type="radio" class="btn-check" name="team" id="team_${team.replace(/\s+/g, '_')}" 
                   value="${team}" ${team === currentState.team ? 'checked' : ''}>
            <label class="btn btn-outline-primary" for="team_${team.replace(/\s+/g, '_')}">${team}</label>
        `).join('');
        
        document.getElementById('buttonsTeam').innerHTML = teamButtons;
    } else {
        // Fall back to the standard updateTeamButtons
        updateTeamButtons();
    }
}