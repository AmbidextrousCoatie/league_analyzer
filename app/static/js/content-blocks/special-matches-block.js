/**
 * Special Matches Content Block
 * 
 * Replaces the legacy loadSpecialMatches() and loadSpecialMatchesForSeason() functions
 * Shows highest scores, lowest scores, biggest wins, and biggest losses in tables
 */

class SpecialMatchesBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'special-matches',
            containerId: 'specialMatchesContainer', // We'll use a wrapper container
            dataEndpoint: '/team/get_special_matches',
            requiredFilters: ['team'],
            optionalFilters: ['season'],
            title: 'Special Moments',
            description: 'Team record performances and notable results'
        });
        
        // Table container IDs
        this.tableContainers = {
            highestScores: 'highestScoresBody',
            lowestScores: 'lowestScoresBody',
            biggestWins: 'biggestWinsBody',
            biggestLosses: 'biggestLossesBody'
        };
    }
    
    /**
     * Render the special matches tables
     */
    async render(data, filterState) {
        if (!data) {
            throw new Error('No special matches data available');
        }
        
        console.log('SpecialMatchesBlock: Rendering special matches with data:', data);
        
        // Render all tables
        this.renderHighestScores(data.highest_scores || []);
        this.renderLowestScores(data.lowest_scores || []);
        this.renderBiggestWins(data.biggest_win_margin || []);
        this.renderBiggestLosses(data.biggest_loss_margin || []);
        
        console.log(`${this.id}: Rendered all special matches tables successfully`);
    }
    
    /**
     * Helper function to format event string
     */
    formatEvent(match) {
        return `${match.Season} ${match.League} W${match.Week}`;
    }
    
    /**
     * Render highest scores table
     */
    renderHighestScores(matches) {
        const container = document.getElementById(this.tableContainers.highestScores);
        if (!container) {
            console.warn(`${this.id}: Highest scores container not found`);
            return;
        }
        
        if (!matches || matches.length === 0) {
            container.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No data available</td></tr>';
            return;
        }
        
        container.innerHTML = matches.map(match => `
            <tr>
                <td><strong>${match.Score}</strong></td>
                <td>${this.formatEvent(match)}</td>
                <td>${match.Opponent}</td>
            </tr>
        `).join('');
        
        console.log(`${this.id}: Rendered ${matches.length} highest scores`);
    }
    
    /**
     * Render lowest scores table
     */
    renderLowestScores(matches) {
        const container = document.getElementById(this.tableContainers.lowestScores);
        if (!container) {
            console.warn(`${this.id}: Lowest scores container not found`);
            return;
        }
        
        if (!matches || matches.length === 0) {
            container.innerHTML = '<tr><td colspan="3" class="text-center text-muted">No data available</td></tr>';
            return;
        }
        
        container.innerHTML = matches.map(match => `
            <tr>
                <td><strong>${match.Score}</strong></td>
                <td>${this.formatEvent(match)}</td>
                <td>${match.Opponent}</td>
            </tr>
        `).join('');
        
        console.log(`${this.id}: Rendered ${matches.length} lowest scores`);
    }
    
    /**
     * Render biggest wins table
     */
    renderBiggestWins(matches) {
        const container = document.getElementById(this.tableContainers.biggestWins);
        if (!container) {
            console.warn(`${this.id}: Biggest wins container not found`);
            return;
        }
        
        if (!matches || matches.length === 0) {
            container.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No data available</td></tr>';
            return;
        }
        
        container.innerHTML = matches.map(match => `
            <tr>
                <td><strong class="text-success">+${match.WinMargin}</strong></td>
                <td>${match.Score} : ${match.Score - match.WinMargin}</td>
                <td>${this.formatEvent(match)}</td>
                <td>${match.Opponent}</td>
            </tr>
        `).join('');
        
        console.log(`${this.id}: Rendered ${matches.length} biggest wins`);
    }
    
    /**
     * Render biggest losses table
     */
    renderBiggestLosses(matches) {
        const container = document.getElementById(this.tableContainers.biggestLosses);
        if (!container) {
            console.warn(`${this.id}: Biggest losses container not found`);
            return;
        }
        
        if (!matches || matches.length === 0) {
            container.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No data available</td></tr>';
            return;
        }
        
        container.innerHTML = matches.map(match => `
            <tr>
                <td><strong class="text-danger">${match.WinMargin}</strong></td>
                <td>${match.Score} : ${match.Score - match.WinMargin}</td>
                <td>${this.formatEvent(match)}</td>
                <td>${match.Opponent}</td>
            </tr>
        `).join('');
        
        console.log(`${this.id}: Rendered ${matches.length} biggest losses`);
    }
    
    /**
     * Show loading state in all tables
     */
    showLoading() {
        const loadingHtml = '<tr><td colspan="4" class="text-center"><div class="spinner-border spinner-border-sm text-primary" role="status"><span class="visually-hidden">Loading...</span></div></td></tr>';
        const loadingHtml3Col = '<tr><td colspan="3" class="text-center"><div class="spinner-border spinner-border-sm text-primary" role="status"><span class="visually-hidden">Loading...</span></div></td></tr>';
        
        Object.entries(this.tableContainers).forEach(([key, containerId]) => {
            const container = document.getElementById(containerId);
            if (container) {
                // Use 3 columns for scores tables, 4 for wins/losses
                const html = (key.includes('Scores')) ? loadingHtml3Col : loadingHtml;
                container.innerHTML = html;
            }
        });
    }
    
    /**
     * Show placeholder when cannot render
     */
    showPlaceholder() {
        const placeholderHtml = '<tr><td colspan="4" class="text-center text-muted">Select a team to view special moments</td></tr>';
        const placeholderHtml3Col = '<tr><td colspan="3" class="text-center text-muted">Select a team to view special moments</td></tr>';
        
        Object.entries(this.tableContainers).forEach(([key, containerId]) => {
            const container = document.getElementById(containerId);
            if (container) {
                // Use 3 columns for scores tables, 4 for wins/losses
                const html = (key.includes('Scores')) ? placeholderHtml3Col : placeholderHtml;
                container.innerHTML = html;
            }
        });
    }
    
    /**
     * Show error state in all tables
     */
    showError(error) {
        const errorHtml = `<tr><td colspan="4" class="text-center text-warning">Error loading data: ${error.message}</td></tr>`;
        const errorHtml3Col = `<tr><td colspan="3" class="text-center text-warning">Error loading data: ${error.message}</td></tr>`;
        
        Object.entries(this.tableContainers).forEach(([key, containerId]) => {
            const container = document.getElementById(containerId);
            if (container) {
                // Use 3 columns for scores tables, 4 for wins/losses
                const html = (key.includes('Scores')) ? errorHtml3Col : errorHtml;
                container.innerHTML = html;
            }
        });
    }
    
    /**
     * Clear all table contents
     */
    clear() {
        Object.values(this.tableContainers).forEach(containerId => {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = '';
            }
        });
        
        this.lastRenderedState = {};
        this.lastData = null;
    }
    
    /**
     * Check if all table containers exist
     */
    hasAllContainers() {
        return Object.values(this.tableContainers).every(containerId => 
            !!document.getElementById(containerId)
        );
    }
    
    /**
     * Get container element (override to check all containers)
     */
    getContainer() {
        // For this block, we don't use a single container but multiple table containers
        // Return the first one for base class compatibility
        return document.getElementById(this.tableContainers.highestScores);
    }
    
    /**
     * Check if container exists (override to check all containers)
     */
    hasContainer() {
        return this.hasAllContainers();
    }
    
    /**
     * Enhanced debug information
     */
    debug() {
        const baseDebug = super.debug();
        const containerStatus = {};
        
        Object.entries(this.tableContainers).forEach(([key, containerId]) => {
            containerStatus[key] = !!document.getElementById(containerId);
        });
        
        return {
            ...baseDebug,
            tableContainers: this.tableContainers,
            containerStatus,
            allContainersExist: this.hasAllContainers()
        };
    }
}

// Make SpecialMatchesBlock globally available
window.SpecialMatchesBlock = SpecialMatchesBlock;