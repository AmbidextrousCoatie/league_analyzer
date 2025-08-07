/**
 * Base Content Block
 * 
 * Abstract base class for all content blocks
 * Provides common functionality for data fetching, rendering, and lifecycle management
 */

class BaseContentBlock {
    constructor(config) {
        // Required configuration
        this.id = config.id;
        this.containerId = config.containerId;
        
        // API configuration
        this.dataEndpoint = config.dataEndpoint;
        this.requiredFilters = config.requiredFilters || [];
        this.optionalFilters = config.optionalFilters || [];
        
        // Display configuration
        this.title = config.title || '';
        this.description = config.description || '';
        
        // State management
        this.isRendering = false;
        this.lastRenderedState = {};
        this.lastData = null;
        
        // Error handling
        this.retryCount = 0;
        this.maxRetries = 3;
    }
    
    /**
     * Check if this block can render with the given filter state
     */
    canRender(filterState) {
        return this.requiredFilters.every(filter => 
            filterState[filter] && filterState[filter] !== ''
        );
    }
    
    /**
     * Build API parameters from filter state
     */
    buildParams(filterState) {
        const params = new URLSearchParams();
        
        // Add required filters
        this.requiredFilters.forEach(filter => {
            if (filterState[filter]) {
                params.set(this.getParamName(filter), filterState[filter]);
            }
        });
        
        // Add optional filters
        this.optionalFilters.forEach(filter => {
            if (filterState[filter] && filterState[filter] !== '') {
                params.set(this.getParamName(filter), filterState[filter]);
            }
        });
        
        return params.toString();
    }
    
    /**
     * Map filter names to API parameter names
     */
    getParamName(filterName) {
        const mapping = {
            'team': 'team_name',
            'season': 'season',
            'week': 'week',
            'league': 'league_name'
        };
        return mapping[filterName] || filterName;
    }
    
    /**
     * Fetch data from API
     */
    async fetchData(filterState) {
        if (!this.dataEndpoint) {
            throw new Error(`No data endpoint configured for block ${this.id}`);
        }
        
        const params = this.buildParams(filterState);
        const url = `${this.dataEndpoint}?${params}`;
        
        console.log(`${this.id}: Fetching data from ${url}`);
        
        try {
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            // Check for API error responses
            if (data.error) {
                throw new Error(`API Error: ${data.error}`);
            }
            
            this.lastData = data;
            this.retryCount = 0; // Reset retry count on success
            
            return data;
            
        } catch (error) {
            console.error(`${this.id}: Error fetching data:`, error);
            
            // Implement retry logic
            if (this.retryCount < this.maxRetries) {
                this.retryCount++;
                console.log(`${this.id}: Retrying... (${this.retryCount}/${this.maxRetries})`);
                
                // Wait before retry (exponential backoff)
                await new Promise(resolve => setTimeout(resolve, 1000 * this.retryCount));
                return this.fetchData(filterState);
            }
            
            throw error;
        }
    }
    
    /**
     * Render the content block
     * This method should be overridden by subclasses
     */
    async render(filterState) {
        throw new Error(`render() method must be implemented by ${this.constructor.name}`);
    }
    
    /**
     * Main rendering pipeline
     */
    async renderWithData(filterState) {
        // Check if already rendering
        if (this.isRendering) {
            console.log(`${this.id}: Already rendering, skipping...`);
            return;
        }
        
        // Check if state actually changed
        if (JSON.stringify(filterState) === JSON.stringify(this.lastRenderedState)) {
            console.log(`${this.id}: State unchanged, skipping render`);
            return;
        }
        
        // Check if we can render with this state
        if (!this.canRender(filterState)) {
            console.log(`${this.id}: Cannot render with current state:`, filterState);
            this.showPlaceholder();
            return;
        }
        
        this.isRendering = true;
        this.lastRenderedState = { ...filterState };
        
        try {
            // Show loading state
            this.showLoading();
            
            // Fetch data
            const data = await this.fetchData(filterState);
            
            // Render with data
            await this.render(data, filterState);
            
            console.log(`${this.id}: Rendered successfully`);
            
        } catch (error) {
            console.error(`${this.id}: Render error:`, error);
            this.showError(error);
        } finally {
            this.isRendering = false;
        }
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = `
                <div class="d-flex justify-content-center align-items-center" style="min-height: 200px;">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span class="ms-2">Loading ${this.title}...</span>
                </div>
            `;
        }
    }
    
    /**
     * Show placeholder when cannot render
     */
    showPlaceholder() {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="fas fa-info-circle fa-2x mb-2"></i>
                    <p>Select ${this.requiredFilters.join(', ')} to view ${this.title}</p>
                </div>
            `;
        }
    }
    
    /**
     * Show error state
     */
    showError(error) {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = `
                <div class="alert alert-warning" role="alert">
                    <h6 class="alert-heading">Unable to load ${this.title}</h6>
                    <p class="mb-0">${error.message}</p>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="this.closest('.alert').parentElement.innerHTML=''">
                        Dismiss
                    </button>
                </div>
            `;
        }
    }
    
    /**
     * Clear the content area
     */
    clear() {
        // Clean up any orphaned Chart.js instances first
        this.clearOrphanedCharts();
        
        const container = document.getElementById(this.containerId);
        if (container) {
            container.innerHTML = '';
        }
        
        this.lastRenderedState = {};
        this.lastData = null;
    }
    
    /**
     * Helper method to clean up orphaned Chart.js instances
     */
    clearOrphanedCharts() {
        const container = this.getContainer();
        if (!container) return;
        
        let canvas = container.querySelector('canvas');
        if (!canvas && container.tagName === 'CANVAS') {
            canvas = container;
        }
        
        if (canvas && typeof Chart !== 'undefined') {
            // Find and destroy any Chart.js instance attached to this canvas
            if (Chart.instances) {
                Object.values(Chart.instances).forEach(chartInstance => {
                    if (chartInstance && chartInstance.canvas === canvas) {
                        try {
                            console.log(`${this.id}: Clearing orphaned chart instance`);
                            chartInstance.destroy();
                        } catch (error) {
                            console.warn(`${this.id}: Error clearing orphaned chart:`, error);
                        }
                    }
                });
            }
            
            // Also check canvas context
            const ctx = canvas.getContext('2d');
            if (ctx && ctx.chart) {
                try {
                    console.log(`${this.id}: Clearing chart from canvas context`);
                    ctx.chart.destroy();
                } catch (error) {
                    console.warn(`${this.id}: Error clearing chart from context:`, error);
                }
            }
        }
    }
    
    /**
     * Destroy the content block and clean up resources
     */
    destroy() {
        this.clear();
        
        // Clean up any event listeners or resources
        this.cleanup();
    }
    
    /**
     * Cleanup method for subclasses to override
     */
    cleanup() {
        // Override in subclasses if needed
    }
    
    /**
     * Get the container element
     */
    getContainer() {
        return document.getElementById(this.containerId);
    }
    
    /**
     * Helper to check if container exists
     */
    hasContainer() {
        return !!this.getContainer();
    }
    
    /**
     * Debug information
     */
    debug() {
        return {
            id: this.id,
            containerId: this.containerId,
            dataEndpoint: this.dataEndpoint,
            requiredFilters: this.requiredFilters,
            optionalFilters: this.optionalFilters,
            isRendering: this.isRendering,
            lastRenderedState: this.lastRenderedState,
            hasContainer: this.hasContainer(),
            retryCount: this.retryCount
        };
    }
}

// Make BaseContentBlock globally available
window.BaseContentBlock = BaseContentBlock;