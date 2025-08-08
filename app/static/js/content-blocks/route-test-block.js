/**
 * Route Test Content Block
 * 
 * Handles testing of API routes with dynamic parameter injection
 * Shows request/response details in a structured format
 */

class RouteTestBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'route-test',
            containerId: 'routeTestContainer',
            title: 'API Route Testing',
            description: 'Test API endpoints with current filter state'
        });
        
        // Track test results
        this.testResults = new Map();
        this.isTestingAll = false;
    }
    
    /**
     * Can always render - doesn't require specific filters
     */
    canRender(filterState) {
        return true;
    }
    
    /**
     * Render the route testing interface
     */
    async render(data, filterState) {
        const container = this.getContainer();
        if (!container) {
            throw new Error('Route test container not found');
        }
        
        // Create route testing interface
        container.innerHTML = this.createRouteTestingInterface(filterState);
        
        // Attach event listeners
        this.attachEventListeners(filterState);
        
        console.log(`${this.id}: Route testing interface rendered`);
    }
    
    /**
     * Create the route testing interface HTML
     */
    createRouteTestingInterface(filterState) {
        const routes = this.getAPIRoutes();
        
        return `
            <div class="route-test-block">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5>API Route Testing</h5>
                    <div>
                        <button class="btn btn-primary btn-sm" onclick="window.testAllRoutes()" id="testAllBtn">
                            Test All Routes
                        </button>
                        <button class="btn btn-outline-secondary btn-sm" onclick="window.clearResults()" id="clearBtn">
                            Clear Results
                        </button>
                    </div>
                </div>
                
                <div class="current-filters mb-3">
                    <small class="text-muted">Current Filters:</small>
                    <div class="filter-display">
                        ${this.renderCurrentFilters(filterState)}
                    </div>
                </div>
                
                <div class="accordion" id="routeAccordion">
                    ${routes.map((category, idx) => this.renderRouteCategory(category, idx, filterState)).join('')}
                </div>
            </div>
        `;
    }
    
    /**
     * Render current filter state
     */
    renderCurrentFilters(filterState) {
        const filters = ['database', 'season', 'league', 'week', 'team'];
        return filters
            .filter(filter => filterState[filter])
            .map(filter => `
                <span class="badge bg-secondary me-1">
                    ${filter}: ${filterState[filter]}
                </span>
            `).join('');
    }
    
    /**
     * Render a category of routes
     */
    renderRouteCategory(category, categoryIndex, filterState) {
        return `
            <div class="accordion-item">
                <h2 class="accordion-header" id="heading${categoryIndex}">
                    <button class="accordion-button ${categoryIndex === 0 ? '' : 'collapsed'}" 
                            type="button" data-bs-toggle="collapse" 
                            data-bs-target="#collapse${categoryIndex}" 
                            aria-expanded="${categoryIndex === 0 ? 'true' : 'false'}" 
                            aria-controls="collapse${categoryIndex}">
                        <i class="bi bi-api me-2"></i>
                        ${category.name} Routes
                        <span class="badge bg-primary ms-2">${category.routes.length}</span>
                    </button>
                </h2>
                <div id="collapse${categoryIndex}" 
                     class="accordion-collapse collapse ${categoryIndex === 0 ? 'show' : ''}" 
                     aria-labelledby="heading${categoryIndex}" 
                     data-bs-parent="#routeAccordion">
                    <div class="accordion-body">
                        <div class="mb-2">
                            <button class="btn btn-outline-primary btn-sm" 
                                    onclick="window.testCategoryRoutes('${category.id}')">
                                Test All ${category.name} Routes
                            </button>
                        </div>
                        ${category.routes.map((route, routeIdx) => this.renderRoute(route, `${categoryIndex}-${routeIdx}`, filterState)).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Render individual route
     */
    renderRoute(route, routeId, filterState) {
        const testResult = this.testResults.get(route.endpoint);
        const statusClass = testResult ? (testResult.success ? 'success' : 'danger') : 'secondary';
        const statusIcon = testResult ? (testResult.success ? 'check-circle' : 'x-circle') : 'circle';
        
        return `
            <div class="route-item border rounded p-3 mb-2">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="route-info flex-grow-1">
                        <div class="d-flex align-items-center mb-1">
                            <span class="badge bg-${this.getMethodColor(route.method)} me-2">${route.method}</span>
                            <code class="route-endpoint">${route.endpoint}</code>
                            <i class="bi bi-${statusIcon} text-${statusClass} ms-2"></i>
                        </div>
                        <small class="text-muted">${route.description}</small>
                        ${route.requiredParams ? `
                            <div class="mt-1">
                                <small class="text-warning">
                                    <i class="bi bi-exclamation-triangle me-1"></i>
                                    Requires: ${route.requiredParams.join(', ')}
                                </small>
                            </div>
                        ` : ''}
                        ${route.visualizations ? `
                            <div class="mt-1">
                                <small class="text-info">
                                    <i class="bi bi-graph-up me-1"></i>
                                    Visualizations: ${route.visualizations.join(', ')}
                                </small>
                            </div>
                        ` : ''}
                    </div>
                    <button class="btn btn-outline-primary btn-sm" 
                            onclick="window.testRoute('${route.endpoint}', '${route.method}', ${JSON.stringify(route.requiredParams || []).replace(/"/g, '&quot;')}, ${JSON.stringify(route.paramMapping || {}).replace(/"/g, '&quot;')})"
                            ${this.canTestRoute(route, filterState) ? '' : 'disabled'}>
                        <i class="bi bi-play-circle me-1"></i>Test
                    </button>
                </div>
                
                <div class="route-result mt-2" id="result-${routeId}" style="display: none;">
                    <!-- Test results will be inserted here -->
                </div>
            </div>
        `;
    }
    
    /**
     * Get color for HTTP method badge
     */
    getMethodColor(method) {
        const colors = {
            'GET': 'primary',
            'POST': 'success',
            'PUT': 'warning',
            'DELETE': 'danger',
            'PATCH': 'info'
        };
        return colors[method] || 'secondary';
    }
    
    /**
     * Check if route can be tested with current filters
     */
    canTestRoute(route, filterState) {
        if (!route.requiredParams) return true;
        
        return route.requiredParams.every(param => 
            filterState[param] && filterState[param] !== ''
        );
    }
    
    /**
     * Get API routes configuration
     */
    getAPIRoutes() {
        return [
            {
                id: 'league',
                name: 'League',
                routes: [
                    {
                        endpoint: '/league/get_available_seasons',
                        method: 'GET',
                        description: 'Get all available seasons'
                    },
                    {
                        endpoint: '/league/get_available_leagues',
                        method: 'GET',
                        description: 'Get all available leagues'
                    },
                    {
                        endpoint: '/league/get_available_weeks',
                        method: 'GET', 
                        description: 'Get available weeks for season/league',
                        requiredParams: ['season', 'league']
                    },
                    {
                        endpoint: '/league/get_league_history',
                        method: 'GET',
                        description: 'Get league season history/overview',
                        requiredParams: ['season', 'league'],
                        visualizations: ['table', 'json']
                    },
                    {
                        endpoint: '/league/get_league_week_table',
                        method: 'GET',
                        description: 'Get league standings for specific week',
                        requiredParams: ['season', 'league', 'week'],
                        visualizations: ['table', 'json']
                    },
                    {
                        endpoint: '/league/get_honor_scores',
                        method: 'GET',
                        description: 'Get honor scores for league week',
                        requiredParams: ['season', 'league', 'week']
                    },
                    {
                        endpoint: '/league/get_team_points',
                        method: 'GET',
                        description: 'Get team points data',
                        requiredParams: ['season', 'league'],
                        visualizations: ['line', 'scatter', 'table', 'json']
                    },
                    {
                        endpoint: '/league/get_team_positions',
                        method: 'GET',
                        description: 'Get team positions over time',
                        requiredParams: ['season', 'league'],
                        visualizations: ['line', 'area', 'table', 'json']
                    },
                    {
                        endpoint: '/league/get_team_averages',
                        method: 'GET',
                        description: 'Get team averages data',
                        requiredParams: ['season', 'league'],
                        visualizations: ['bar', 'table', 'json']
                    }
                ]
            },
            {
                id: 'team',
                name: 'Team',
                routes: [
                    {
                        endpoint: '/team/get_teams',
                        method: 'GET',
                        description: 'Get all teams for season/league',
                        requiredParams: ['season', 'league']
                    },
                    {
                        endpoint: '/team/get_team_history',
                        method: 'GET',
                        description: 'Get team position history',
                        requiredParams: ['team'],
                        paramMapping: { 'team': 'team_name' },
                        visualizations: ['line', 'scatter', 'table', 'json']
                    },
                    {
                        endpoint: '/team/get_league_comparison',
                        method: 'GET',
                        description: 'Compare team vs league averages',
                        requiredParams: ['team'],
                        paramMapping: { 'team': 'team_name' },
                        visualizations: ['bar', 'radar', 'table', 'json']
                    },
                    {
                        endpoint: '/team/get_clutch_analysis',
                        method: 'GET',
                        description: 'Get clutch performance data',
                        requiredParams: ['team'],
                        paramMapping: { 'team': 'team_name' },
                        visualizations: ['scatter', 'bar', 'table', 'json']
                    },
                    {
                        endpoint: '/team/get_consistency_metrics',
                        method: 'GET',
                        description: 'Get team consistency metrics',
                        requiredParams: ['team'],
                        paramMapping: { 'team': 'team_name' },
                        visualizations: ['line', 'bar', 'table', 'json']
                    },
                    {
                        endpoint: '/team/get_special_matches',
                        method: 'GET',
                        description: 'Get special team matches (highest/lowest scores)',
                        requiredParams: ['team'],
                        paramMapping: { 'team': 'team_name' },
                        visualizations: ['table', 'bar', 'json']
                    },
                    {
                        endpoint: '/team/get_margin_analysis',
                        method: 'GET',
                        description: 'Get team margin analysis',
                        requiredParams: ['team'],
                        paramMapping: { 'team': 'team_name' },
                        visualizations: ['scatter', 'histogram', 'table', 'json']
                    }
                ]
            },
            {
                id: 'player',
                name: 'Player',
                routes: [
                    {
                        endpoint: '/player/get_players',
                        method: 'GET',
                        description: 'Get all players for team/season',
                        requiredParams: ['season', 'league', 'team']
                    },
                    {
                        endpoint: '/player/get_player_stats',
                        method: 'GET',
                        description: 'Get player statistics',
                        requiredParams: ['player']
                    }
                ]
            }
        ];
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners(filterState) {
        const container = this.getContainer();
        
        // Attach to window for global access
        window.routeTestBlock = this;
        
        // Make methods available globally for onclick handlers
        window.testRoute = this.testRoute.bind(this);
        window.testAllRoutes = this.testAllRoutes.bind(this);
        window.testCategoryRoutes = this.testCategoryRoutes.bind(this);
        window.clearResults = this.clearResults.bind(this);
    }
    
    /**
     * Test a specific route
     */
    async testRoute(endpoint, method, requiredParams = [], paramMapping = {}) {
        console.log(`Testing route: ${method} ${endpoint}`);
        
        try {
            // Build URL with current filter state
            const url = this.buildTestURL(endpoint, requiredParams, paramMapping);
            
            const startTime = performance.now();
            const response = await fetch(url, { method });
            const endTime = performance.now();
            
            let responseData;
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                responseData = await response.json();
            } else {
                // Handle non-JSON responses (HTML error pages, etc.)
                const textData = await response.text();
                responseData = {
                    error: 'Non-JSON response received',
                    content_type: contentType,
                    body: textData.substring(0, 500) + (textData.length > 500 ? '...' : '')
                };
            }
            
            const duration = Math.round(endTime - startTime);
            
            const result = {
                success: response.ok,
                status: response.status,
                statusText: response.statusText,
                duration,
                data: responseData,
                url: url
            };
            
            this.testResults.set(endpoint, result);
            this.displayTestResult(endpoint, result);
            
            // Dispatch event for other blocks to listen to
            document.dispatchEvent(new CustomEvent('routeTestComplete', {
                detail: { endpoint, result }
            }));
            
        } catch (error) {
            console.error(`Error testing ${endpoint}:`, error);
            
            const result = {
                success: false,
                error: error.message,
                url: endpoint
            };
            
            this.testResults.set(endpoint, result);
            this.displayTestResult(endpoint, result);
            
            // Dispatch event even for errors
            document.dispatchEvent(new CustomEvent('routeTestComplete', {
                detail: { endpoint, result }
            }));
        }
    }
    
    /**
     * Build test URL with parameters
     */
    buildTestURL(endpoint, requiredParams, paramMapping = {}) {
        const filterState = window.currentState || {};
        const params = new URLSearchParams();
        
        requiredParams.forEach(param => {
            if (filterState[param]) {
                // Use mapped parameter name if available, otherwise use original
                const actualParamName = paramMapping[param] || param;
                params.append(actualParamName, filterState[param]);
            }
        });
        
        return params.toString() ? `${endpoint}?${params.toString()}` : endpoint;
    }
    
    /**
     * Display test result
     */
    displayTestResult(endpoint, result) {
        // Find the route item and update its result display
        const routeItems = this.getContainer().querySelectorAll('.route-item');
        
        routeItems.forEach(item => {
            const codeElement = item.querySelector('.route-endpoint');
            if (codeElement && codeElement.textContent === endpoint) {
                const resultContainer = item.querySelector('.route-result');
                if (resultContainer) {
                    resultContainer.style.display = 'block';
                    resultContainer.innerHTML = this.formatTestResult(result);
                }
                
                // Update status icon
                const statusIcon = item.querySelector('.bi-circle, .bi-check-circle, .bi-x-circle');
                if (statusIcon) {
                    statusIcon.className = `bi bi-${result.success ? 'check-circle' : 'x-circle'} text-${result.success ? 'success' : 'danger'} ms-2`;
                }
            }
        });
    }
    
    /**
     * Format test result for display
     */
    formatTestResult(result) {
        if (!result.success) {
            return `
                <div class="alert alert-danger alert-sm">
                    <strong>Error:</strong> ${result.error || result.statusText || 'Unknown error'}
                    ${result.status ? `<br><small>Status: ${result.status}</small>` : ''}
                </div>
            `;
        }
        
        return `
            <div class="alert alert-success alert-sm">
                <div class="d-flex justify-content-between">
                    <strong>Success!</strong>
                    <small>${result.duration}ms</small>
                </div>
                <small>Status: ${result.status} ${result.statusText}</small>
            </div>
            <details class="mt-2">
                <summary class="text-muted" style="cursor: pointer;">View Response Data</summary>
                <pre class="mt-2 p-2 bg-light border rounded" style="max-height: 200px; overflow-y: auto; font-size: 0.8em;"><code>${JSON.stringify(result.data, null, 2)}</code></pre>
            </details>
        `;
    }
    
    /**
     * Test all routes
     */
    async testAllRoutes() {
        console.log('Testing all routes...');
        this.isTestingAll = true;
        
        const routes = this.getAPIRoutes();
        const allRoutes = routes.flatMap(category => category.routes);
        
        for (const route of allRoutes) {
            if (this.canTestRoute(route, window.currentState || {})) {
                await this.testRoute(route.endpoint, route.method, route.requiredParams || [], route.paramMapping || {});
                // Small delay between requests
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }
        
        this.isTestingAll = false;
        console.log('Finished testing all routes');
    }
    
    /**
     * Test all routes in a specific category
     */
    async testCategoryRoutes(categoryId) {
        console.log(`Testing ${categoryId} routes...`);
        
        const routes = this.getAPIRoutes();
        const category = routes.find(cat => cat.id === categoryId);
        
        if (!category) {
            console.error(`Category ${categoryId} not found`);
            return;
        }
        
        for (const route of category.routes) {
            if (this.canTestRoute(route, window.currentState || {})) {
                await this.testRoute(route.endpoint, route.method, route.requiredParams || [], route.paramMapping || {});
                // Small delay between requests
                await new Promise(resolve => setTimeout(resolve, 100));
            }
        }
        
        console.log(`Finished testing ${categoryId} routes`);
    }
    
    /**
     * Clear all test results
     */
    clearResults() {
        this.testResults.clear();
        
        // Clear result displays
        const resultContainers = this.getContainer().querySelectorAll('.route-result');
        resultContainers.forEach(container => {
            container.style.display = 'none';
            container.innerHTML = '';
        });
        
        // Reset status icons
        const statusIcons = this.getContainer().querySelectorAll('.bi-check-circle, .bi-x-circle');
        statusIcons.forEach(icon => {
            icon.className = 'bi bi-circle text-secondary ms-2';
        });
        
        console.log('Test results cleared');
    }
}