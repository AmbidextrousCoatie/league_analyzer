class TeamPerformanceBlock {
    constructor() {
        this.containerId = 'team-performance';
        this.chartContainerId = 'team-performance-chart';
        this.container = document.getElementById(this.containerId);
        this.currentFilter = 'both'; // 'points', 'score', 'both'
        this.columnMetadata = null; // Store column info for filtering
    }

    shouldRender(state) {
        return state.league && state.season && state.team && !state.week;
    }

    async render(state = {}) {
        try {
            // Check if required dependencies are met
            if (!this.shouldRender(state)) {
                this.hide();
                return;
            }

            this.show();
            
            // Fetch data
            const data = await this.fetchData(state);
            
            
            if (!data || !data.performance_data || !data.performance_data.data || Object.keys(data.performance_data.data).length === 0) {
                this.renderError(typeof t === 'function' ? t('no_data', 'No performance data available for the selected team.') : 'No performance data available for the selected team.');
                return;
            }

            if (!this.container) {
                console.error(`${this.containerId}: Container not found`);
                return;
            }

            // Create the card structure - Top: Performance Table, Middle: Graphs side by side
            this.container.innerHTML = `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>${data.team} - ${typeof t === 'function' ? t('ui.team_performance.title', 'Performance Analysis') : 'Performance Analysis'}</h5>
                        <!--<p class="mb-0 text-muted">${typeof t === 'function' ? t('ui.team_performance.description', 'Individual player scores and team performance over time') : 'Individual player scores and team performance over time'}</p>-->
                    </div>
                    <div class="card-body">
                        <!-- Performance Table (Top) -->
                        <div class="row mb-4">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h6>${typeof t === 'function' ? t('ui.team_performance.individual', 'Individual Player Performance') : 'Individual Player Performance'}</h6>
                                        <!--<p class="mb-0 text-muted small">${typeof t === 'function' ? t('ui.team_performance.individual_desc', 'Player scores per week with totals and averages per game') : 'Player scores per week with totals and averages per game'}</p>-->
                                    </div>
                                    <div class="card-body">
                                        <div id="team-performance-table"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Performance Charts (Middle - Side by Side) -->
                        <div class="row mb-4">
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        <h6>${typeof t === 'function' ? t('score_per_match_day', 'Score per Match Day') : 'Score per Match Day'}</h6>
                                    </div>
                                    <div class="card-body">
                                        <div id="${this.chartContainerId}-bubble" style="height: 400px;"></div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="card">
                                    <div class="card-header">
                                        <h6>${typeof t === 'function' ? t('ui.win_percentage.weekly', 'Weekly Win %') : 'Weekly Win %'}</h6>
                                    </div>
                                    <div class="card-body">
                                        <div id="team-win-percentage-chart-bubble" style="height: 400px;"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Win Percentage Table (Bottom) -->
                        <div class="row">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h6>${typeof t === 'function' ? t('ui.win_percentage.individual', 'Individual Player Win Percentages') : 'Individual Player Win Percentages'}</h6>
                                        <p class="mb-0 text-muted small">${typeof t === 'function' ? t('ui.win_percentage.individual_desc', 'Player win percentages per week with totals') : 'Player win percentages per week with totals'}</p>
                                    </div>
                                    <div class="card-body">
                                        <div id="team-win-percentage-table"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Fetch and render tables and charts
            await Promise.all([
                this.loadPerformanceTable(state),
                this.loadWinPercentageTable(state)
            ]);
            
            // Render the performance bubble chart
            this.renderBubbleChart(data);
            
            // Fetch and render win percentage data for the second graph
            const winPercentageData = await this.fetchWinPercentageData(state);
            if (winPercentageData && winPercentageData.win_percentage_data) {
                this.renderWinPercentageBubbleChart(winPercentageData);
            }
            
        } catch (error) {
            console.error('Error rendering team performance analysis:', error);
            this.renderError(typeof t === 'function' ? t('error_loading_data', 'Failed to load team performance analysis data') : 'Failed to load team performance analysis data');
        }
    }

    async fetchData(filterState) {
        const url = new URL('/league/get_team_analysis', window.location.origin);
        
        // Add required parameters
        url.searchParams.append('league', filterState.league);
        url.searchParams.append('season', filterState.season);
        url.searchParams.append('team', filterState.team);
        
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

    async loadPerformanceTable(state) {
        const url = new URL('/league/get_team_performance_table', window.location.origin);
        url.searchParams.append('league', state.league);
        url.searchParams.append('season', state.season);
        url.searchParams.append('team', state.team);
        
        const database = getCurrentDatabase();
        if (database) {
            url.searchParams.append('database', database);
        }

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const tableData = await response.json();
            
            if (tableData.error) {
                throw new Error(`API Error: ${tableData.error}`);
            }

            // Extract player names for color mapping (from data, excluding team average)
            // Normalize player names (trim whitespace) for consistent color mapping
            const teamAverageKey = `${state.team} (Team Average)`;
            if (tableData.data && Array.isArray(tableData.data)) {
                const playerNames = tableData.data
                    .map(row => row.player_name ? String(row.player_name).trim() : null)
                    .filter(name => name && name !== teamAverageKey);
                if (window.updatePlayerColorMap && playerNames.length > 0) {
                    window.updatePlayerColorMap(playerNames);
                }
            }

            // Store column metadata for filtering
            this.storeColumnMetadata(tableData);

            // Pass directly to createTableTabulator (like timetable)
            if (typeof createTableTabulator === 'function') {
                createTableTabulator('team-performance-table', tableData, {
                    disablePositionCircle: false, // Enable colored circles based on player names
                    enableSpecialRowStyling: true,
                    disableTeamColorUpdate: true // We handle player colors manually
                });
            }

            // Apply current filter after table is created
            setTimeout(() => {
                console.log('Applying default filter:', this.currentFilter, 'Column metadata:', this.columnMetadata);
                this.applyFilter(this.currentFilter);
            }, 200);
        } catch (error) {
            console.error('Error loading performance table:', error);
        }
    }

    async fetchWinPercentageData(filterState) {
        try {
            const url = new URL('/league/get_team_analysis', window.location.origin);
            
            // Add required parameters
            url.searchParams.append('league', filterState.league);
            url.searchParams.append('season', filterState.season);
            url.searchParams.append('team', filterState.team);
            
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
        } catch (error) {
            console.error('Error fetching win percentage data:', error);
            return null;
        }
    }

    async loadWinPercentageTable(state) {
        const url = new URL('/league/get_team_win_percentage_table', window.location.origin);
        url.searchParams.append('league', state.league);
        url.searchParams.append('season', state.season);
        url.searchParams.append('team', state.team);
        
        const database = getCurrentDatabase();
        if (database) {
            url.searchParams.append('database', database);
        }

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const tableData = await response.json();
            
            if (tableData.error) {
                throw new Error(`API Error: ${tableData.error}`);
            }

            // Extract player names for color mapping (from data, excluding team)
            // Normalize player names (trim whitespace) for consistent color mapping
            const teamKey = `${state.team} (Team)`;
            if (tableData.data && Array.isArray(tableData.data)) {
                const playerNames = tableData.data
                    .map(row => row.player_name ? String(row.player_name).trim() : null)
                    .filter(name => name && name !== teamKey);
                if (window.updatePlayerColorMap && playerNames.length > 0) {
                    window.updatePlayerColorMap(playerNames);
                }
            }

            // Pass directly to createTableTabulator (like timetable)
            if (typeof createTableTabulator === 'function') {
                createTableTabulator('team-win-percentage-table', tableData, {
                    disablePositionCircle: false, // Enable colored circles based on player names
                    enableSpecialRowStyling: true,
                    disableTeamColorUpdate: true // We handle player colors manually
                });
            }
        } catch (error) {
            console.error('Error loading win percentage table:', error);
        }
    }

    renderWinPercentageBubbleChart(data) {
        const chartContainer = document.getElementById('team-win-percentage-chart-bubble');
        if (!chartContainer) {
            console.error('Win percentage bubble chart container not found');
            return;
        }

        if (typeof createScatterChartMultiAxis !== 'function') {
            console.error('createScatterChartMultiAxis function not available');
            return;
        }

        // Extract data from SeriesData format
        const winPercentageData = data.win_percentage_data;
        const labels = data.weeks;
        const teamKey = `${data.team} (Team)`;
        
        // Ensure player colors are set - normalize player names (trim whitespace)
        const playerNames = Object.keys(winPercentageData.data)
            .map(name => String(name).trim())
            .filter(name => name !== teamKey);
        if (window.updatePlayerColorMap && playerNames.length > 0) {
            window.updatePlayerColorMap(playerNames);
        }
        
        // Convert SeriesData format to scatter chart format
        const chartData = {};
        
        // Process each player/team in the win percentage data
        Object.keys(winPercentageData.data).forEach(playerName => {
            const playerData = winPercentageData.data[playerName];
            // Filter out null/undefined values for chart display
            chartData[playerName] = playerData.map(value => 
                value === null || value === undefined ? null : value
            );
        });

        // Generate week labels
        const weekLabel = typeof t === 'function' ? t('week', 'Week') : 'Week';
        const weekLabels = labels.map((week, index) => `${weekLabel} ${index + 1}`);

        // Create scatter chart using existing function
        const winPercentageLabel = typeof t === 'function' ? t('ui.win_percentage.win_percentage', 'Win %') : 'Win %';
        createScatterChartMultiAxis(
            chartData,
            Object.keys(chartData),
            'team-win-percentage-chart-bubble',
            (typeof t === 'function' ? t('ui.win_percentage.weekly', 'Weekly Win %') : 'Weekly Win %'),
            weekLabels,
            {
                minValue: 0,
                maxValue: 100,
                tooltipValueLabel: winPercentageLabel
            }
        );
    }

    renderBubbleChart(data) {
        const chartContainer = document.getElementById(`${this.chartContainerId}-bubble`);
        if (!chartContainer) {
            console.error(`${this.containerId}: Bubble chart container not found`);
            return;
        }

        if (typeof createScatterChartMultiAxis !== 'function') {
            console.error('createScatterChartMultiAxis function not available');
            return;
        }

        // Extract data from SeriesData format
        const performanceData = data.performance_data;
        const labels = data.weeks;
        const teamAverageKey = `${data.team} (Team Average)`;
        
        // Ensure player colors are set (should already be set from createPerformanceTable, but ensure it)
        // Normalize player names (trim whitespace) for consistent color mapping
        const playerNames = Object.keys(performanceData.data)
            .map(name => String(name).trim())
            .filter(name => name !== teamAverageKey);
        if (window.updatePlayerColorMap && playerNames.length > 0) {
            window.updatePlayerColorMap(playerNames);
        }
        
        // Convert SeriesData format to scatter chart format
        // The scatter chart expects data in the same format as line chart
        const chartData = {};
        
        // Process each player/team in the performance data
        Object.keys(performanceData.data).forEach(playerName => {
            const playerData = performanceData.data[playerName];
            // Filter out null/undefined values for chart display
            chartData[playerName] = playerData.map(value => 
                value === null || value === undefined ? null : value
            );
        });

        // Generate week labels
        const weekLabel = typeof t === 'function' ? t('week', 'Week') : 'Week';
        const weekLabels = labels.map((week, index) => `${weekLabel} ${index + 1}`);

        // Create scatter chart using existing function (getTeamColor will check playerColorMap as fallback)
        // Normalize circle sizes: values 150-250 map to circle sizes 20-80
        const pointsLabel = typeof t === 'function' ? t('pins', 'Punkte') : 'Punkte';
        createScatterChartMultiAxis(
            chartData,
            Object.keys(chartData),
            `${this.chartContainerId}-bubble`,
            (typeof t === 'function' ? t('points_per_match_day', 'Points per Match Day') : 'Points per Match Day'),
            weekLabels,
            {
                minValue: 160,
                maxValue: 230,
                tooltipValueLabel: pointsLabel
                //minCircleSize: 20,
                //maxCircleSize: 80
            }
        );
    }

    storeColumnMetadata(tableData) {
        // Extract all column fields and categorize them
        this.columnMetadata = {
            allFields: [],
            pointsFields: [],
            scoreFields: [],
            otherFields: []
        };

        if (!tableData.columns) {
            return;
        }

        // Flatten column structure to get all fields
        const flattenColumns = (columns) => {
            const fields = [];
            columns.forEach((group) => {
                if (group.columns && Array.isArray(group.columns)) {
                    group.columns.forEach((col) => {
                        if (col.field) {
                            fields.push(col.field);
                        }
                    });
                }
            });
            return fields;
        };

        const allFields = flattenColumns(tableData.columns);
        this.columnMetadata.allFields = allFields;

        // Categorize fields: points vs score
        allFields.forEach((field) => {
            const fieldLower = field.toLowerCase();
            // Check for points first (to catch avg_points, etc.)
            if (fieldLower.includes('points')) {
                this.columnMetadata.pointsFields.push(field);
            } else if (fieldLower.includes('score') || fieldLower.startsWith('week_')) {
                // Score fields: anything with "score" or week columns (week_1, week_2, etc.)
                this.columnMetadata.scoreFields.push(field);
            } else {
                // Other fields (player_name, player_initials, totals, etc.) - always show
                this.columnMetadata.otherFields.push(field);
            }
        });
    }

    attachFilterListeners() {
        // Use event delegation on document to catch events from dynamically created buttons
        // Remove any existing listener first to avoid duplicates
        if (this._filterListener) {
            document.removeEventListener('change', this._filterListener);
        }
        
        this._filterListener = (event) => {
            if (event.target.name === 'performanceFilter') {
                this.currentFilter = event.target.value;
                console.log('Filter changed to:', this.currentFilter);
                this.applyFilter(this.currentFilter);
            }
        };
        
        document.addEventListener('change', this._filterListener);
        
        // Wait for DOM to be ready, then verify buttons exist and set default
        setTimeout(() => {
            const defaultButton = document.getElementById('performanceFilterBoth');
            const pointsButton = document.getElementById('performanceFilterPoints');
            const scoreButton = document.getElementById('performanceFilterScore');
            
            console.log('🔍 Filter buttons check:', {
                both: !!defaultButton,
                points: !!pointsButton,
                score: !!scoreButton,
                container: this.container ? this.container.id : 'null'
            });
            
            if (!defaultButton || !pointsButton || !scoreButton) {
                console.warn('⚠️ Filter buttons not found in DOM!');
                return;
            }
            
            // Set default checked state
            defaultButton.checked = true;
            this.currentFilter = 'both';
            
            // Ensure visual state is correct
            const labels = document.querySelectorAll('label[for^="performanceFilter"]');
            labels.forEach(label => {
                const inputId = label.getAttribute('for');
                const input = document.getElementById(inputId);
                if (input && input.checked) {
                    label.classList.add('active');
                } else {
                    label.classList.remove('active');
                }
            });
            
            console.log('✅ Filter buttons initialized, default filter:', this.currentFilter);
        }, 100);
    }

    applyFilter(filterType) {
        const tableInstance = window['team-performance-tableInstance'];
        if (!tableInstance || !this.columnMetadata) {
            return;
        }

        const { pointsFields, scoreFields, otherFields } = this.columnMetadata;

        // Determine which fields to show
        let fieldsToShow = [];
        let fieldsToHide = [];

        if (filterType === 'points') {
            fieldsToShow = [...pointsFields, ...otherFields];
            fieldsToHide = scoreFields;
        } else if (filterType === 'score') {
            fieldsToShow = [...scoreFields, ...otherFields];
            fieldsToHide = pointsFields;
        } else {
            // 'both' - show all
            fieldsToShow = [...pointsFields, ...scoreFields, ...otherFields];
            fieldsToHide = [];
        }

        // Apply show/hide to columns
        try {
            // Get all columns from Tabulator
            const allColumns = tableInstance.getColumns();
            
            allColumns.forEach((column) => {
                const field = column.getField();
                if (!field) {
                    return; // Skip group headers
                }

                if (fieldsToHide.includes(field)) {
                    column.hide();
                } else if (fieldsToShow.includes(field)) {
                    column.show();
                }
            });
        } catch (error) {
            console.error('Error applying filter:', error);
        }
    }

    renderError(message) {
        if (this.container) {
            this.container.innerHTML = `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>${typeof t === 'function' ? t('block.team_performance.title', 'Team Performance Analysis') : 'Team Performance Analysis'}</h5>
                    </div>
                    <div class="card-body">
                        <div class="alert alert-warning" role="alert">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            ${message}
                        </div>
                    </div>
                </div>
            `;
        }
    }
}
