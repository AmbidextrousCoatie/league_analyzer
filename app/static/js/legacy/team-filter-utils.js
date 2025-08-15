/**
 * Legacy Team Filter Utilities
 * 
 * UI update functions for team filter controls
 * Works in compatibility mode with modern state management
 */

/**
 * Update team select dropdown
 * Does not add event listeners when modern state management is active
 */
function updateTeamSelect(teams) {
    const select = document.getElementById('teamSelect');
    
    if (!select) {
        console.error('Team select element not found!');
        return;
    }
    
    const html = `
        <option value="">Bitte wählen...</option>
        ${teams.map(team => `
            <option value="${team}">${team}</option>
        `).join('')}
    `;
    
    select.innerHTML = html;

    // Only add legacy event listeners if modern state management is not active
    if (window.teamStatsApp && window.teamStatsApp.isInitialized) {
        console.log('Modern state management active - team select managed by FilterManager');
        return;
    }
    
    console.log('Adding legacy team select event listener');

    // Remove old event listener first to prevent duplicates
    const newSelect = select.cloneNode(true);
    select.parentNode.replaceChild(newSelect, select);

    // Add event listener to new select
    newSelect.addEventListener('change', function() {
        const selectedTeam = this.value;
        console.log('Selected team (legacy):', selectedTeam);
        if (selectedTeam) {
            updateSeasonButtons(selectedTeam);
            updateMessageVisibility();
            updateTeamHistory(selectedTeam);
    
            updateLeagueComparison(selectedTeam);
            loadSpecialMatches(selectedTeam);
            
            // Also trigger modern analysis if a season is already selected
            const selectedSeason = document.querySelector('input[name="season"]:checked')?.value;
            if (selectedSeason && selectedSeason !== '') {
                // Team + specific season selected
                console.log('Team + specific season selected');
                updateClutchAnalysis(selectedTeam, selectedSeason);
                updateConsistencyMetrics(selectedTeam, selectedSeason);
                loadSpecialMatchesForSeason(selectedTeam, selectedSeason);
            } else {
                // Team only selected (season = "All")
                console.log('Team only selected (All seasons)');
                updateClutchAnalysis(selectedTeam, null);
                updateConsistencyMetrics(selectedTeam, null);
                loadSpecialMatches(selectedTeam);
            }
        } else {
            // No team selected - show all teams stats
            console.log('No team selected - show all teams');
            updateAllTeamsStats();
            updateMessageVisibility();
        }
    });
}

/**
 * Update season buttons
 * Original function signature preserved exactly
 */
function updateSeasonButtons(teamName) {
    fetchWithDatabase(`/team/get_available_seasons?team_name=${teamName}`)
        .then(response => response.json())
        .then(seasons => {
            const container = document.getElementById('buttonsSeason');
            const buttonsSeason = ['All', ...seasons].map(season => `
                <input type="radio" class="btn-check" name="season" id="season_${season}" 
                       value="${season === 'All' ? '' : season}" ${season === 'All' ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="season_${season}">${season}</label>
            `).join('');
            container.innerHTML = buttonsSeason;
        });
}

/**
 * Update week buttons
 * Original function signature preserved exactly
 */
function updateWeekButtons(teamName, season) {
    fetchWithDatabase(`/team/get_available_weeks?team_name=${teamName}&season=${season}`)
        .then(response => response.json())
        .then(weeks => {
            const container = document.getElementById('buttonsWeek');
            // Handle case where weeks might be null, undefined, or not an array
            if (weeks && Array.isArray(weeks) && weeks.length > 0) {
                container.innerHTML = weeks.map(week => `
                    <input type="radio" class="btn-check" name="week" id="week_${week}" value="${week}">
                    <label class="btn btn-outline-primary" for="week_${week}">${week}</label>
                `).join('');
            } else {
                container.innerHTML = '<p class="text-muted">Keine Wochen verfügbar</p>';
            }
        })
        .catch(error => {
            console.error('Error loading weeks:', error);
            const container = document.getElementById('buttonsWeek');
            container.innerHTML = '<p class="text-muted">Fehler beim Laden der Wochen</p>';
        });
}

/**
 * Update message visibility based on selection state
 * Original function signature preserved exactly
 */
function updateMessageVisibility() {
    const selectedTeam = document.getElementById('teamSelect').value;
    const message = document.getElementById('selectionMessage');
    
    if (selectedTeam) {
        message.style.display = 'none';
    } else {
        message.style.display = 'block';
    }
}

/**
 * Update available options when filters change
 * Original function signature preserved exactly
 */
function updateAvailableOptions() {
    const selectedTeam = document.getElementById('teamSelect').value;
    const selectedSeason = document.querySelector('input[name="season"]:checked')?.value;
    if (selectedTeam) {
        updateSeasonButtons(selectedTeam);
        if (selectedSeason) {
            updateWeekButtons(selectedTeam, selectedSeason);
        }
    }
}

/**
 * Show stats for all teams (placeholder)
 * Original function signature preserved exactly
 */
function updateAllTeamsStats() {
    // This would show overall league statistics
    console.log('Showing all teams statistics');
    // TODO: Implement all teams overview
}

// Make functions globally available (preserve original behavior)
window.updateTeamSelect = updateTeamSelect;
window.updateSeasonButtons = updateSeasonButtons;
window.updateWeekButtons = updateWeekButtons;
window.updateMessageVisibility = updateMessageVisibility;
window.updateAvailableOptions = updateAvailableOptions;
window.updateAllTeamsStats = updateAllTeamsStats;