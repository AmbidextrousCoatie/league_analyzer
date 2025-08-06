/**
 * Legacy Team Chart Utilities
 * 
 * Extracted from team/stats.html with identical signatures
 * These functions preserve exact functionality during Phase 1 migration
 */

// Global variables (preserved from original)
window.currentTeamName = window.currentTeamName || null;
window.teamHistoryChart = window.teamHistoryChart || null;

/**
 * Update team history chart
 * Original function signature preserved exactly
 */
function updateTeamHistory(teamName) {
    // Set current team name for use in other charts
    window.currentTeamName = teamName;
    
    fetch(`/team/get_team_history?team_name=${teamName}`)
        .then(response => response.json())
        .then(data => {
            const seasons = Object.keys(data);
            const combinedPositions = seasons.map(season => {
                const leagueLevel = data[season].league_level;
                const position = data[season].final_position;
                return (leagueLevel - 1) * 10 + position;
            });
            
            const ctx = document.getElementById('chartTeamHistory').getContext('2d');
            if (window.teamHistoryChart instanceof Chart) {
                window.teamHistoryChart.destroy();
            }
            
            window.teamHistoryChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: seasons,
                    datasets: [{
                        label: teamName,
                        data: combinedPositions,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'transparent',
                        tension: 0.1,
                        pointRadius: 15,
                        pointHoverRadius: 17,
                        pointStyle: 'circle',
                        pointBackgroundColor: 'white',
                        pointBorderColor: 'rgba(255, 99, 132, 1)',
                        pointBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            reverse: true,
                            beginAtZero: false,
                            min: 1,
                            max: 70,
                            ticks: {
                                autoSkip: false,
                                stepSize: 1,
                                callback: function(value) {
                                    const midPoints = [5, 15, 25, 35, 45, 55, 65];
                                    if (midPoints.includes(value)) {
                                        const leagueNames = {
                                            1: "1. Bundesliga",
                                            2: "2. Bundesliga",
                                            3: "Bayernliga",
                                            4: "Landesliga",
                                            5: "Bezirksoberliga",
                                            6: "Bezirksliga",
                                            7: "Kreisliga"
                                        };
                                        const leagueLevel = Math.floor((value - 1) / 10) + 1;
                                        return leagueNames[leagueLevel];
                                    }
                                    return '';
                                },
                                font: {
                                    size: 12
                                },
                                color: '#000'
                            },
                            grid: {
                                color: (context) => {
                                    const value = context.tick.value;
                                    return value % 10 === 0 ? 'rgba(0, 0, 0, 0.1)' : 'transparent';
                                }
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: 'Platzierungsverlauf'
                        },
                        tooltip: {
                            enabled: true
                        },
                        legend: {
                            display: true
                        },
                        customLabels: {
                            afterDatasetsDraw(chart) {
                                const {ctx} = chart;
                                const meta = chart.getDatasetMeta(0);
                                
                                meta.data.forEach((point, index) => {
                                    const season = seasons[index];
                                    const position = data[season].final_position;
                                    
                                    ctx.save();
                                    ctx.textAlign = 'center';
                                    ctx.textBaseline = 'middle';
                                    ctx.font = 'bold 12px Arial';
                                    ctx.fillStyle = 'rgba(255, 99, 132, 1)';
                                    ctx.fillText(position.toString(), point.x, point.y);
                                    ctx.restore();
                                });
                            }
                        }
                    }
                },
                plugins: [{
                    id: 'customLabels',
                    afterDatasetsDraw(chart) {
                        const {ctx} = chart;
                        const meta = chart.getDatasetMeta(0);
                        
                        meta.data.forEach((point, index) => {
                            const season = seasons[index];
                            const position = data[season].final_position;
                            
                            ctx.save();
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.font = 'bold 12px Arial';
                            ctx.fillStyle = getTeamColor(teamName);
                            ctx.fillText(position.toString(), point.x, point.y);
                            ctx.restore();
                        });
                    }
                }]
            });
        });
}

/**
 * Update league comparison chart
 * Original function signature preserved exactly
 */
