/**
 * League Chart Utilities
 * 
 * Chart rendering and data visualization functions for league statistics
 * Extracted from monolithic league stats template
 */

// Chart instance references
let positionChart = null;

/**
 * Update shared legend for charts
 */
function updateSharedLegend(teams) {
    const colors = [
        '#28255c', '#592a6b', '#882c70', '#b4306b',
        '#d8405e', '#f25b4a', '#ff7f30', '#ffa600'
    ];
    
    const legendHtml = teams.map((team, index) => `
        <div class="legend-item d-inline-flex align-items-center me-3 mb-2">
            <div class="legend-color" style="
                background-color: ${colors[index % colors.length]}; 
                width: 12px; 
                height: 12px; 
                border-radius: 50%; 
                margin-right: 8px;
                
            "></div>
            <span>${team}</span>
        </div>
    `).join('');
    
    // Update multiple legend containers if they exist
    const legendContainers = ['sharedLegend', 'sharedLegendMiddle'];
    legendContainers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = legendHtml;
        }
    });
}

/**
 * Update position progression chart
 */
function updatePositionChart() {
    // Use global currentState with DOM fallback (same pattern as league-data-utils.js)
    console.log('🎯 updatePositionChart called - currentState:', currentState);
    
    // Early return if currentState is not properly initialized
    if (!currentState || (typeof currentState !== 'object')) {
        console.log('⚠️ updatePositionChart: currentState not ready, skipping...');
        return;
    }
    
    const selectedSeason = currentState?.season || document.querySelector('input[name="season"]:checked')?.value;
    const selectedLeague = currentState?.league || document.querySelector('input[name="league"]:checked')?.value;
    const currentWeek = currentState?.week || document.querySelector('input[name="week"]:checked')?.value;
    
    if (selectedSeason && selectedLeague) {
        const url = `/league/get_team_positions?season=${selectedSeason}&league=${selectedLeague}`;
        console.log('🔍 Fetching position chart from:', url);
        console.log('🔍 State values:', { selectedSeason, selectedLeague, currentWeek });
        
        fetch(url)
            .then(response => {
                console.log('📊 Position chart response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('📊 Position chart API response:', data);
                console.log('📊 Data structure keys:', Object.keys(data || {}));
                console.log('📊 data.data (teams):', data?.data ? Object.keys(data.data) : 'No data.data');
                
                // Validate data structure (SeriesData format)
                if (!data || !data.data || typeof data.data !== 'object') {
                    console.error('❌ Invalid position chart data structure:', data);
                    throw new Error('Invalid data structure: missing or invalid data object');
                }
                
                // Extract teams from data keys
                const teams = Object.keys(data.data);
                console.log('📊 Teams extracted:', teams);
                
                if (teams.length === 0) {
                    console.warn('⚠️ No teams found in position data');
                    return;
                }
                
                // Destroy existing chart if it exists
                if (positionChart) {
                    positionChart.destroy();
                    positionChart = null;
                }
                
                // Updated color palette
                const colors = [
                    '#28255c', '#592a6b', '#882c70', '#b4306b',
                    '#d8405e', '#f25b4a', '#ff7f30', '#ffa600'
                ];
                
                // Assign colors to teams
                const teamColors = teams.reduce((acc, team, index) => {
                    acc[team] = colors[index % colors.length];
                    return acc;
                }, {});
                
                // Update shared legend
                updateSharedLegend(teams);
                
                // Create week labels (assume all teams have same number of weeks)
                const firstTeam = teams[0];
                const weekCount = data.data[firstTeam]?.length || 0;
                const weekLabels = Array.from({length: weekCount}, (_, i) => `Week ${i + 1}`);
                
                console.log('📊 Week labels:', weekLabels);
                console.log('📊 Sample team data:', firstTeam, ':', data.data[firstTeam]);
                
                // Create new chart
                const canvas = document.getElementById('positionChart');
                if (canvas) {
                    positionChart = new Chart(canvas, {
                        type: 'line',
                        data: {
                            labels: weekLabels,
                            datasets: teams.map(team => ({
                                label: team,
                                data: data.data[team] || [],
                                borderColor: teamColors[team],
                                backgroundColor: teamColors[team],
                                fill: false,
                                tension: 0.1,
                                pointRadius: 4,
                                pointHoverRadius: 6,
                                borderWidth: 2,
                                pointStyle: 'circle',
                            }))
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: {
                                    reverse: true,
                                    min: 0.5,
                                    max: data.teams.length + 0.5,
                                    ticks: {
                                        stepSize: 1,
                                        callback: function(value) {
                                            return Number.isInteger(value) ? value : '';
                                        }
                                    },
                                    grid: {
                                        color: '#f0f0f0',
                                        offset: false,
                                        drawTicks: true,
                                        drawOnChartArea: true,
                                        z: 1,
                                        tickOffset: 0,
                                        tickLength: 0
                                    },
                                    afterFit: function(scaleInstance) {
                                        scaleInstance.options.grid.offset = false;
                                    },
                                    afterDataLimits: (scale) => {
                                        scale.min = 0.5;
                                        scale.max = data.teams.length + 0.5;
                                    },
                                    title: { 
                                        display: true, 
                                        text: 'Position',
                                        font: { weight: 'bold' },
                                        padding: { top: 10, bottom: 10 }
                                    }
                                },
                                x: {
                                    grid: {
                                        drawTicks: true
                                    },
                                    title: {
                                        display: true,
                                        text: window.translations ? (window.translations['match_day_label'] || 'Match Day') : 'Match Day',
                                        font: { weight: 'bold' },
                                        padding: { top: 10, bottom: 10 }
                                    }
                                }
                            },
                            plugins: {
                                tooltip: {
                                    callbacks: {
                                        label: function(context) {
                                            const team = context.dataset.label;
                                            const position = context.parsed.y;
                                            const points = data.data.find(d => 
                                                d.team === team && d.week === context.parsed.x
                                            )?.points || 'N/A';
                                            return `${team}: Position ${position} (${points} pts)`;
                                        }
                                    }
                                },
                                legend: {
                                    position: 'right',
                                    labels: {
                                        padding: 20,
                                        usePointStyle: true,
                                        pointStyle: 'circle',
                                        boxWidth: 10
                                    }
                                }
                            },
                            layout: {
                                padding: {
                                    top: 10,
                                    bottom: 10
                                }
                            }
                        }
                    });
                }
            })
            .catch(error => {
                console.error('Error loading position chart:', error);
                // Show error message in chart container
                const canvas = document.getElementById('positionChart');
                if (canvas && canvas.parentNode) {
                    canvas.parentNode.innerHTML = `
                        <div class="alert alert-danger">
                            <strong>Error loading position chart:</strong> ${error.message || 'Unknown error'}
                        </div>
                    `;
                }
            });
    }
}

/**
 * Get team color for charts
 */
function getTeamColor(teamName, teamIndex = 0) {
    const colors = [
        '#28255c', '#592a6b', '#882c70', '#b4306b',
        '#d8405e', '#f25b4a', '#ff7f30', '#ffa600'
    ];
    return colors[teamIndex % colors.length];
}

/**
 * Destroy all chart instances
 */
function destroyAllCharts() {
    if (positionChart) {
        positionChart.destroy();
        positionChart = null;
    }
    
    // Clear any chart containers that might have error messages
    const chartContainers = ['positionChart'];
    chartContainers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container && container.tagName !== 'CANVAS') {
            // If container is not a canvas, it might have error content - clear it
            const parent = container.parentNode;
            if (parent) {
                parent.innerHTML = `<canvas id="${containerId}"></canvas>`;
            }
        }
    });
}