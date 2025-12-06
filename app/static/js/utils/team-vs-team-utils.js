/**
 * Team vs Team Comparison Utilities
 * Shared functions for rendering team vs team comparison tables across different content blocks
 */

/**
 * Fetches team vs team comparison data from the API
 * @param {Object} params - Parameters object
 * @param {string} params.league - League name
 * @param {string} params.season - Season identifier
 * @param {number} [params.week] - Optional week number
 * @returns {Promise<Object>} Team vs team comparison data
 */
async function fetchTeamVsTeamComparison({ league, season, week = null }) {
    const url = new URL('/league/get_team_vs_team_comparison', window.location.origin);
    url.searchParams.append('league', league);
    url.searchParams.append('season', season);
    
    if (week !== null && week !== undefined) {
        url.searchParams.append('week', week);
    }
    
    // Add database parameter
    const database = getCurrentDatabase();
    if (database) {
        url.searchParams.append('database', database);
    }

    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    if (data.error) {
        throw new Error(`API Error: ${data.error}`);
    }
    
    return data;
}

/**
 * Renders the team vs team comparison card and table
 * @param {Object} data - Team vs team comparison data from API
 * @param {Object} options - Rendering options
 * @param {string} options.containerId - ID of the container element to render into
 * @param {string} options.tableId - ID for the table element (will be created inside container)
 * @param {string} [options.headerLevel='h6'] - HTML header level ('h5', 'h6', etc.)
 * @param {boolean} [options.disablePositionCircle=false] - Whether to disable position circles
 * @param {boolean} [options.enableHeatMap=true] - Whether to enable heat map
 * @param {string} [options.teamField] - Field name for team identification (for position circles)
 */
function renderTeamVsTeamComparison(data, options) {
    const {
        containerId,
        tableId,
        headerLevel = 'h6',
        disablePositionCircle = false,
        enableHeatMap = true,
        teamField = null
    } = options;

    if (!data || !data.columns || !data.data) {
        console.warn('No team vs team comparison data available');
        return;
    }

    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Team vs team comparison container not found: ${containerId}`);
        return;
    }

    // Get translation function if available
    const t = typeof window.t === 'function' ? window.t : null;
    const getText = (key, fallback) => (t ? t(key, fallback) : fallback);

    // Use title and description from API response (which includes proper i18n with article_male + season/week)
    // The backend provides: title with i18n, and description with "team_vs_team_comparison_matrix_explanation" + article_male + season/week
    const title = data.title || getText('team_vs_team_comparison_matrix', 'Team vs Team Comparison Matrix');
    const description = data.description || getText('ui.team_vs_team.description', 'Matrix showing team performance against each opponent');

    // Create the team vs team comparison card
    container.innerHTML = `
        <div class="card">
            <div class="card-header">
                <${headerLevel}>${title}</${headerLevel}>
                ${description ? `<p class="mb-0 text-muted small">${description}</p>` : ''}
            </div>
            <div class="card-body">
                <div id="${tableId}"></div>
                <div class="row mt-3">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header">
                                <h6>${getText('ui.heatmap.legend', 'Heat Map Legend')}</h6>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>${getText('ui.heatmap.score', 'Score Heat Map')}</h6>
                                        <div class="d-flex align-items-center">
                                            <span class="me-2">${getText('ui.heatmap.low', 'Low:')}</span>
                                            <div class="heat-map-legend me-2" style="background: ${window.ColorUtils?.getThemeColor('heatMapLow') || '#d9596a'}; width: 20px; height: 20px;"></div>
                                            <span class="me-2">${getText('ui.heatmap.high', 'High:')}</span>
                                            <div class="heat-map-legend" style="background: ${window.ColorUtils?.getThemeColor('heatMapHigh') || '#1b8da7'}; width: 20px; height: 20px;"></div>
                                        </div>
                                        <small class="text-muted">${getText('ui.range_label', 'Range:')} ${data.metadata?.score_range?.min || 'N/A'} - ${data.metadata?.score_range?.max || 'N/A'}</small>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>${getText('ui.heatmap.points', 'Points Heat Map')}</h6>
                                        <div class="d-flex align-items-center">
                                            <span class="me-2">${getText('ui.heatmap.low', 'Low:')}</span>
                                            <div class="heat-map-legend me-2" style="background: ${window.ColorUtils?.getThemeColor('heatMapLow') || '#d9596a'}; width: 20px; height: 20px;"></div>
                                            <span class="me-2">${getText('ui.heatmap.high', 'High:')}</span>
                                            <div class="heat-map-legend" style="background: ${window.ColorUtils?.getThemeColor('heatMapHigh') || '#1b8da7'}; width: 20px; height: 20px;"></div>
                                        </div>
                                        <small class="text-muted">${getText('ui.range_label', 'Range:')} ${data.metadata?.points_range?.min || 'N/A'} - ${data.metadata?.points_range?.max || 'N/A'}</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Create table using Tabulator
    if (typeof createTableTabulator === 'function') {
        const tableOptions = {
            disablePositionCircle,
            enableSpecialRowStyling: true,
            tooltips: true,
            enableHeatMap
        };
        
        if (teamField) {
            tableOptions.teamField = teamField;
        }
        
        createTableTabulator(tableId, data, tableOptions);
    } else if (typeof createTableBootstrap3 === 'function') {
        // Fallback to Bootstrap
        createTableBootstrap3(tableId, data, {
            disablePositionCircle,
            enableSpecialRowStyling: true,
            enableHeatMap
        });
    } else {
        console.error('Table creation function not available');
    }
}

/**
 * Loads and renders team vs team comparison with error handling
 * @param {Object} params - Parameters for fetching data
 * @param {string} params.league - League name
 * @param {string} params.season - Season identifier
 * @param {number} [params.week] - Optional week number
 * @param {Object} renderOptions - Options for rendering (see renderTeamVsTeamComparison)
 * @param {string} [errorMessage] - Custom error message to display on failure
 */
async function loadAndRenderTeamVsTeamComparison(params, renderOptions, errorMessage = null) {
    try {
        const data = await fetchTeamVsTeamComparison(params);
        renderTeamVsTeamComparison(data, renderOptions);
    } catch (error) {
        console.error('Error loading team vs team comparison:', error);
        const container = document.getElementById(renderOptions.containerId);
        if (container) {
            const t = typeof window.t === 'function' ? window.t : null;
            const getText = (key, fallback) => (t ? t(key, fallback) : fallback);
            const message = errorMessage || getText('no_data', 'Team vs team comparison not available');
            container.innerHTML = `<div class="alert alert-info">${message}</div>`;
        }
    }
}