function updateLeagueComparison(teamName) {
    fetch(`/team/get_league_comparison?team_name=${teamName}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data || Object.keys(data).length === 0) {
                console.log('No league comparison data available');
                return;
            }
            
            const seasons = Object.keys(data).sort();
            const teamScores = seasons.map(season => data[season].team_performance.team_average_score);
            const leagueScores = seasons.map(season => data[season].league_averages.average_score);
            
            // Create area chart using the existing generic function
            createAreaChart_vanilla(
                leagueScores,  // Reference data (league averages)
                teamScores,    // Actual data (team averages)
                'chartLeagueComparison',
                'Team vs League Performance by Season',
                seasons        // Labels (seasons)
            );

            // Create comparison table
            const tableData = seasons.map(season => {
                const seasonData = data[season];
                return [
                    season,
                    seasonData.league_name,
                    seasonData.performance_rank,
                    seasonData.team_performance.team_average_score,
                    seasonData.league_averages.average_score,
                    seasonData.team_performance.vs_league_score > 0 ? 
                        `+${seasonData.team_performance.vs_league_score}` : 
                        seasonData.team_performance.vs_league_score
                ];
            });

            const tableConfig = {
                data: tableData,
                columns: [
                    { title: 'Saison' },
                    { title: 'Liga' },
                    { title: 'Platz' },
                    { title: 'Team Ø' },
                    { title: 'Liga Ø' },
                    { title: 'Differenz' }
                ],
                headerGroups: []
            };

            document.getElementById('tableLeagueComparison').innerHTML = createTable(tableConfig);
        })
        .catch(error => {
            console.error('Error loading league comparison data:', error);
        });
}

/**
 * Update clutch analysis chart and stats
 * Original function signature preserved exactly
 */
function updateClutchAnalysis(teamName, season) {
    console.log('updateClutchAnalysis called with:', { teamName, season });
    if (!teamName) {
        console.log('Missing team parameter for clutch analysis');
        return;
    }

    // Build URL with appropriate parameters
    let url = `/team/get_clutch_analysis?team_name=${encodeURIComponent(teamName)}`;
    if (season && season !== '') {
        url += `&season=${encodeURIComponent(season)}`;
    }

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Clutch analysis data received:', data);
            if (data.error) {
                console.error('Error in clutch analysis:', data.error);
                return;
            }

            // Create clutch performance chart
            const opponentClutch = data.opponent_clutch;
            console.log('About to create chart with opponentClutch:', opponentClutch);
            
            if (Object.keys(opponentClutch).length > 0) {
                console.log('Calling createClutchPerformanceChart...');
                console.log('Function exists?', typeof createClutchPerformanceChart);
                try {
                    createClutchPerformanceChart(
                        opponentClutch,
                        'chartClutchPerformance',
                        'Clutch Games Performance per Opponent (<10 point margin)'
                    );
                    console.log('createClutchPerformanceChart called successfully');
                } catch (error) {
                    console.error('Error in createClutchPerformanceChart:', error);
                }
            } else {
                console.log('No opponent data to chart');
            }

            // Display clutch statistics
            const statsHtml = `
                <div class="row text-center">
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body">
                                <h6>Total Games</h6>
                                <h4>${data.total_games}</h4>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body">
                                <h6>Clutch Games</h6>
                                <h4>${data.total_clutch_games}</h4>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body">
                                <h6>Clutch Wins</h6>
                                <h4 class="text-success">${data.total_clutch_wins}</h4>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card bg-light">
                            <div class="card-body">
                                <h6>Win %</h6>
                                <h4 class="text-primary">${data.clutch_percentage}%</h4>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById('clutchStats').innerHTML = statsHtml;
        })
        .catch(error => {
            console.error('Error loading clutch analysis data:', error);
        });
}

/**
 * Update consistency metrics display
 * Original function signature preserved exactly
 */
function updateConsistencyMetrics(teamName, season) {
    console.log('updateConsistencyMetrics called with:', { teamName, season });
    if (!teamName) {
        console.log('Missing team parameter for consistency metrics');
        return;
    }

    // Build URL with appropriate parameters
    let url = `/team/get_consistency_metrics?team_name=${encodeURIComponent(teamName)}`;
    if (season && season !== '') {
        url += `&season=${encodeURIComponent(season)}`;
    }

    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Consistency metrics data received:', data);
            if (data.error) {
                console.error('Error in consistency metrics:', data.error);
                return;
            }

            const metricsHtml = `
                <div class="row">
                    <div class="col-md-6">
                        <h6>Basic Statistics</h6>
                        <table class="table table-sm">
                            <tr><td>Average Score:</td><td><strong>${data.mean_score}</strong></td></tr>
                            <tr><td>Standard Deviation:</td><td><strong>${data.std_deviation}</strong></td></tr>
                            <tr><td>Coefficient of Variation:</td><td><strong>${data.coefficient_of_variation}%</strong></td></tr>
                            <tr><td>Consistency Rating:</td><td><strong class="text-primary">${data.consistency_rating}</strong></td></tr>
                        </table>
                    </div>
                    <div class="col-md-6">
                        <h6>Score Range</h6>
                        <table class="table table-sm">
                            <tr><td>Highest Score:</td><td><strong class="text-success">${data.max_score}</strong></td></tr>
                            <tr><td>Lowest Score:</td><td><strong class="text-danger">${data.min_score}</strong></td></tr>
                            <tr><td>Score Range:</td><td><strong>${data.score_range}</strong></td></tr>
                            <tr><td>Interquartile Range:</td><td><strong>${data.iqr}</strong></td></tr>
                        </table>
                    </div>
                </div>
            `;
            document.getElementById('consistencyMetrics').innerHTML = metricsHtml;
        })
        .catch(error => {
            console.error('Error loading consistency metrics data:', error);
        });
}

// Make functions globally available (preserve original behavior)
window.updateTeamHistory = updateTeamHistory;
window.updateLeagueComparison = updateLeagueComparison;
window.updateClutchAnalysis = updateClutchAnalysis;
window.updateConsistencyMetrics = updateConsistencyMetrics;