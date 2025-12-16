/**
 * Legacy Team Data Utilities
 * 
 * Data fetching and display functions for team statistics
 * Works in compatibility mode with modern state management
 */

/**
 * Load special matches data
 * Original function signature preserved exactly
 */
function loadSpecialMatches(teamName) {
    fetchWithDatabase(`/team/get_special_matches?team_name=${encodeURIComponent(teamName)}`)
        .then(response => response.json())
        .then(data => displaySpecialMatches(data));
}

/**
 * Load special matches for specific season
 * Original function signature preserved exactly
 */
function loadSpecialMatchesForSeason(teamName, season) {
    fetchWithDatabase(`/team/get_special_matches?team_name=${encodeURIComponent(teamName)}&season=${encodeURIComponent(season)}`)
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
 * Initialize teams data using existing function
 * Original function signature preserved exactly
 */
function initializeTeamsData() {
    // Initial load of teams
    fetchWithDatabase('/team/get_teams')
        .then(response => response.json())
        .then(teams => {
            updateTeamSelect(teams);
        });
}

/**
 * Setup global event listeners
 * Only sets up legacy handlers if modern state management is not active
 */
function setupGlobalEventListeners() {
    // Check if modern state management is active
    if (window.teamStatsApp && window.teamStatsApp.isInitialized) {
        console.log('Modern state management active - skipping legacy event listeners');
        return;
    }
    
    console.log('Setting up legacy event listeners');
    
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
 * Only runs legacy initialization if modern state management is not active
 */
function initializeTeamStatsPage() {
    // Check if modern state management is active
    if (window.teamStatsApp && window.teamStatsApp.isInitialized) {
        console.log('Modern state management active - skipping legacy initialization');
        return;
    }
    
    console.log('Running legacy initialization');
    
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