/**
 * League Data Utilities
 * 
 * Data fetching and display functions for league statistics
 * Extracted from monolithic league stats template
 */

/**
 * Update team details table
 */
function updateTableTeamDetails() {
    const selectedSeason = currentState?.season || document.querySelector('input[name="season"]:checked')?.value;
    const selectedLeague = currentState?.league || document.querySelector('input[name="league"]:checked')?.value;
    const selectedWeek = currentState?.week || document.querySelector('input[name="week"]:checked')?.value;
    const selectedTeam = currentState?.team || document.querySelector('input[name="team"]:checked')?.value;
    const selectedView = currentState?.teamView || document.querySelector('input[name="teamView"]:checked')?.value;
    
    let endpoint = '/league/get_team_week_details_table';
    let viewMode = undefined;
    
    if (selectedView === 'new') {
        endpoint = '/league/get_team_individual_scores_table';
    } else if (selectedView === 'newFull') {
        endpoint = '/league/get_team_week_head_to_head_table';
        viewMode = 'full';
    }
    
    if (!selectedSeason || !selectedLeague || !selectedWeek || !selectedTeam) {
        return;
    }
    
    // Update header
    const matchDayText = window.translations ? (window.translations['match_day_label'] || 'Match Day') : 'Match Day';
    const headerElement = document.getElementById('teamDetailsMetadata');
    if (headerElement) {
        headerElement.innerHTML = `${selectedTeam} - ${matchDayText} ${selectedWeek}`;
    }
    
    // Use fetchAndRenderTable for consistent table rendering
    const params = {
        season: selectedSeason,
        league: selectedLeague,
        week: selectedWeek,
        team: selectedTeam,
        options: {
            disablePositionCircle: true,
            mergeCells: false,
            enableSpecialRowStyling: true
        }
    };
    
    if (viewMode) {
        params.view_mode = viewMode;
    }
    
    fetchAndRenderTable('teamTableWeekDetails', endpoint, params);
}

/**
 * Update position history table
 */
function updateTablePosition(data) {
    const table = document.getElementById('positionHistoryTable');
    if (!table) return;
    
    // Update headers
    const headerRow = table.querySelector('thead tr');
    if (headerRow) {
        headerRow.innerHTML = '<th>Team</th>';
        data.weeks.forEach(week => {
            headerRow.innerHTML += `<th colspan="2">Week ${week}</th>`;
        });
    }
    
    // Add subheader row for Points/Average
    const existingSubheader = table.querySelector('thead tr:nth-child(2)');
    if (existingSubheader) {
        existingSubheader.remove();
    }
    
    const subheaderRow = document.createElement('tr');
    subheaderRow.innerHTML = '<th></th>';  // Empty cell for team name
    data.weeks.forEach(() => {
        subheaderRow.innerHTML += '<th>Points</th><th>Average</th>';
    });
    
    const thead = table.querySelector('thead');
    if (thead) {
        thead.appendChild(subheaderRow);
    }
    
    // Update body
    const tbody = table.querySelector('tbody');
    if (tbody) {
        tbody.innerHTML = '';
        
        data.data.forEach(teamData => {
            const row = document.createElement('tr');
            row.innerHTML = `<td>${teamData.team}</td>`;
            
            teamData.weeks.forEach(week => {
                row.innerHTML += `
                    <td>${week.points.toFixed(1)}</td>
                    <td>${week.average.toFixed(2)}</td>
                `;
            });
            
            tbody.appendChild(row);
        });
    }
}

/**
 * Update league week standings table
 */
function updateTableLeagueWeek() {
    const selectedSeason = currentState?.season || document.querySelector('input[name="season"]:checked')?.value;
    const selectedLeague = currentState?.league || document.querySelector('input[name="league"]:checked')?.value;
    const selectedWeek = currentState?.week || document.querySelector('input[name="week"]:checked')?.value;
    
    if (!selectedSeason || !selectedLeague) {
        return;
    }
    
    if (!selectedWeek) {
        // Show message when no week is selected
        const messageArea = document.getElementById('weekMessage');
        const standingsTable = document.getElementById('tableLeagueWeek');
        
        if (messageArea) {
            messageArea.style.display = 'block';
            messageArea.innerHTML = window.translations ? 
                (window.translations['please_select_match_day'] || 'Please select a match day.') : 
                'Please select a match day.';
        }
        if (standingsTable) standingsTable.style.display = 'none';
        return;
    }
    
    // Show the table and hide the message
    const messageArea = document.getElementById('weekMessage');
    const standingsTable = document.getElementById('tableLeagueWeek');
    
    if (messageArea) messageArea.style.display = 'none';
    if (standingsTable) standingsTable.style.display = 'block';
    
    // Fetch and display table
    fetchAndRenderTable('tableLeagueWeek', '/league/get_league_week_table', {
        season: selectedSeason,
        league: selectedLeague,
        week: selectedWeek
    });
}

/**
 * Update league history table
 */
function updateTableLeagueHistory() {
    const selectedSeason = currentState?.season || document.querySelector('input[name="season"]:checked')?.value;
    const selectedLeague = currentState?.league || document.querySelector('input[name="league"]:checked')?.value;
    
    if (!selectedSeason || !selectedLeague) {
        const selectionMessage = document.getElementById('selectionMessage');
        const leagueTable = document.getElementById('leagueTableHistory');
        
        if (selectionMessage) selectionMessage.style.display = 'block';
        if (leagueTable) leagueTable.style.display = 'none';
        return;
    }
    
    const selectionMessage = document.getElementById('selectionMessage');
    const leagueTable = document.getElementById('leagueTableHistory');
    
    if (selectionMessage) selectionMessage.style.display = 'none';
    if (leagueTable) leagueTable.style.display = 'block';
    
    // Fetch and display table
    fetchAndRenderTable('leagueTableHistory', '/league/get_league_history', {
        season: selectedSeason,
        league: selectedLeague
    });
}

/**
 * Update all content based on current state
 */
function updateAllContent() {
    updatePositionChart();
    updateTableLeagueHistory();
    updateTableLeagueWeek();
    updateTableTeamDetails();
}

/**
 * Update content for specific button type change
 */
function updateContentForButtonType(buttonType) {
    switch(buttonType) {
        case 'season':
            updatePositionChart();
            updateTableLeagueHistory();
            updateTableLeagueWeek();
            updateTableTeamDetails();
            break;
        case 'league':
            updatePositionChart();
            updateTableLeagueHistory();
            updateTableLeagueWeek();
            updateTableTeamDetails();
            break;
        case 'week':
            updateTableLeagueWeek();
            updateTableTeamDetails();
            break;
        case 'team':
            updateTableTeamDetails();
            break;
    }
}

/**
 * Handle data request errors
 */
function handleDataRequestError(error, elementId, fallbackMessage = 'Data temporarily unavailable') {
    console.error('Data request error:', error);
    
    const element = document.getElementById(elementId);
    if (element) {
        let message = fallbackMessage;
        if (error.status === 404) {
            message = 'No data found for the current parameters. This might be due to a data source change.';
        }
        
        element.innerHTML = `
            <div class="alert alert-warning">
                <strong>Data Unavailable:</strong> ${message}
                <br><small>This might be due to a data source change. Try refreshing the page or selecting different parameters.</small>
            </div>
        `;
    }
}

/**
 * Show data unavailable message
 */
function showDataUnavailableMessage(message, elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-warning">
                <strong>Data Unavailable:</strong> ${message}
                <br><small>This might be due to a data source change. Try refreshing the page or selecting different parameters.</small>
            </div>
        `;
    }
}