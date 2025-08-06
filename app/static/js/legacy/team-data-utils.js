/**
 * Legacy Team Data Utilities
 * 
 * Extracted from team/stats.html with identical signatures
 * These functions preserve exact functionality during Phase 1 migration
 */

/**
 * Load special matches data
 * Original function signature preserved exactly
 */
function loadSpecialMatches(teamName) {
    fetch(`/team/get_special_matches?team_name=${encodeURIComponent(teamName)}`)
        .then(response => response.json())
        .then(data => displaySpecialMatches(data));
}

/**
 * Load special matches for specific season
 * Original function signature preserved exactly
 */
function loadSpecialMatchesForSeason(teamName, season) {
    fetch(`/team/get_special_matches?team_name=${encodeURIComponent(teamName)}&season=${encodeURIComponent(season)}`)
        .then(response => response.json())
        .then(data => displaySpecialMatches(data));
}

/**
 * Display special matches in tables
 * Original function signature preserved exactly
 */
function displaySpecialMatches(data) {
    // Helper function to format event string
    const formatEvent = (match) => `${match.Season} ${match.League} W${match.Week}`;

    // Populate highest scores
    document.getElementById('highestScoresBody').innerHTML = data.highest_scores.map(match => `
        <tr>
            <td>${match.Score}</td>
            <td>${formatEvent(match)}</td>
            <td>${match.Opponent}</td>
        </tr>
    `).join('');

    // Populate lowest scores
    document.getElementById('lowestScoresBody').innerHTML = data.lowest_scores.map(match => `
        <tr>
            <td>${match.Score}</td>
            <td>${formatEvent(match)}</td>
            <td>${match.Opponent}</td>
        </tr>
    `).join('');

    // Populate biggest wins
    document.getElementById('biggestWinsBody').innerHTML = data.biggest_win_margin.map(match => `
        <tr>
            <td>+${match.WinMargin}</td>
            <td>${match.Score} : ${match.Score - match.WinMargin}</td>
            <td>${formatEvent(match)}</td>
            <td>${match.Opponent}</td>
        </tr>
    `).join('');

    // Populate biggest losses
    document.getElementById('biggestLossesBody').innerHTML = data.biggest_loss_margin.map(match => `
        <tr>
            <td>${match.WinMargin}</td>
            <td>${match.Score} : ${match.Score - match.WinMargin}</td>
            <td>${formatEvent(match)}</td>
            <td>${match.Opponent}</td>
        </tr>
    `).join('');
}

/**
 * Initialize teams data on page load
 * Original function signature preserved exactly
 */
function initializeTeamsData() {
    // Initial load of teams
    fetch('/team/get_teams')
        .then(response => response.json())
        .then(teams => {
            updateTeamSelect(teams);
        });
}

/**
 * Setup global event listeners
 * Original function signature preserved exactly
 */
function setupGlobalEventListeners() {
    // Always update available options when team or season changes
    document.addEventListener('change', event => {
        if (event.target.name === 'season') {
            updateAvailableOptions();
        }
        if (event.target.id === 'teamSelect') {
            updateAvailableOptions();
        }
        // Add other handlers for week if needed
    });

    // Centralized event listener for all changes
    document.addEventListener('change', event => {
        const name = event.target.name;
        if (name === 'season') {
            const selectedTeam = document.getElementById('teamSelect').value;
            const selectedSeason = event.target.value;
            console.log('Season changed to:', selectedSeason);
            
            updateWeekButtons(selectedTeam, selectedSeason);
            
            // Update analysis based on selection state
            if (selectedTeam) {
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
            }
        }
    });
}

/**
 * Initialize the team stats page
 * Original function signature preserved exactly
 */
function initializeTeamStatsPage() {
    // Setup event listeners
    setupGlobalEventListeners();
    
    // Initialize teams data
    initializeTeamsData();
}

// Make functions globally available (preserve original behavior)
window.loadSpecialMatches = loadSpecialMatches;
window.loadSpecialMatchesForSeason = loadSpecialMatchesForSeason;
window.displaySpecialMatches = displaySpecialMatches;
window.initializeTeamsData = initializeTeamsData;
window.setupGlobalEventListeners = setupGlobalEventListeners;
window.initializeTeamStatsPage = initializeTeamStatsPage;