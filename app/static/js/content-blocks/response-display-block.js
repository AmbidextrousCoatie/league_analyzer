/**
 * Response Display Content Block
 * 
 * Shows detailed response data in a structured, interactive format
 * Provides JSON viewer, data statistics, and response analysis
 */

class ResponseDisplayBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'response-display',
            containerId: 'responseDisplayContainer',
            title: 'Response Data Viewer',
            description: 'Interactive display of API response data'
        });
        
        this.currentResponse = null;
        this.viewMode = 'json'; // json, table, stats, chart
        this.chartType = 'line'; // line, bar, scatter, area
        this.chartInstance = null;
    }
    
    /**
     * Can always render
     */
    canRender(filterState) {
        return true;
    }
    
    /**
     * Render the response display interface
     */
    async render(data, filterState) {
        const container = this.getContainer();
        if (!container) {
            throw new Error('Response display container not found');
        }
        
        container.innerHTML = this.createResponseDisplayInterface();
        this.attachEventListeners();
        
        // Listen for route test results
        this.setupRouteTestListener();
        
        console.log(`${this.id}: Response display interface rendered`);
    }
    
    /**
     * Create the response display interface
     */
    createResponseDisplayInterface() {
        return `
            <div class="response-display-block">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5>Response Data Viewer</h5>
                    <div class="btn-group btn-group-sm" role="group">
                        <input type="radio" class="btn-check" name="viewMode" id="viewJson" value="json" checked>
                        <label class="btn btn-outline-primary" for="viewJson">
                            <i class="bi bi-code me-1"></i>JSON
                        </label>
                        
                        <input type="radio" class="btn-check" name="viewMode" id="viewTable" value="table">
                        <label class="btn btn-outline-primary" for="viewTable">
                            <i class="bi bi-table me-1"></i>Table
                        </label>
                        
                        <input type="radio" class="btn-check" name="viewMode" id="viewStats" value="stats">
                        <label class="btn btn-outline-primary" for="viewStats">
                            <i class="bi bi-bar-chart me-1"></i>Stats
                        </label>
                        
                        <input type="radio" class="btn-check" name="viewMode" id="viewChart" value="chart">
                        <label class="btn btn-outline-primary" for="viewChart">
                            <i class="bi bi-graph-up me-1"></i>Chart
                        </label>
                    </div>
                </div>
                
                <div class="response-content-area">
                    <div class="empty-state text-center p-5">
                        <i class="bi bi-box text-muted" style="font-size: 3rem;"></i>
                        <h6 class="text-muted mt-2">No Response Data</h6>
                        <p class="text-muted small">Test an API route to see response data here</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const container = this.getContainer();
        
        // View mode toggle
        container.addEventListener('change', (event) => {
            if (event.target.name === 'viewMode') {
                this.viewMode = event.target.value;
                this.updateResponseDisplay();
            } else if (event.target.name === 'chartType') {
                this.chartType = event.target.value;
                if (this.viewMode === 'chart') {
                    this.renderChart();
                }
            }
        });
    }
    
    /**
     * Setup listener for route test results
     */
    setupRouteTestListener() {
        // Listen for custom events from route test block
        document.addEventListener('routeTestComplete', (event) => {
            const { endpoint, result } = event.detail;
            this.displayResponse(result);
        });
        
        // Also make it available globally for direct calls
        window.responseDisplayBlock = this;
    }
    
    /**
     * Display response data
     */
    displayResponse(responseData) {
        this.currentResponse = responseData;
        this.updateResponseDisplay();
    }
    
    /**
     * Update the response display based on current view mode
     */
    updateResponseDisplay() {
        const container = this.getContainer();
        const contentArea = container.querySelector('.response-content-area');
        
        if (!this.currentResponse) {
            contentArea.innerHTML = `
                <div class="empty-state text-center p-5">
                    <i class="bi bi-box text-muted" style="font-size: 3rem;"></i>
                    <h6 class="text-muted mt-2">No Response Data</h6>
                    <p class="text-muted small">Test an API route to see response data here</p>
                </div>
            `;
            return;
        }
        
        switch (this.viewMode) {
            case 'json':
                contentArea.innerHTML = this.renderJsonView();
                break;
            case 'table':
                contentArea.innerHTML = this.renderTableView();
                break;
            case 'stats':
                contentArea.innerHTML = this.renderStatsView();
                break;
            case 'chart':
                contentArea.innerHTML = this.renderChartView();
                this.renderChart();
                break;
        }
    }
    
    /**
     * Render JSON view
     */
    renderJsonView() {
        const responseInfo = this.currentResponse.success ? 
            `<div class="alert alert-success alert-sm">
                <strong>Success!</strong> ${this.currentResponse.status} ${this.currentResponse.statusText}
                <span class="float-end">${this.currentResponse.duration}ms</span>
            </div>` :
            `<div class="alert alert-danger alert-sm">
                <strong>Error!</strong> ${this.currentResponse.error || this.currentResponse.statusText}
            </div>`;
        
        return `
            ${responseInfo}
            <div class="json-viewer">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <small class="text-muted">Response Data:</small>
                    <button class="btn btn-outline-secondary btn-sm" onclick="window.responseDisplayBlock.copyToClipboard()">
                        <i class="bi bi-clipboard me-1"></i>Copy JSON
                    </button>
                </div>
                <pre class="json-display p-3 bg-light border rounded" style="max-height: 500px; overflow-y: auto;"><code>${this.formatJSON(this.currentResponse.data)}</code></pre>
            </div>
        `;
    }
    
    /**
     * Render table view (for array data)
     */
    renderTableView() {
        const data = this.currentResponse.data;
        
        // Handle TableData structure from backend
        if (data && typeof data === 'object' && data.columns && data.data) {
            // This is a TableData object - use it directly
            const tableHTML = createTable(data);
            const itemCount = Array.isArray(data.data) ? data.data.length : 'unknown';
            
            return `
                <div class="table-viewer">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <small class="text-muted">${data.title || 'Response Data'} (${itemCount} items):</small>
                        <button class="btn btn-outline-secondary btn-sm" onclick="window.responseDisplayBlock.exportTable()">
                            <i class="bi bi-download me-1"></i>Export CSV
                        </button>
                    </div>
                    <div class="table-responsive" style="max-height: 500px; overflow-y: auto;">
                        ${tableHTML}
                    </div>
                </div>
            `;
        }
        
        // Handle array data (original logic)
        if (!Array.isArray(data) || data.length === 0) {
            return `
                <div class="alert alert-info">
                    <i class="bi bi-info-circle me-2"></i>
                    Table view is only available for array data or TableData objects. Current response contains ${typeof data} data.
                </div>
                ${this.renderJsonView()}
            `;
        }
        
        // Use existing createTable function for array data
        const tableConfig = this.generateTableConfig(data);
        const tableHTML = createTable(tableConfig);
        
        return `
            <div class="table-viewer">
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <small class="text-muted">Response Data (${data.length} items):</small>
                    <button class="btn btn-outline-secondary btn-sm" onclick="window.responseDisplayBlock.exportTable()">
                        <i class="bi bi-download me-1"></i>Export CSV
                    </button>
                </div>
                <div class="table-responsive" style="max-height: 500px; overflow-y: auto;">
                    ${tableHTML}
                </div>
            </div>
        `;
    }
    
    /**
     * Render statistics view
     */
    renderStatsView() {
        const stats = this.generateDataStats(this.currentResponse.data);
        
        return `
            <div class="stats-viewer">
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="card-title mb-0">Data Structure</h6>
                            </div>
                            <div class="card-body">
                                ${this.renderStructureStats(stats.structure)}
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="card-title mb-0">Content Analysis</h6>
                            </div>
                            <div class="card-body">
                                ${this.renderContentStats(stats.content)}
                            </div>
                        </div>
                    </div>
                </div>
                
                ${stats.fields ? `
                    <div class="card mt-3">
                        <div class="card-header">
                            <h6 class="card-title mb-0">Field Analysis</h6>
                        </div>
                        <div class="card-body">
                            ${this.renderFieldStats(stats.fields)}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    /**
     * Render chart view
     */
    renderChartView() {
        const data = this.currentResponse.data;
        const availableCharts = this.detectAvailableChartTypes(data);
        
        return `
            <div class="chart-viewer">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <div>
                        <small class="text-muted">Chart Type:</small>
                        <div class="btn-group btn-group-sm ms-2" role="group">
                            ${availableCharts.map(type => `
                                <input type="radio" class="btn-check" name="chartType" id="chart${type}" value="${type}" ${type === this.chartType ? 'checked' : ''}>
                                <label class="btn btn-outline-secondary" for="chart${type}">
                                    ${this.getChartIcon(type)} ${this.capitalize(type)}
                                </label>
                            `).join('')}
                        </div>
                    </div>
                    <button class="btn btn-outline-secondary btn-sm" onclick="window.responseDisplayBlock.exportChart()">
                        <i class="bi bi-download me-1"></i>Export
                    </button>
                </div>
                
                <div class="chart-container" style="position: relative; height: 400px; width: 100%;">
                    <div id="responseChart" style="width: 100%; height: 400px;"></div>
                </div>
                
                <div class="chart-info mt-2">
                    <small class="text-muted">
                        <i class="bi bi-info-circle me-1"></i>
                        Data points: ${this.getDataPointCount(data)} | 
                        Chart type: ${this.capitalize(this.chartType)}
                    </small>
                </div>
            </div>
        `;
    }
    
    /**
     * Format JSON with syntax highlighting
     */
    formatJSON(data) {
        if (data === undefined || data === null) {
            return '<span class="json-null">null</span>';
        }
        
        try {
            return JSON.stringify(data, null, 2)
                .replace(/(".*?"):/g, '<span class="json-key">$1</span>:')
                .replace(/: (".*?")/g, ': <span class="json-string">$1</span>')
                .replace(/: (true|false)/g, ': <span class="json-boolean">$1</span>')
                .replace(/: (null)/g, ': <span class="json-null">$1</span>')
                .replace(/: (\d+\.?\d*)/g, ': <span class="json-number">$1</span>');
        } catch (error) {
            console.error('Error formatting JSON:', error);
            return `<span class="text-danger">Error formatting data: ${error.message}</span>`;
        }
    }
    

    
    /**
     * Format cell value for table display
     */
    formatCellValue(value) {
        if (value === null || value === undefined) {
            return '<span class="text-muted">null</span>';
        }
        if (typeof value === 'object') {
            return `<code>${JSON.stringify(value)}</code>`;
        }
        return String(value);
    }
    
    /**
     * Generate data statistics
     */
    generateDataStats(data) {
        const stats = {
            structure: this.analyzeStructure(data),
            content: this.analyzeContent(data)
        };
        
        if (Array.isArray(data) && data.length > 0 && typeof data[0] === 'object') {
            stats.fields = this.analyzeFields(data);
        }
        
        return stats;
    }
    
    /**
     * Analyze data structure
     */
    analyzeStructure(data) {
        return {
            type: Array.isArray(data) ? 'array' : typeof data,
            length: Array.isArray(data) ? data.length : (typeof data === 'string' ? data.length : null),
            keys: typeof data === 'object' && !Array.isArray(data) ? Object.keys(data).length : null,
            depth: this.calculateDepth(data)
        };
    }
    
    /**
     * Analyze content
     */
    analyzeContent(data) {
        const serialized = JSON.stringify(data);
        return {
            size: new Blob([serialized]).size,
            characters: serialized.length
        };
    }
    
    /**
     * Analyze fields (for array of objects)
     */
    analyzeFields(data) {
        const fieldStats = {};
        const allKeys = new Set();
        
        data.forEach(item => {
            Object.keys(item).forEach(key => allKeys.add(key));
        });
        
        allKeys.forEach(key => {
            const values = data.map(item => item[key]).filter(v => v !== null && v !== undefined);
            const types = [...new Set(values.map(v => typeof v))];
            
            fieldStats[key] = {
                present: values.length,
                missing: data.length - values.length,
                types: types,
                unique: new Set(values).size
            };
        });
        
        return fieldStats;
    }
    
    /**
     * Calculate data depth
     */
    calculateDepth(obj, currentDepth = 0) {
        if (typeof obj !== 'object' || obj === null) {
            return currentDepth;
        }
        
        let maxDepth = currentDepth;
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                const depth = this.calculateDepth(obj[key], currentDepth + 1);
                maxDepth = Math.max(maxDepth, depth);
            }
        }
        
        return maxDepth;
    }
    
    /**
     * Render structure statistics
     */
    renderStructureStats(stats) {
        return `
            <dl class="row mb-0">
                <dt class="col-sm-4">Type:</dt>
                <dd class="col-sm-8"><span class="badge bg-primary">${stats.type}</span></dd>
                
                ${stats.length !== null ? `
                    <dt class="col-sm-4">Length:</dt>
                    <dd class="col-sm-8">${stats.length}</dd>
                ` : ''}
                
                ${stats.keys !== null ? `
                    <dt class="col-sm-4">Keys:</dt>
                    <dd class="col-sm-8">${stats.keys}</dd>
                ` : ''}
                
                <dt class="col-sm-4">Depth:</dt>
                <dd class="col-sm-8">${stats.depth}</dd>
            </dl>
        `;
    }
    
    /**
     * Render content statistics
     */
    renderContentStats(stats) {
        return `
            <dl class="row mb-0">
                <dt class="col-sm-4">Size:</dt>
                <dd class="col-sm-8">${this.formatBytes(stats.size)}</dd>
                
                <dt class="col-sm-4">Characters:</dt>
                <dd class="col-sm-8">${stats.characters.toLocaleString()}</dd>
            </dl>
        `;
    }
    
    /**
     * Render field statistics
     */
    renderFieldStats(fieldStats) {
        return `
            <div class="table-responsive" style="max-height: 300px; overflow-y: auto;">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Field</th>
                            <th>Present</th>
                            <th>Missing</th>
                            <th>Types</th>
                            <th>Unique</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Object.entries(fieldStats).map(([field, stats]) => `
                            <tr>
                                <td><code>${field}</code></td>
                                <td>${stats.present}</td>
                                <td>${stats.missing}</td>
                                <td>${stats.types.map(type => `<span class="badge bg-secondary me-1">${type}</span>`).join('')}</td>
                                <td>${stats.unique}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
    
    /**
     * Format bytes for display
     */
    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    /**
     * Copy JSON to clipboard
     */
    copyToClipboard() {
        if (this.currentResponse) {
            navigator.clipboard.writeText(JSON.stringify(this.currentResponse.data, null, 2))
                .then(() => {
                    console.log('JSON copied to clipboard');
                    // Show temporary feedback
                    const button = this.getContainer().querySelector('.btn-outline-secondary');
                    if (button) {
                        const originalText = button.innerHTML;
                        button.innerHTML = '<i class="bi bi-check me-1"></i>Copied!';
                        setTimeout(() => {
                            button.innerHTML = originalText;
                        }, 2000);
                    }
                })
                .catch(err => console.error('Failed to copy to clipboard:', err));
        }
    }
    
    /**
     * Export table data as CSV
     */
    exportTable() {
        if (!this.currentResponse) {
            console.warn('No response data to export');
            return;
        }
        
        const responseData = this.currentResponse.data;
        let data, headers;
        
        // Handle TableData structure
        if (responseData && typeof responseData === 'object' && responseData.columns && responseData.data) {
            data = responseData.data;
            // Extract column headers from TableData structure
            headers = [];
            responseData.columns.forEach(group => {
                group.columns.forEach(col => {
                    headers.push(col.title || col.field);
                });
            });
        }
        // Handle array data
        else if (Array.isArray(responseData)) {
            data = responseData;
            if (data.length === 0) {
                console.warn('Empty data array');
                return;
            }
            headers = Object.keys(data[0]);
        }
        else {
            console.warn('No exportable table data found');
            return;
        }
        
        if (!data || data.length === 0) {
            console.warn('No data to export');
            return;
        }
        
        // Convert to CSV
        const csvContent = [
            headers.join(','),
            ...data.map(row => 
                headers.map((header, index) => {
                    // For TableData, row is an array; for array data, row is an object
                    const value = Array.isArray(row) ? row[index] : row[header];
                    // Escape commas and quotes
                    if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                        return `"${value.replace(/"/g, '""')}"`;
                    }
                    return value;
                }).join(',')
            )
        ].join('\n');
        
        // Create download
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'api-response-data.csv';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        console.log('CSV export completed');
    }
    
    /**
     * Detect available chart types based on data structure
     */
    detectAvailableChartTypes(data) {
        const available = ['json']; // Always available
        
        // Handle TableData structure
        if (data && typeof data === 'object' && data.columns && data.data) {
            available.push('table'); // TableData always supports table view
            
            // Check if TableData contains numeric columns for charts
            const hasNumericColumns = data.columns.some(group => 
                group.columns.some(col => 
                    col.format === 'number' || 
                    col.field?.includes('point') ||
                    col.field?.includes('score') ||
                    col.field?.includes('average')
                )
            );
            
            if (hasNumericColumns && data.data.length > 0) {
                available.push('bar', 'line');
                
                // Check for time series indicators
                const hasTimeField = data.columns.some(group =>
                    group.columns.some(col =>
                        col.field?.toLowerCase().includes('week') ||
                        col.field?.toLowerCase().includes('date') ||
                        col.field?.toLowerCase().includes('season')
                    )
                );
                
                if (hasTimeField) {
                    available.push('area');
                }
            }
            
            return available;
        }
        
        // Check for team points format (object with data property containing team arrays)
        if (typeof data === 'object' && !Array.isArray(data) && data.data) {
            const teamData = data.data;
            if (typeof teamData === 'object' && Object.keys(teamData).length > 0) {
                const firstTeamData = Object.values(teamData)[0];
                if (Array.isArray(firstTeamData) && firstTeamData.length > 0) {
                    // This is team points/positions data - perfect for line charts and scatter plots
                    available.push('line', 'area', 'scatter');
                    return available;
                }
            }
        }
        
        if (Array.isArray(data) && data.length > 0) {
            available.push('table');
            
            // Check if data is suitable for charts
            const firstItem = data[0];
            if (typeof firstItem === 'object') {
                const keys = Object.keys(firstItem);
                const numericKeys = keys.filter(key => typeof firstItem[key] === 'number');
                
                if (numericKeys.length >= 1) {
                    available.push('bar', 'line');
                    
                    if (numericKeys.length >= 2) {
                        available.push('scatter');
                    }
                    
                    // Check for time series data
                    const hasTimeField = keys.some(key => 
                        key.toLowerCase().includes('week') || 
                        key.toLowerCase().includes('date') || 
                        key.toLowerCase().includes('time') ||
                        key.toLowerCase().includes('season')
                    );
                    
                    if (hasTimeField) {
                        available.push('area');
                    }
                }
            }
        }
        
        return available;
    }
    
    /**
     * Get chart icon for button
     */
    getChartIcon(type) {
        const icons = {
            line: '<i class="bi bi-graph-up me-1"></i>',
            bar: '<i class="bi bi-bar-chart me-1"></i>',
            scatter: '<i class="bi bi-scatter-chart me-1"></i>',
            area: '<i class="bi bi-area-chart me-1"></i>',
            radar: '<i class="bi bi-diagram-3 me-1"></i>',
            histogram: '<i class="bi bi-bar-chart-steps me-1"></i>',
            table: '<i class="bi bi-table me-1"></i>',
            json: '<i class="bi bi-code me-1"></i>'
        };
        return icons[type] || '<i class="bi bi-graph-up me-1"></i>';
    }
    
    /**
     * Capitalize string
     */
    capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    
    /**
     * Get data point count
     */
    getDataPointCount(data) {
        if (Array.isArray(data)) {
            return data.length;
        } else if (typeof data === 'object' && data !== null) {
            return Object.keys(data).length;
        }
        return 1;
    }
    
    /**
     * Render chart using existing ECharts functions
     */
    async renderChart() {
        // Wait for container to be available
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const container = document.getElementById('responseChart');
        if (!container) {
            console.warn('Chart container not found');
            return;
        }
        
        const data = this.currentResponse.data;
        const chartData = this.prepareChartData(data, this.chartType);
        
        if (!chartData) {
            console.warn('Could not prepare chart data');
            return;
        }
        
        try {
            // Use existing chart functions based on chart type
            switch (this.chartType) {
                case 'line':
                    createLineChart(chartData.data, chartData.order, 'responseChart', 'API Response Data', chartData.labels);
                    break;
                case 'bar':
                    createHorizontalBarChart(chartData.values, 'responseChart', 'API Response Data', chartData.labels);
                    break;
                case 'scatter':
                    if (chartData.isTeamPointsFormat) {
                        // Use multi-axis scatter chart for team points data (like "Points per Match Day")
                        createScatterChartMultiAxis(chartData.data, chartData.order, 'responseChart', 'Points per Match Day', chartData.labels);
                    } else {
                        // Use vanilla scatter chart for regular array data
                        createScatterChart_vanilla(chartData.scatterData, 'responseChart', 'API Response Data', chartData.axisLabels);
                    }
                    break;
                case 'area':
                    // Use line chart with area fill for now
                    createLineChart(chartData.data, chartData.order, 'responseChart', 'API Response Data', chartData.labels);
                    break;
                default:
                    createLineChart(chartData.data, chartData.order, 'responseChart', 'API Response Data', chartData.labels);
            }
        } catch (error) {
            console.error('Error creating chart:', error);
        }
    }
    
    /**
     * Prepare chart data for existing ECharts functions
     */
    prepareChartData(data, chartType) {
        // Handle team points format first (this takes priority)
        if (typeof data === 'object' && !Array.isArray(data) && data && data.data) {
            switch (chartType) {
                case 'scatter':
                    return this.prepareTeamPointsScatterData(data);
                case 'line':
                case 'area':
                default:
                    return this.prepareLineChartData(data, null, []);
            }
        }
        
        if (!Array.isArray(data) || data.length === 0) {
            return null;
        }
        
        const firstItem = data[0];
        if (typeof firstItem !== 'object') {
            return null;
        }
        
        const keys = Object.keys(firstItem);
        const numericKeys = keys.filter(key => typeof firstItem[key] === 'number');
        const labelKey = keys.find(key => 
            typeof firstItem[key] === 'string' || 
            key.toLowerCase().includes('team') ||
            key.toLowerCase().includes('name')
        ) || keys[0];
        
        const labels = data.map(item => item[labelKey]);
        
        switch (chartType) {
            case 'bar':
                return this.prepareBarChartData(data, labels, numericKeys);
            case 'line':
                return this.prepareLineChartData(data, labels, numericKeys);
            case 'scatter':
                return this.prepareScatterChartData(data, numericKeys);
            case 'area':
                return this.prepareLineChartData(data, labels, numericKeys); // Same as line for now
            default:
                return this.prepareLineChartData(data, labels, numericKeys);
        }
    }
    
    /**
     * Generate table configuration for existing createTable function
     */
    generateTableConfig(data) {
        if (!Array.isArray(data) || data.length === 0) {
            return null;
        }
        
        const firstItem = data[0];
        const keys = Object.keys(firstItem);
        
        // Create columns configuration
        const columns = keys.map(key => ({
            title: key,
            field: key
        }));
        
        // Convert data to row format expected by createTable
        const tableData = data.map(item => keys.map(key => item[key]));
        
        return {
            data: tableData,
            columns: columns,
            headerGroups: [{
                title: 'API Response Data',
                colspan: keys.length
            }]
        };
    }
    
    /**
     * Prepare bar chart data for createHorizontalBarChart
     */
    prepareBarChartData(data, labels, numericKeys) {
        if (numericKeys.length === 0) return null;
        
        // Use first numeric key for bar chart
        const values = data.map(item => item[numericKeys[0]]);
        
        return {
            values: values,
            labels: labels,
            title: `${numericKeys[0]} by ${labels[0] ? 'Category' : 'Item'}`
        };
    }
    
    /**
     * Prepare line chart data for createLineChart
     */
    prepareLineChartData(data, labels, numericKeys) {
        // Handle team points format (object with team names as keys and arrays as values)
        if (typeof data === 'object' && !Array.isArray(data) && data && data.data) {
            // This is team points data format: { data: { "Team1": [1,2,3], "Team2": [4,5,6] }, sorted_by_total: [...] }
            const teamData = data.data || data.data_accumulated || {};
            const teamOrder = data.sorted_by_total || Object.keys(teamData);
            
            // Generate labels for weeks if not provided
            const numWeeks = Object.values(teamData)[0]?.length || 0;
            const weekLabels = labels || Array.from({length: numWeeks}, (_, i) => `Week ${i + 1}`);
            
            return {
                data: teamData,
                order: teamOrder,
                labels: weekLabels
            };
        }
        
        // Handle array format (original logic)
        if (!Array.isArray(data) || numericKeys.length === 0) {
            return null;
        }
        
        // Create data object in format expected by createLineChart
        const chartData = {};
        const order = [];
        
        // Group by label (team/category) and create series for each numeric key
        numericKeys.slice(0, 3).forEach(key => {
            chartData[key] = data.map(item => item[key]);
            order.push(key);
        });
        
        return {
            data: chartData,
            order: order,
            labels: labels
        };
    }
    
    /**
     * Prepare scatter chart data for createScatterChart_vanilla
     */
    prepareScatterChartData(data, numericKeys) {
        if (numericKeys.length < 2) return null;
        
        const xKey = numericKeys[0];
        const yKey = numericKeys[1];
        
        // Format data for createScatterChart_vanilla
        const scatterData = data.map(item => [item[xKey], item[yKey]]);
        
        return {
            scatterData: scatterData,
            axisLabels: [xKey, yKey],
            title: `${yKey} vs ${xKey}`,
            isTeamPointsFormat: false
        };
    }
    
    /**
     * Prepare team points scatter chart data for createScatterChartMultiAxis
     */
    prepareTeamPointsScatterData(data) {
        if (!data || !data.data) return null;
        
        const teamData = data.data;
        const teamOrder = data.sorted_by_total || Object.keys(teamData);
        
        // Generate labels for weeks
        const numWeeks = Object.values(teamData)[0]?.length || 0;
        const weekLabels = Array.from({length: numWeeks}, (_, i) => `Week ${i + 1}`);
        
        return {
            data: teamData,
            order: teamOrder,
            labels: weekLabels,
            isTeamPointsFormat: true
        };
    }
    
    /**
     * Export chart as image (for ECharts)
     */
    exportChart() {
        const container = document.getElementById('responseChart');
        if (!container) {
            console.warn('No chart container found');
            return;
        }
        
        // Get ECharts instance
        const chartInstance = echarts.getInstanceByDom(container);
        if (!chartInstance) {
            console.warn('No chart instance found');
            return;
        }
        
        // Export as image using ECharts built-in functionality
        const url = chartInstance.getDataURL({
            type: 'png',
            pixelRatio: 2,
            backgroundColor: '#fff'
        });
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `api-response-chart-${Date.now()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        console.log('Chart exported as image');
    }
}