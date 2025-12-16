/**
 * GameOverviewBlock - Shows game overview for a specific round
 * Displays when: Season + League + Week + Round are selected (no team)
 */
class GameOverviewBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'game-overview',
            containerId: 'gameOverviewContainer',
            dataEndpoint: '/league/get_game_overview',
            requiredFilters: ['season', 'league', 'week', 'round'],
            title: 'Game Overview'
        });
        this.dependencies = ['season', 'league', 'week', 'round'];
        this.container = document.getElementById(this.containerId);
    }

    hide() {
        if (this.container) {
            this.container.style.display = 'none';
        }
    }

    show() {
        if (this.container) {
            this.container.style.display = 'block';
        }
    }

    renderError(message) {
        return `
            <div class="alert alert-danger" role="alert">
                <h4 class="alert-heading">Error</h4>
                <p>${message}</p>
            </div>
        `;
    }

    async render(state = {}) {
        try {
            // Check if required dependencies are met
            if (!this.shouldRender(state)) {
                this.container.innerHTML = this.renderSelectionMessage();
                this.hide();
                return;
            }

            this.show();
            const html = this.generateHTML(state);
            this.container.innerHTML = html;
            
            // Load game overview data
            await this.loadGameOverviewData(state);
            
            console.log('game-overview: Game overview content rendered');
        } catch (error) {
            console.error('Error rendering game overview content:', error);
            this.container.innerHTML = this.renderError('Failed to load game overview content');
        }
    }

    shouldRender(state) {
        // Show only when season, league, week, and round are selected but NO team is selected
        const hasTeam = state.team && state.team !== '' && state.team !== 'null';
        const hasRound = state.round && state.round !== '' && state.round !== 'null' && state.round !== null;
        const shouldShow = state.season && state.league && state.week && hasRound && !hasTeam;
        console.log(`🎮 GameOverviewBlock.shouldRender:`, {
            season: state.season,
            league: state.league,
            week: state.week,
            round: state.round,
            roundType: typeof state.round,
            hasTeam,
            hasRound,
            shouldShow
        });
        return shouldShow;
    }

    generateHTML(state) {
        return `
            <div class="card mb-4">
                <div class="card-header">
                    <h5 data-i18n="game_overview">Game Overview</h5>
                </div>
                <div class="card-body">
                    <div id="tableGameOverview">
                        <div class="text-center py-3">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">${typeof t === 'function' ? t('status.loading_data', 'Loading game overview...') : 'Loading game overview...'}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderSelectionMessage() {
        return `
            <div class="card mb-4">
                <div class="card-header">
                    <h5>${typeof t === 'function' ? t('block.game_overview.title', 'Game Overview') : 'Game Overview'}</h5>
                </div>
                <div class="card-body">
                    <div id="gameOverviewMessage" class="alert alert-info">
                        ${typeof t === 'function' ? t('msg.please_select.game', 'Please select a game/round.') : 'Please select a game/round.'}
                    </div>
                </div>
            </div>
        `;
    }

    async loadGameOverviewData(state) {
        const { season, league, week, round } = state;
        
        try {
            const response = await fetchWithDatabase(`/league/get_game_overview?season=${season}&league=${league}&week=${week}&round=${round}`);
            
            // Check if response is OK
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: `HTTP ${response.status}: ${response.statusText}` }));
                console.error('Error response from server:', errorData);
                const container = document.getElementById('tableGameOverview');
                if (container) {
                    container.innerHTML = `<div class="alert alert-danger">${typeof t === 'function' ? t('error_loading_data', 'Error loading game overview') : 'Error loading game overview'}: ${errorData.error || response.statusText}</div>`;
                }
                return;
            }
            
            const tableData = await response.json();
            
            // Check if response contains an error
            if (tableData.error) {
                console.error('Error in response data:', tableData.error);
                const container = document.getElementById('tableGameOverview');
                if (container) {
                    container.innerHTML = `<div class="alert alert-danger">${typeof t === 'function' ? t('error_loading_data', 'Error loading game overview') : 'Error loading game overview'}: ${tableData.error}</div>`;
                }
                return;
            }
            
            console.log('Game overview data:', tableData);
            
            const container = document.getElementById('tableGameOverview');
            if (container) {
                // Use Tabulator for the game overview table
                if (typeof createTableTabulator === 'function') {
                    console.log('Using createTableTabulator function for game overview table');
                    createTableTabulator('tableGameOverview', tableData, { 
                        disablePositionCircle: false, // Enable position circles for team and opponent positions
                        enableSpecialRowStyling: true,
                        tooltips: true,
                        enableHeatMap: true // Enable heatmap coloring for pins and points columns
                    });
                } else if (typeof createTableBootstrap3 === 'function') {
                    console.log('Fallback: Using createTableBootstrap3 function');
                    createTableBootstrap3('tableGameOverview', tableData, { 
                        disablePositionCircle: true,
                        enableSpecialRowStyling: true 
                    });
                } else {
                    console.error('No table creation function available');
                    container.innerHTML = `<div class="alert alert-warning">${typeof t === 'function' ? t('no_data', 'Table creation function not available') : 'Table creation function not available'}</div>`;
                }
            }
        } catch (error) {
            console.error('Error loading game overview:', error);
            const container = document.getElementById('tableGameOverview');
            if (container) {
                container.innerHTML = `<div class="alert alert-danger">${typeof t === 'function' ? t('error_loading_data', 'Error loading game overview') : 'Error loading game overview'}: ${error.message || error}</div>`;
            }
        }
    }
}

