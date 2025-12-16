/**
 * Chart Adapters
 * 
 * Helper functions to bridge between content blocks and legacy chart functions
 * These adapters ensure compatibility without breaking existing interfaces
 */

/**
 * Adapter for createAreaChart_vanilla that works with canvas elements
 * 
 * @param {Array} referenceData - Reference data (league averages)
 * @param {Array} actualData - Actual data (team averages) 
 * @param {HTMLCanvasElement} canvas - Canvas element (not ID)
 * @param {string} title - Chart title
 * @param {Array} labels - Labels for x-axis
 * @returns {Chart} Chart.js instance
 */
function createAreaChart_forContentBlock(referenceData, actualData, canvas, title, labels) {
    if (!canvas || canvas.tagName !== 'CANVAS') {
        console.error('createAreaChart_forContentBlock: Invalid canvas element:', canvas);
        return null;
    }
    
    // Get canvas context
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('createAreaChart_forContentBlock: Could not get canvas context');
        return null;
    }
    
    console.log('createAreaChart_forContentBlock: Creating chart on canvas', canvas.id, 'with data:', {
        referenceData: referenceData.length,
        actualData: actualData.length,
        labels: labels.length,
        title
    });
    
    // Create the area chart with seasons on x-axis and averages on y-axis
    const chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels, // Seasons on x-axis
            datasets: [
                {
                    label: 'Reference (League Average)',
                    data: referenceData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                },
                {
                    label: 'Actual (Team Average)',
                    data: actualData,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: title
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Season'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Average Score'
                    },
                    beginAtZero: false
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    });
    
    console.log('createAreaChart_forContentBlock: Chart created successfully:', chartInstance);
    return chartInstance;
}

/**
 * Adapter for createLineChart that works with canvas elements
 * 
 * @param {HTMLCanvasElement} canvas - Canvas element
 * @param {Array} data - Chart data
 * @param {Array} labels - Labels for x-axis
 * @param {string} title - Chart title
 * @param {Object} options - Additional chart options
 * @returns {Chart} Chart.js instance
 */
function createLineChart_forContentBlock(canvas, data, labels, title, options = {}) {
    if (!canvas || canvas.tagName !== 'CANVAS') {
        console.error('createLineChart_forContentBlock: Invalid canvas element:', canvas);
        return null;
    }
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('createLineChart_forContentBlock: Could not get canvas context');
        return null;
    }
    
    const chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: title,
                data: data,
                borderColor: options.borderColor || 'rgba(255, 99, 132, 1)',
                backgroundColor: options.backgroundColor || 'transparent',
                borderWidth: options.borderWidth || 2,
                tension: options.tension || 0.1,
                pointRadius: options.pointRadius || 5,
                pointHoverRadius: options.pointHoverRadius || 7,
                ...options.datasetOptions
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: title
                },
                legend: {
                    display: options.showLegend !== false
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: options.xAxisTitle || 'X Axis'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: options.yAxisTitle || 'Y Axis'
                    },
                    beginAtZero: options.beginAtZero !== false,
                    ...options.yAxisOptions
                }
            },
            ...options.chartOptions
        }
    });
    
    return chartInstance;
}

/**
 * Helper function to get team color (shared utility)
 */
function getTeamColorForBlock(teamName) {
    if (window.ColorUtils && typeof window.ColorUtils.getTeamColor === 'function') {
        return window.ColorUtils.getTeamColor(teamName);
    }
    if (typeof getTeamColor === 'function') {
        return getTeamColor(teamName);
    }
    
    const fallbackColors = [
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 205, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)'
    ];
    
    let hash = 0;
    for (let i = 0; i < teamName.length; i++) {
        hash = teamName.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    return fallbackColors[Math.abs(hash) % fallbackColors.length];
}

// Make functions globally available
window.createAreaChart_forContentBlock = createAreaChart_forContentBlock;
window.createLineChart_forContentBlock = createLineChart_forContentBlock;
window.getTeamColorForBlock = getTeamColorForBlock;