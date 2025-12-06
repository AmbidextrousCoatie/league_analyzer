/**
 * Individual Averages Utilities
 * Shared functions for rendering individual averages tables across different content blocks
 */

/**
 * Fetches individual averages data from the API
 * @param {Object} params - Parameters object
 * @param {string} params.league - League name
 * @param {string} params.season - Season identifier
 * @param {number} [params.week] - Optional week number
 * @param {string} [params.team] - Optional team name
 * @returns {Promise<Object>} Individual averages data
 */
async function fetchIndividualAverages({ league, season, week = null, team = null }) {
    let url = `/league/get_individual_averages?league=${encodeURIComponent(league)}&season=${encodeURIComponent(season)}`;
    
    if (week !== null && week !== undefined) {
        url += `&week=${encodeURIComponent(week)}`;
    }
    
    if (team !== null && team !== undefined) {
        url += `&team=${encodeURIComponent(team)}`;
    }

    const response = await fetchWithDatabase(url);
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
 * Renders the individual averages card and table
 * @param {Object} data - Individual averages data from API
 * @param {Object} options - Rendering options
 * @param {string} [options.containerId] - ID of the container element to render into (if provided, creates full card)
 * @param {string} options.tableId - ID for the table element (will be created inside container or used directly)
 * @param {string} [options.headerLevel='h6'] - HTML header level ('h5', 'h6', etc.)
 * @param {boolean} [options.disablePositionCircle=true] - Whether to disable position circles
 * @param {boolean} [options.enableSpecialRowStyling=true] - Whether to enable special row styling
 * @param {boolean} [options.tooltips=true] - Whether to enable tooltips
 */
function renderIndividualAverages(data, options) {
    const {
        containerId,
        tableId,
        headerLevel = 'h6',
        disablePositionCircle = true,
        enableSpecialRowStyling = true,
        tooltips = true
    } = options;

    if (!data || !data.columns || !data.data) {
        console.warn('No individual averages data available');
        const container = document.getElementById(containerId || tableId);
        if (container) {
            const t = typeof window.t === 'function' ? window.t : null;
            const getText = (key, fallback) => (t ? t(key, fallback) : fallback);
            container.innerHTML = `<div class="alert alert-info">${getText('no_data', 'Individual averages data not available')}</div>`;
        }
        return;
    }

    // Get translation function if available
    const t = typeof window.t === 'function' ? window.t : null;
    const getText = (key, fallback) => (t ? t(key, fallback) : fallback);

    // Use title from API response (which includes proper i18n with article_male + season/week)
    // Description content is now integrated into the title, no separate description paragraph
    const title = data.title || getText('individual_performance', 'Individual Performance');

    // If containerId is provided, render full card structure
    if (containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Individual averages container not found: ${containerId}`);
            return;
        }

        container.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <${headerLevel}>${title}</${headerLevel}>
                </div>
                <div class="card-body">
                    <div id="${tableId}"></div>
                </div>
            </div>
        `;
    }

    // Create table using Tabulator
    if (typeof createTableTabulator === 'function') {
        createTableTabulator(tableId, data, {
            disablePositionCircle,
            enableSpecialRowStyling,
            tooltips
        });
    } else if (typeof createTableBootstrap3 === 'function') {
        // Fallback to Bootstrap
        createTableBootstrap3(tableId, data, {
            disablePositionCircle,
            enableSpecialRowStyling
        });
    } else {
        console.error('Table creation function not available');
        const tableContainer = document.getElementById(tableId);
        if (tableContainer) {
            const t = typeof window.t === 'function' ? window.t : null;
            const getText = (key, fallback) => (t ? t(key, fallback) : fallback);
            tableContainer.innerHTML = `<div class="alert alert-warning">${getText('error_loading_data', 'Table creation function not available')}</div>`;
        }
    }
}

/**
 * Loads and renders individual averages with error handling
 * @param {Object} params - Parameters for fetching data
 * @param {string} params.league - League name
 * @param {string} params.season - Season identifier
 * @param {number} [params.week] - Optional week number
 * @param {string} [params.team] - Optional team name
 * @param {Object} renderOptions - Options for rendering (see renderIndividualAverages)
 * @param {string} [errorMessage] - Custom error message to display on failure
 */
async function loadAndRenderIndividualAverages(params, renderOptions, errorMessage = null) {
    try {
        const data = await fetchIndividualAverages(params);
        renderIndividualAverages(data, renderOptions);
    } catch (error) {
        console.error('Error loading individual averages:', error);
        const container = document.getElementById(renderOptions.containerId || renderOptions.tableId);
        if (container) {
            const t = typeof window.t === 'function' ? window.t : null;
            const getText = (key, fallback) => (t ? t(key, fallback) : fallback);
            const message = errorMessage || getText('error_loading_individual_averages', 'Error loading individual averages');
            container.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        }
    }
}
