/**
 * URL State Manager
 * 
 * Manages synchronization between application state and URL parameters
 * Provides browser history support and shareable links
 */

class URLStateManager {
    constructor(callbacks = {}) {
        this.callbacks = callbacks;
        this.state = this.parseUrlParams();
        
        // Listen for browser back/forward navigation
        window.addEventListener('popstate', (event) => {
            if (event.state) {
                this.state = event.state;
                this.notifyStateChange();
            }
        });
    }
    
    /**
     * Parse URL parameters into state object
     */
    parseUrlParams() {
        const params = new URLSearchParams(window.location.search);
        return {
            team: params.get('team') || '',
            season: params.get('season') || '',
            week: params.get('week') || '',
            league: params.get('league') || '',
            database: params.get('database') || 'db_sim'
        };
    }
    
    /**
     * Update URL with current state
     */
    updateUrl(newState, replaceHistory = false) {
        // Merge new state with existing state
        this.state = { ...this.state, ...newState };
        
        // Build URL parameters
        const params = new URLSearchParams();
        Object.entries(this.state).forEach(([key, value]) => {
            if (value && value !== '' && value !== 'db_sim') {
                params.set(key, value);
            }
        });
        
        // Update browser URL
        const newUrl = `${window.location.pathname}?${params.toString()}`;
        
        if (replaceHistory) {
            window.history.replaceState(this.state, '', newUrl);
        } else {
            window.history.pushState(this.state, '', newUrl);
        }
        
        console.log('URL updated:', newUrl, 'State:', this.state);
    }
    
    /**
     * Get current state
     */
    getState() {
        return { ...this.state };
    }
    
    /**
     * Update state and URL
     */
    setState(newState, replaceHistory = false) {
        const oldState = { ...this.state };
        this.updateUrl(newState, replaceHistory);
        
        // Only notify if state actually changed
        if (JSON.stringify(oldState) !== JSON.stringify(this.state)) {
            this.notifyStateChange();
        }
    }
    
    /**
     * Notify callbacks of state changes
     */
    notifyStateChange() {
        if (this.callbacks.onStateChange) {
            this.callbacks.onStateChange(this.state);
        }
    }
    
    /**
     * Register callback for state changes
     */
    onStateChange(callback) {
        this.callbacks.onStateChange = callback;
    }
    
    /**
     * Get filter depth (how many filters are active)
     */
    getFilterDepth() {
        let depth = 0;
        if (this.state.database && this.state.database !== 'main') depth++;
        if (this.state.team) depth++;
        if (this.state.season) depth++;
        if (this.state.week) depth++;
        if (this.state.league) depth++;
        return depth;
    }
    
    /**
     * Check if specific filter is active
     */
    hasFilter(filterName) {
        return this.state[filterName] && this.state[filterName] !== '';
    }
    
    /**
     * Clear specific filter and dependent filters
     */
    clearFilter(filterName) {
        const newState = { ...this.state };
        
        // Define filter dependencies (clearing a filter clears dependent ones)
        const dependencies = {
            team: ['season', 'week'],
            season: ['week'],
            league: ['season', 'week']
        };
        
        // Clear the filter
        newState[filterName] = '';
        
        // Clear dependent filters
        if (dependencies[filterName]) {
            dependencies[filterName].forEach(dep => {
                newState[dep] = '';
            });
        }
        
        this.setState(newState);
    }
    
    /**
     * Initialize state from URL on page load
     */
    initializeFromUrl() {
        if (Object.values(this.state).some(value => value && value !== '' && value !== 'main')) {
            this.notifyStateChange();
        }
    }
}

// Make URLStateManager globally available
window.URLStateManager = URLStateManager;