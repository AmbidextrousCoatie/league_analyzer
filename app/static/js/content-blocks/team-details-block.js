/**
 * TeamDetailsBlock - Shows team-specific score sheets and details
 * Displays when: Season + League + Week + Team are selected
 */
class TeamDetailsBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'team-details',
            containerId: 'teamDetailsContainer',
            dataEndpoint: '/league/get_team_week_details_table',
            requiredFilters: ['season', 'league', 'week', 'team'],
            title: 'Team Details'
        });
        this.dependencies = ['season', 'league', 'week', 'team'];
        this.currentView = 'classic';
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
                this.container.innerHTML = this.renderSelectionMessage(state);
                this.hide();
                return;
            }

            this.show();
            const html = this.generateHTML(state);
            this.container.innerHTML = html;
            
            // Set up event listeners for view toggle
            this.attachEventListeners();
            
            // Load team data
            await this.loadTeamData(state);
            
            console.log('team-details: Team details rendered');
        } catch (error) {
            console.error('Error rendering team details:', error);
            this.container.innerHTML = this.renderError('Failed to load team details');
        }
    }

    shouldRender(state) {
        // Show only when season, league, week, and team are selected but NO round is selected
        // (when round is selected, game-team-details-block should show instead)
        const hasRound = state.round && state.round !== '' && state.round !== 'null';
        return state.season && state.league && state.week && state.team && !hasRound;
    }

    generateHTML(state) {
        const matchDayText = window.translations ? 
            (window.translations['match_day'] || 'Match Day') : 
            'Match Day';

        return `
            <div class="card mb-4">
                <div class="card-body">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <div>
                                <h5 data-i18n="score_sheet_selected_team">Score Sheet for Selected Team</h5>
                                <div id="teamDetailsMetadata" class="text-muted small">
                                    ${state.team} - ${matchDayText} ${state.week}
                                </div>
                            </div>
                            <div class="btn-group" role="group" aria-label="View options">
                                <input type="radio" class="btn-check" name="teamView" id="teamViewClassic" value="classic" checked>
                                <label class="btn btn-outline-primary btn-sm" for="teamViewClassic">${typeof t === 'function' ? t('block.team_details.view.classic', 'Classic') : 'Classic'}</label>
                                <input type="radio" class="btn-check" name="teamView" id="teamViewNew" value="new">
                                <label class="btn btn-outline-primary btn-sm" for="teamViewNew">${typeof t === 'function' ? t('block.team_details.view.new', 'New') : 'New'}</label>
                            </div>
                        </div>
                        <div class="card-body">
                            <div id="teamTableWeekDetails">
                                <div class="text-center py-3">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Loading team details...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>  
                    
                    <!-- Team Individual Averages Section -->
                    <div class="card mt-4">
                        <div class="card-header">
                            <h6 data-i18n="team_individual_averages">Team Individual Averages</h6>
                            <p class="mb-0 text-muted small">Player statistics for this team in this specific week</p>
                        </div>
                        <div class="card-body">
                            <div id="teamIndividualAveragesTable">
                                <div class="text-center py-3">
                                    <div class="spinner-border text-primary" role="status">
                                        <span class="visually-hidden">Loading team individual averages...</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderSelectionMessage(state) {
        let message = '';
        
        if (!state.season || !state.league) {
            message = typeof t === 'function' ? t('msg.please_select.season_league', 'Please select a season and league first.') : 'Please select a season and league first.';
        } else if (!state.week) {
            message = typeof t === 'function' ? t('msg.please_select.match_day', 'Please select a match day to view team details.') : 'Please select a match day to view team details.';
        } else if (!state.team) {
            message = typeof t === 'function' ? t('msg.please_select.team', 'Please select a team to display the score sheet.') : 'Please select a team to display the score sheet.';
        }

        return `
            <div class="card mb-4">
                <div class="card-body">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <div>
                                <h5>${typeof t === 'function' ? t('block.team_details.title', 'Score Sheet for Selected Team') : 'Score Sheet for Selected Team'}</h5>
                                <div id="teamDetailsMetadata" class="text-muted small"></div>
                            </div>
                            <div class="btn-group" role="group" aria-label="View options">
                                <input type="radio" class="btn-check" name="teamView" id="teamViewClassic" value="classic" checked>
                                <label class="btn btn-outline-primary btn-sm" for="teamViewClassic">Classic</label>
                                <input type="radio" class="btn-check" name="teamView" id="teamViewNew" value="new">
                                <label class="btn btn-outline-primary btn-sm" for="teamViewNew">New</label>
                            </div>
                        </div>
                        <div class="card-body">
                            <div id="teamTableWeekDetails">
                                <div class="alert alert-info" data-i18n="please_select_team">${message}</div>
                            </div>
                        </div>
                    </div>  
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Listen for view toggle changes
        this.container.addEventListener('change', (event) => {
            if (event.target.name === 'teamView') {
                this.currentView = event.target.value;
                this.handleViewChange();
            }
        });
    }

    async loadTeamData(state) {
        const { season, league, week, team } = state;
        
        try {
            // Load team details and individual averages in parallel
            await Promise.all([
                this.loadTeamWeekDetails(season, league, week, team, this.currentView),
                this.loadTeamIndividualAverages(state)
            ]);
        } catch (error) {
            console.error('Error loading team data:', error);
        }
    }

    async loadTeamWeekDetails(season, league, week, team, view = 'classic') {
        try {
            // Determine endpoint based on view
            let endpoint = '/league/get_team_week_details_table';
            if (view === 'new') {
                endpoint = '/league/get_team_individual_scores_table';
            } else if (view === 'newFull') {
                endpoint = '/league/get_team_week_head_to_head_table';
            }
            
            console.log(`Loading team details with view: ${view}, endpoint: ${endpoint}`);
            
            const response = await fetchWithDatabase(`${endpoint}?season=${season}&league=${league}&week=${week}&team=${team}`);
            const tableData = await response.json();
            
            console.log('Team week details table data:', tableData); // Debug logging
            
            const container = document.getElementById('teamTableWeekDetails');
            if (container) {
                // Determine table options based on view
                const tableOptions = {
                    disablePositionCircle: true, // Team details should never show color circles for player numbers
                    mergeCells: view === 'newFull',
                    enableSpecialRowStyling: true
                };
                
                // Use the proper createTableBootstrap3 function for structured TableData
                if (typeof createTableBootstrap3 === 'function') {
                    console.log(`Using createTableBootstrap3 function for team details (${view} view)`);
                    createTableBootstrap3('teamTableWeekDetails', tableData, tableOptions);
                } else if (typeof createTable === 'function') {
                    console.log('Fallback: Using createTable function');
                    const tableHTML = createTable(tableData);
                    container.innerHTML = tableHTML;
                } else {
                    console.error('No table creation function available');
                    container.innerHTML = '<div class="alert alert-warning">Table creation function not available</div>';
                }
            }
        } catch (error) {
            console.error('Error loading team week details:', error);
            const container = document.getElementById('teamTableWeekDetails');
            if (container) {
                container.innerHTML = '<div class="alert alert-danger">Error loading team details</div>';
            }
        }
    }

    async handleViewChange() {
        // Get current state from the parent app
        const currentState = this.getCurrentState();
        
        if (this.shouldRender(currentState)) {
            // Reload team details with new view
            await this.loadTeamWeekDetails(
                currentState.season, 
                currentState.league, 
                currentState.week, 
                currentState.team, 
                this.currentView
            );
        }
    }

    getCurrentState() {
        // Get state from filter controls or parent app
        return {
            season: document.querySelector('input[name="season"]:checked')?.value || null,
            league: document.querySelector('input[name="league"]:checked')?.value || null,
            week: document.querySelector('input[name="week"]:checked')?.value || null,
            team: document.querySelector('input[name="team"]:checked')?.value || null
        };
    }

    async loadTeamIndividualAverages(state) {
        const { season, league, week, team } = state;
        
        try {
            console.log(`Loading team individual averages for ${team} in ${league} ${season} week ${week}`);
            
            const url = `/league/get_individual_averages?league=${encodeURIComponent(league)}&season=${encodeURIComponent(season)}&week=${encodeURIComponent(week)}&team=${encodeURIComponent(team)}`;
            console.log(`Fetching team individual averages from: ${url}`);
            
            const response = await fetchWithDatabase(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Team individual averages data received:', data);
            
            // Create the table using the existing createTableBootstrap3 function
            if (typeof createTableBootstrap3 === 'function' && data) {
                createTableBootstrap3('teamIndividualAveragesTable', data, {
                    disablePositionCircle: true, // Individual averages don't need team colors
                    enableSpecialRowStyling: true
                });
                console.log('Team individual averages table created successfully');
            } else {
                console.warn('createTableBootstrap3 not available or no data received');
                const container = document.getElementById('teamIndividualAveragesTable');
                if (container) {
                    container.innerHTML = '<div class="alert alert-info">Team individual averages data not available</div>';
                }
            }
            
        } catch (error) {
            console.error('Error loading team individual averages:', error);
            const container = document.getElementById('teamIndividualAveragesTable');
            if (container) {
                container.innerHTML = '<div class="alert alert-danger">Error loading team individual averages</div>';
            }
        }
    }
}