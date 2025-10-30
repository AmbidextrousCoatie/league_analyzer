/**
 * Consistency Metrics Content Block
 * 
 * Replaces the legacy updateConsistencyMetrics() function
 * Shows team performance consistency statistics and score ranges
 */

class ConsistencyMetricsBlock extends BaseContentBlock {
    constructor() {
        super({
            id: 'consistency-metrics',
            containerId: 'consistencyMetrics',
            dataEndpoint: '/team/get_consistency_metrics',
            requiredFilters: ['team'],
            optionalFilters: ['season'],
            title: 'Consistency Metrics',
            description: 'Team performance consistency and statistical analysis'
        });
        
        // Store translation keys for dynamic updates
        this.titleKey = 'block.consistency_metrics.title';
        this.descriptionKey = 'block.consistency_metrics.description';
        
        // Update with current translations
        this.updateTranslations();
    }
    
    /**
     * Render the consistency metrics
     */
    async render(data, filterState) {
        if (!data) {
            throw new Error('No consistency metrics data available');
        }
        
        console.log('ConsistencyMetricsBlock: Rendering consistency metrics with data:', data);
        
        // Render metrics
        this.renderMetrics(data);
        
        console.log(`${this.id}: Rendered metrics successfully`);
    }
    
    /**
     * Render the consistency metrics HTML
     */
    renderMetrics(data) {
        const container = this.getContainer();
        if (!container) {
            throw new Error('Metrics container not found');
        }
        
        const metricsHtml = `
            <div class="row">
                <div class="col-md-6">
                    <h6>${typeof t === 'function' ? t('ui.consistency.basic_stats', 'Basic Statistics') : 'Basic Statistics'}</h6>
                    <table class="table table-sm">
                        <tr><td>Average Score:</td><td><strong>${data.mean_score || 'N/A'}</strong></td></tr>
                        <tr><td>Standard Deviation:</td><td><strong>${data.std_deviation || 'N/A'}</strong></td></tr>
                        <tr><td>Coefficient of Variation:</td><td><strong>${data.coefficient_of_variation || 'N/A'}%</strong></td></tr>
                        <tr><td>Consistency Rating:</td><td><strong class="text-primary">${data.consistency_rating || 'N/A'}</strong></td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>${typeof t === 'function' ? t('ui.consistency.score_range', 'Score Range') : 'Score Range'}</h6>
                    <table class="table table-sm">
                        <tr><td>Highest Score:</td><td><strong class="text-success">${data.max_score || 'N/A'}</strong></td></tr>
                        <tr><td>Lowest Score:</td><td><strong class="text-danger">${data.min_score || 'N/A'}</strong></td></tr>
                        <tr><td>Score Range:</td><td><strong>${data.score_range || 'N/A'}</strong></td></tr>
                        <tr><td>Interquartile Range:</td><td><strong>${data.iqr || 'N/A'}</strong></td></tr>
                    </table>
                </div>
            </div>
        `;
        
        container.innerHTML = metricsHtml;
        console.log(`${this.id}: Metrics HTML rendered successfully`);
    }
    
    /**
     * Show loading state
     */
    showLoading() {
        const container = this.getContainer();
        if (container) {
            container.innerHTML = `
                <div class="d-flex justify-content-center align-items-center" style="min-height: 150px;">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span class="ms-2">${typeof t === 'function' ? t('status.loading', 'Loading consistency metrics...') : 'Loading consistency metrics...'}</span>
                </div>
            `;
        }
    }
    
    /**
     * Show placeholder when cannot render
     */
    showPlaceholder() {
        const container = this.getContainer();
        if (container) {
            container.innerHTML = `
                <div class="text-center text-muted p-4">
                    <i class="fas fa-chart-line fa-2x mb-2"></i>
                    <p>${typeof t === 'function' ? t('msg.please_select.team', 'Select a team to view consistency metrics') : 'Select a team to view consistency metrics'}</p>
                    <small>${typeof t === 'function' ? t('ui.consistency.description', 'Statistical analysis of team performance consistency') : 'Statistical analysis of team performance consistency'}</small>
                </div>
            `;
        }
    }
    
    /**
     * Show error state
     */
    showError(error) {
        const container = this.getContainer();
        if (container) {
            container.innerHTML = `
                <div class="alert alert-warning" role="alert">
                    <h6 class="alert-heading">${typeof t === 'function' ? t('error_loading_data', 'Unable to load consistency metrics') : 'Unable to load consistency metrics'}</h6>
                    <p class="mb-0">${error.message}</p>
                    <button class="btn btn-sm btn-outline-primary mt-2" onclick="this.closest('.alert').parentElement.innerHTML=''">
                        ${typeof t === 'function' ? t('action.dismiss', 'Dismiss') : 'Dismiss'}
                    </button>
                </div>
            `;
        }
    }
    
    /**
     * Clear the content area
     */
    clear() {
        const container = this.getContainer();
        if (container) {
            container.innerHTML = '';
        }
        
        this.lastRenderedState = {};
        this.lastData = null;
    }
    
    /**
     * Enhanced debug information for metrics block
     */
    debug() {
        const baseDebug = super.debug();
        return {
            ...baseDebug,
            contentType: 'metrics-only',
            hasData: !!this.lastData,
            dataKeys: this.lastData ? Object.keys(this.lastData) : []
        };
    }
}

// Make ConsistencyMetricsBlock globally available
window.ConsistencyMetricsBlock = ConsistencyMetricsBlock;