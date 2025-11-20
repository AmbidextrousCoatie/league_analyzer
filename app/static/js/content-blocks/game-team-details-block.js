/**
 * GameTeamDetailsBlock - Shows individual player scores for a specific team in a specific round
 * Displays when: Season + League + Week + Team + Round are selected
 */
class GameTeamDetailsBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'game-team-details',
            containerId: 'gameTeamDetailsContainer',
            dataEndpoint: '/league/get_game_team_details',
            requiredFilters: ['season', 'league', 'week', 'team', 'round'],
            title: 'Game Team Details'
        });
        this.dependencies = ['season', 'league', 'week', 'team', 'round'];
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
            
            // Load game team details data
            await this.loadGameTeamDetailsData(state);
            
            console.log('game-team-details: Game team details content rendered');
        } catch (error) {
            console.error('Error rendering game team details content:', error);
            this.container.innerHTML = this.renderError('Failed to load game team details content');
        }
    }

    shouldRender(state) {
        // Show only when season, league, week, team, and round are all selected
        const hasRound = state.round && state.round !== '' && state.round !== 'null' && state.round !== null;
        const shouldShow = state.season && state.league && state.week && state.team && hasRound;
        console.log(`🎮 GameTeamDetailsBlock.shouldRender:`, {
            season: state.season,
            league: state.league,
            week: state.week,
            team: state.team,
            round: state.round,
            roundType: typeof state.round,
            hasRound,
            shouldShow
        });
        return shouldShow;
    }

    generateHTML(state) {
        return `
            <div class="card mb-4">
                <div class="card-header">
                    <h5 data-i18n="game_team_details">Game Team Details</h5>
                </div>
                <div class="card-body">
                    <div id="tableGameTeamDetails">
                        <div class="text-center py-3">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">${typeof t === 'function' ? t('status.loading_data', 'Loading team details...') : 'Loading team details...'}</span>
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
                    <h5>${typeof t === 'function' ? t('block.game_team_details.title', 'Game Team Details') : 'Game Team Details'}</h5>
                </div>
                <div class="card-body">
                    <div id="gameTeamDetailsMessage" class="alert alert-info">
                        ${typeof t === 'function' ? t('msg.please_select.team_game', 'Please select a team and game/round.') : 'Please select a team and game/round.'}
                    </div>
                </div>
            </div>
        `;
    }

    async loadGameTeamDetailsData(state) {
        const { season, league, week, team, round } = state;
        
        try {
            const response = await fetchWithDatabase(`/league/get_game_team_details?season=${season}&league=${league}&week=${week}&team=${encodeURIComponent(team)}&round=${round}`);
            
            // Check if response is OK
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: `HTTP ${response.status}: ${response.statusText}` }));
                console.error('Error response from server:', errorData);
                const container = document.getElementById('tableGameTeamDetails');
                if (container) {
                    container.innerHTML = `<div class="alert alert-danger">${typeof t === 'function' ? t('error_loading_data', 'Error loading game team details') : 'Error loading game team details'}: ${errorData.error || response.statusText}</div>`;
                }
                return;
            }
            
            const tableData = await response.json();
            
            // Check if response contains an error
            if (tableData.error) {
                console.error('Error in response data:', tableData.error);
                const container = document.getElementById('tableGameTeamDetails');
                if (container) {
                    container.innerHTML = `<div class="alert alert-danger">${typeof t === 'function' ? t('error_loading_data', 'Error loading game team details') : 'Error loading game team details'}: ${tableData.error}</div>`;
                }
                return;
            }
            
            console.log('Game team details data:', tableData);
            
            const container = document.getElementById('tableGameTeamDetails');
            if (container) {
                // Use the proper createTableBootstrap3 function for structured TableData
                if (typeof createTableBootstrap3 === 'function') {
                    console.log('Using createTableBootstrap3 function for game team details table');
                    createTableBootstrap3('tableGameTeamDetails', tableData, { 
                        disablePositionCircle: true, // Game team details doesn't need team color circles
                        enableSpecialRowStyling: true,
                        highlightLastRow: true // Highlight the totals row
                    });
                } else if (typeof createTable === 'function') {
                    console.log('Fallback: Using createTable function');
                    const tableHTML = createTable(tableData);
                    container.innerHTML = tableHTML;
                } else {
                    console.error('No table creation function available');
                    container.innerHTML = `<div class="alert alert-warning">${typeof t === 'function' ? t('no_data', 'Table creation function not available') : 'Table creation function not available'}</div>`;
                }
            }
        } catch (error) {
            console.error('Error loading game team details:', error);
            const container = document.getElementById('tableGameTeamDetails');
            if (container) {
                container.innerHTML = `<div class="alert alert-danger">${typeof t === 'function' ? t('error_loading_data', 'Error loading game team details') : 'Error loading game team details'}: ${error.message || error}</div>`;
            }
        }
    }
}

