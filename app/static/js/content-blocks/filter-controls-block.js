/**
 * FilterControlsBlock - Manages season, league, week, and team filter controls
 */
console.log('🔄 FilterControlsBlock class definition loaded');

class FilterControlsBlock extends BaseContentBlock {
    constructor() {
        console.log('🔄 FilterControlsBlock constructor called');
        super({
            id: 'filter-controls',
            containerId: 'filterControlsContainer',
            dataEndpoint: null, // Filter controls don't use a single endpoint
            requiredFilters: [],
            title: 'Filter Controls'
        });
        this.dependencies = [];
        this.container = document.getElementById(this.containerId);
        console.log('🔄 FilterControlsBlock container found:', !!this.container);
        
        // Debouncing and update management
        this.updateDebounceTimeout = null;
        this.isUpdating = false;
        this.pendingUpdates = new Set();
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

    dispatchEvent(eventName, data) {
        const event = new CustomEvent(eventName, { detail: data });
        document.dispatchEvent(event);
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
        console.log('🔄 FilterControlsBlock.render called with state:', state);
        try {
            const html = this.generateHTML(state);
            this.container.innerHTML = html;
            console.log('✅ HTML generated and set');
            
            // Set up event listeners
            this.attachEventListeners();
            console.log('✅ Event listeners attached');
            
            // Load initial data
            console.log('🔄 Starting to load filter data...');
            await this.loadFilterData(state);
            console.log('✅ Filter data loaded');
            
            console.log('filter-controls: Filter controls rendered');
        } catch (error) {
            console.error('❌ Error rendering filter controls:', error);
            this.container.innerHTML = this.renderError('Failed to load filter controls');
        }
    }

    generateHTML(state) {
        return `
            <div class="card mb-4">
                <div class="card-header">
                    <h4 data-i18n="league_statistics">League Statistics</h4>
                </div>
                <div class="card-body">
                    <div class="row mb-3">
                        <div class="col-md-4">
                            <h5 data-i18n="league">League</h5>
                            <div id="buttonsLeague" class="btn-group-horizontal w-100">
                                <span class="text-muted small">Loading leagues...</span>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h5 data-i18n="season">Season</h5>
                            <div id="buttonsSeason" class="btn-group-horizontal w-100">
                                <span class="text-muted small">Loading seasons...</span>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h5 data-i18n="week">Week</h5>
                            <div id="buttonsWeek" class="btn-group-horizontal w-100">
                                <span class="text-muted small">Select season and league</span>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-12">
                            <h5 data-i18n="team">Team</h5>
                            <div id="buttonsTeam" class="btn-group-horizontal w-100">
                                <span class="text-muted small">Select season and league</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Remove any existing event listeners to prevent duplicates
        if (this._clickHandler) {
            this.container.removeEventListener('click', this._clickHandler);
        }
        
        // Create the event handler function
        this._clickHandler = (event) => {
            if (event.target.type === 'radio' || event.target.tagName === 'LABEL') {
                // Get the radio input (either the clicked radio or the radio associated with the clicked label)
                const radio = event.target.type === 'radio' ? event.target : 
                             document.getElementById(event.target.getAttribute('for'));
                
                if (radio && radio.type === 'radio') {
                    // Prevent the default radio behavior completely
                    event.preventDefault();
                    event.stopPropagation();
                    
                    const filterType = radio.name;
                    const value = radio.value;
                    const currentState = this.getCurrentState();
                    
                    // Toggle logic: if already selected, deselect; otherwise select
                    if (currentState[filterType] === value) {
                        // Toggle off: set to null
                        this.handleFilterChange(filterType, null);
                    } else {
                        // Toggle on: set value
                        this.handleFilterChange(filterType, value);
                    }
                }
            }
        };
        
        // Add the event listener
        this.container.addEventListener('click', this._clickHandler);
    }

    async loadFilterData(state) {
        console.log('🔄 loadFilterData called with state:', state);
        
        try {
            // Load seasons and leagues in parallel (both should be available initially)
            console.log('🔄 Starting parallel load of seasons and leagues...');
            await Promise.all([
                this.updateSeasonButtons(state),
                this.updateLeagueButtons(state)
            ]);
            console.log('✅ Parallel load of seasons and leagues completed');
            
            // Load dependent filters if state has values
            if (state.season && state.league) {
                console.log('🔄 Loading dependent filters (weeks and teams)...');
                await Promise.all([
                    this.updateWeekButtons(state),
                    this.updateTeamButtons(state)
                ]);
                console.log('✅ Dependent filters loaded');
            } else if (state.season) {
                // If only season is selected, update leagues to show compatible ones
                console.log('🔄 Updating leagues for selected season...');
                await this.updateLeagueButtons(state);
            } else if (state.league) {
                // If only league is selected, update seasons to show compatible ones
                console.log('🔄 Updating seasons for selected league...');
                await this.updateSeasonButtons(state);
            }
        } catch (error) {
            console.error('❌ Error in loadFilterData:', error);
        }
    }

    async updateSeasonButtons(state) {
        try {
            console.log('🔄 Loading seasons with database:', getCurrentDatabase());
            // Always show all available seasons
            const response = await fetchWithDatabase('/league/get_available_seasons');
            const data = await response.json();
            console.log('✅ Seasons loaded:', data);
            
            let buttonsHtml = data.map(season => `
                <input type="radio" class="btn-check" name="season" id="season${season}" value="${season}" 
                       ${season === state.season ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="season${season}">${season}</label>
            `).join('');
            
            document.getElementById('buttonsSeason').innerHTML = buttonsHtml;
        } catch (error) {
            console.error('❌ Error loading seasons:', error);
            document.getElementById('buttonsSeason').innerHTML = '<span class="text-danger">Error loading seasons</span>';
        }
    }

    async updateLeagueButtons(state) {
        try {
            console.log('🔄 Loading leagues with database:', getCurrentDatabase(), 'season:', state.season);
            // Always show all available leagues (filter by season if selected for relevance)
            const url = state.season ? 
                `/league/get_available_leagues?season=${state.season}` : 
                '/league/get_available_leagues';
            
            const response = await fetchWithDatabase(url);
            const data = await response.json();
            console.log('✅ Leagues loaded:', data);
            
            let buttonsHtml = data.map(league => `
                <input type="radio" class="btn-check" name="league" id="league${league}" value="${league}"
                       ${league === state.league ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="league${league}">${league}</label>
            `).join('');
            
            document.getElementById('buttonsLeague').innerHTML = buttonsHtml;
        } catch (error) {
            console.error('❌ Error loading leagues:', error);
            document.getElementById('buttonsLeague').innerHTML = '<span class="text-danger">Error loading leagues</span>';
        }
    }

    async updateWeekButtons(state) {
        const selectedSeason = state.season;
        const selectedLeague = state.league;
        
        if (!selectedSeason || !selectedLeague) {
            document.getElementById('buttonsWeek').innerHTML = '<span class="text-muted">Select season and league first</span>';
            return;
        }

        try {
            // Always show all available weeks for the season/league combination
            const response = await fetchWithDatabase(`/league/get_available_weeks?season=${selectedSeason}&league=${selectedLeague}`);
            const data = await response.json();
            
            let buttonsHtml = data.map(week => `
                <input type="radio" class="btn-check" name="week" id="week${week}" value="${week}"
                       ${week.toString() === state.week ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="week${week}">${week}</label>
            `).join('');
            
            document.getElementById('buttonsWeek').innerHTML = buttonsHtml;
        } catch (error) {
            console.error('Error loading weeks:', error);
            document.getElementById('buttonsWeek').innerHTML = '<span class="text-danger">Error loading weeks</span>';
        }
    }

    async updateTeamButtons(state) {
        const selectedSeason = state.season;
        const selectedLeague = state.league;
        
        if (!selectedSeason || !selectedLeague) {
            document.getElementById('buttonsTeam').innerHTML = '<span class="text-muted">Select season and league first</span>';
            return;
        }

        try {
            // Always show all available teams for the season/league combination
            const response = await fetchWithDatabase(`/league/get_available_teams?season=${selectedSeason}&league=${selectedLeague}`);
            const data = await response.json();
            
            let buttonsHtml = data.map(team => `
                <input type="radio" class="btn-check" name="team" id="team${team.replace(/\s+/g, '')}" value="${team}"
                       ${team === state.team ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="team${team.replace(/\s+/g, '')}">${team}</label>
            `).join('');
            
            document.getElementById('buttonsTeam').innerHTML = buttonsHtml;
        } catch (error) {
            console.error('Error loading teams:', error);
            document.getElementById('buttonsTeam').innerHTML = '<span class="text-danger">Error loading teams</span>';
        }
    }

    handleFilterChange(filterType, value) {
        // Prevent multiple simultaneous updates
        if (this.isUpdating) {
            console.log('Update already in progress, queueing change:', { type: filterType, value });
            this.pendingUpdates.add({ filterType, value });
            return;
        }
        
        console.log('Filter changed:', { type: filterType, value });
        
        // Clear any existing debounce timeout
        if (this.updateDebounceTimeout) {
            clearTimeout(this.updateDebounceTimeout);
        }
        
        // Debounce the update to prevent rapid-fire changes
        this.updateDebounceTimeout = setTimeout(() => {
            this.performFilterUpdate(filterType, value);
        }, 150); // 150ms debounce
    }

    async performFilterUpdate(filterType, value) {
        if (this.isUpdating) return;
        
        try {
            this.isUpdating = true;
            console.log('Performing filter update:', { type: filterType, value });
            
            // Create new state object with the changed filter
            const newState = { ...this.getCurrentState() };
            newState[filterType] = value;
            
            // Smart conflict resolution: check if combination is valid
            const validatedState = await this.validateAndFixState(newState, filterType);
            
            console.log('Validated state:', validatedState);
            
            // Update UI to reflect validated state (uncheck conflicting buttons)
            this.syncButtonsWithState(validatedState);
            
            // Batch update dependent filter buttons
            await this.batchUpdateDependentFilters(filterType, validatedState);
            
            // Dispatch filter change event (this will trigger content updates)
            this.dispatchEvent('filterChange', validatedState);
            
            console.log('Filter update completed');
            
        } catch (error) {
            console.error('Error during filter update:', error);
        } finally {
            this.isUpdating = false;
            
            // Process any pending updates
            if (this.pendingUpdates.size > 0) {
                const nextUpdate = Array.from(this.pendingUpdates)[0];
                this.pendingUpdates.clear();
                console.log('Processing pending update:', nextUpdate);
                setTimeout(() => {
                    this.handleFilterChange(nextUpdate.filterType, nextUpdate.value);
                }, 50);
            }
        }
    }

    async batchUpdateDependentFilters(changedFilter, state) {
        console.log('Batch updating dependent filters for:', changedFilter);
        
        try {
            // Determine which filters need updating based on what changed
            const updatesNeeded = [];
            
            switch (changedFilter) {
                case 'season':
                    updatesNeeded.push(
                        this.updateLeagueButtons(state),
                        this.updateWeekButtons(state),
                        this.updateTeamButtons(state)
                    );
                    break;
                case 'league':
                    updatesNeeded.push(
                        this.updateWeekButtons(state),
                        this.updateTeamButtons(state)
                    );
                    break;
                case 'week':
                    updatesNeeded.push(
                        this.updateTeamButtons(state)
                    );
                    break;
                // Team doesn't have dependent filters
            }
            
            // Execute all updates in parallel
            if (updatesNeeded.length > 0) {
                await Promise.all(updatesNeeded);
                console.log('Batch filter updates completed');
            }
            
        } catch (error) {
            console.error('Error during batch filter update:', error);
        }
    }

    async updateDependentFilters(changedFilter, state) {
        // Legacy method - now redirects to batch update
        return this.batchUpdateDependentFilters(changedFilter, state);
    }



    async validateAndFixState(state, changedFilter) {
        const validatedState = { ...state };
        
        try {
            // Check season + league combination
            if (validatedState.season && validatedState.league) {
                const isValidCombo = await this.isValidSeasonLeagueCombo(validatedState.season, validatedState.league);
                if (!isValidCombo) {
                    console.log('Invalid season/league combo, clearing dependent filters');
                    if (changedFilter === 'season') {
                        // Season changed, keep season and clear league + dependents
                        validatedState.league = null;
                        validatedState.week = null;
                        validatedState.team = null;
                    } else if (changedFilter === 'league') {
                        // League changed, keep league and clear season + dependents  
                        validatedState.season = null;
                        validatedState.week = null;
                        validatedState.team = null;
                    }
                }
            }
            
            // Check week validity
            if (validatedState.season && validatedState.league && validatedState.week) {
                const isValidWeek = await this.isValidWeek(validatedState.season, validatedState.league, validatedState.week);
                if (!isValidWeek) {
                    console.log('Invalid week, clearing week and team');
                    validatedState.week = null;
                    validatedState.team = null;
                }
            }
            
            // Check team validity
            if (validatedState.season && validatedState.league && validatedState.team) {
                const isValidTeam = await this.isValidTeam(validatedState.season, validatedState.league, validatedState.team);
                if (!isValidTeam) {
                    console.log('Invalid team, clearing team');
                    validatedState.team = null;
                }
            }
            
            // Clear dependent filters when parent is missing
            if (!validatedState.season || !validatedState.league) {
                validatedState.week = null;
                validatedState.team = null;
            }
            
            if (!validatedState.week) {
                validatedState.team = null;
            }
            
        } catch (error) {
            console.error('Error during state validation:', error);
            // On error, clear dependent filters for safety
            if (changedFilter === 'season') {
                validatedState.week = null;
                validatedState.team = null;
            } else if (changedFilter === 'league') {
                validatedState.week = null;
                validatedState.team = null;
            }
        }
        
        return validatedState;
    }

    async isValidSeasonLeagueCombo(season, league) {
        try {
            const response = await fetchWithDatabase(`/league/get_available_leagues?season=${season}`);
            const leagues = await response.json();
            return leagues.includes(league);
        } catch (error) {
            console.error('Error checking season/league combo:', error);
            return false;
        }
    }

    async isValidWeek(season, league, week) {
        try {
            const response = await fetchWithDatabase(`/league/get_available_weeks?season=${season}&league=${league}`);
            const weeks = await response.json();
            return weeks.includes(parseInt(week));
        } catch (error) {
            console.error('Error checking week validity:', error);
            return false;
        }
    }

    async isValidTeam(season, league, team) {
        try {
            const response = await fetchWithDatabase(`/league/get_available_teams?season=${season}&league=${league}`);
            const teams = await response.json();
            return teams.includes(team);
        } catch (error) {
            console.error('Error checking team validity:', error);
            return false;
        }
    }

    syncButtonsWithState(state) {
        // Sync buttons to match the validated state (including null values)
        const filterTypes = ['season', 'league', 'week', 'team'];
        
        filterTypes.forEach(filterType => {
            const currentlyChecked = document.querySelector(`input[name="${filterType}"]:checked`);
            const shouldBeChecked = state[filterType];
            
            // Only sync if there's actually a mismatch
            const currentValue = currentlyChecked?.value || null;
            if (currentValue !== shouldBeChecked) {
                // If state says null, uncheck any currently checked button
                if (!shouldBeChecked) {
                    if (currentlyChecked) {
                        currentlyChecked.checked = false;
                        console.log(`Synced: Unchecked ${filterType}: ${currentlyChecked.value} (state is null)`);
                    }
                } else {
                    // If state has a value, ensure the correct button is checked
                    // Uncheck conflicting button if exists
                    if (currentlyChecked) {
                        currentlyChecked.checked = false;
                        console.log(`Synced: Unchecked conflicting ${filterType}: ${currentlyChecked.value}`);
                    }
                    
                    // Check the correct button
                    const correctButton = document.querySelector(`input[name="${filterType}"][value="${shouldBeChecked}"]`);
                    if (correctButton) {
                        correctButton.checked = true;
                        console.log(`Synced: Checked correct ${filterType}: ${shouldBeChecked}`);
                    }
                }
            }
        });
    }

    getCurrentState() {
        return {
            season: document.querySelector('input[name="season"]:checked')?.value || null,
            league: document.querySelector('input[name="league"]:checked')?.value || null,
            week: document.querySelector('input[name="week"]:checked')?.value || null,
            team: document.querySelector('input[name="team"]:checked')?.value || null
        };
    }
}