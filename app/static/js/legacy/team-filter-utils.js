/**
 * Legacy Team Filter Utilities
 * 
 * Extracted from team/stats.html with identical signatures
 * These functions preserve exact functionality during Phase 1 migration
 */

/**
 * Update team select dropdown
 * Original function signature preserved exactly
 */
function updateTeamSelect(teams) {
    const select = document.getElementById('teamSelect');
    select.innerHTML = `
        <option value="">Bitte wählen...</option>
        ${teams.map(team => `
            <option value="${team}">${team}</option>
        `).join('')}
    `;

    // Remove old event listener first to prevent duplicates
    const newSelect = select.cloneNode(true);
    select.parentNode.replaceChild(newSelect, select);

    // Add event listener to new select
    newSelect.addEventListener('change', function() {
        const selectedTeam = this.value;
        console.log('Selected team:', selectedTeam); // Debug log
        if (selectedTeam) {
            updateSeasonButtons(selectedTeam);
            updateMessageVisibility();
            updateTeamHistory(selectedTeam);
    
            updateLeagueComparison(selectedTeam); // Call new function
            loadSpecialMatches(selectedTeam);
            
            // Also trigger Phase 2 analysis if a season is already selected
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
                
                // Don't trigger change event automatically - let user make the choice
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
    fetch(`/team/get_available_seasons?team_name=${teamName}`)
        .then(response => response.json())
        .then(seasons => {
            const container = document.getElementById('buttonsSeason');
            const buttonsSeason = ['All', ...seasons].map(season => `
                <input type="radio" class="btn-check" name="season" id="season_${season}" 
                       value="${season === 'All' ? '' : season}" ${season === 'All' ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="season_${season}">${season}</label>
            `).join('');
            container.innerHTML = buttonsSeason;
            
            // Don't automatically select the first button - let user make the choice
            // The "All" button is already checked by default in the HTML generation
        });
}

/**
 * Update week buttons
 * Original function signature preserved exactly
 */
function updateWeekButtons(teamName, season) {
    fetch(`/team/get_available_weeks?team_name=${teamName}&season=${season}`)
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