/**
 * Smart Event Router
 * 
 * Intelligent event routing that determines which blocks should respond to which events
 * Prevents unnecessary re-renders by only notifying interested blocks
 */

class SmartEventRouter {
    constructor(eventBus) {
        this.eventBus = eventBus;
        this.blockInterests = new Map();
        this.setupCoreEventMapping();
    }
    
    /**
     * Setup core event to block mapping
     */
    setupCoreEventMapping() {
        // Define which events affect which blocks
        this.coreEventMapping = {
            // Filter changes
            'filter-changed-team': ['team-history', 'league-comparison', 'clutch-analysis', 'consistency-metrics', 'special-matches'],
            'filter-changed-season': ['league-comparison', 'clutch-analysis', 'consistency-metrics', 'special-matches'],
            'filter-changed-week': ['clutch-analysis', 'special-matches'], // team-history doesn't care about weeks
            'filter-changed-league': ['league-comparison'],
            
            // Data events
            'data-loaded': [], // All blocks might be interested in shared data
            'data-error': [], // All blocks might need to handle errors
            
            // Block lifecycle events
            'block-rendering': [], // Status updates of interest to coordinators
            'block-rendered': [], // Status updates of interest to coordinators
            'block-error': [], // Error events of interest to coordinators
            
            // UI events
            'content-mode-changed': [], // All blocks need to know about mode changes
            'filters-cleared': ['team-history', 'league-comparison', 'clutch-analysis', 'consistency-metrics', 'special-matches']
        };
    }
    
    /**
     * Register a block's interest in specific events
     * @param {string} blockId - The ID of the block
     * @param {array} eventTypes - Array of event types the block is interested in
     * @param {object} options - Additional options
     */
    registerBlockInterests(blockId, eventTypes, options = {}) {
        this.blockInterests.set(blockId, {
            eventTypes: new Set(eventTypes),
            options: {
                priority: options.priority || 0,
                conditions: options.conditions || null // Optional function to check if block should respond
            }
        });
        
        console.log(`🎯 SmartEventRouter: Registered interests for '${blockId}': [${eventTypes.join(', ')}]`);
    }
    
    /**
     * Route a filter change event to interested blocks
     * @param {string} filterType - The type of filter that changed (team, season, week, league)
     * @param {object} changeData - Data about the filter change
     */
    routeFilterChange(filterType, changeData) {
        const eventType = `filter-changed-${filterType}`;
        const interestedBlocks = this.getInterestedBlocks(eventType);
        
        console.log(`🔀 SmartEventRouter: Routing '${eventType}' to [${interestedBlocks.join(', ')}]`);
        
        // Emit specific event for each interested block
        interestedBlocks.forEach(blockId => {
            this.eventBus.emit(`${eventType}:${blockId}`, {
                filterType,
                blockId,
                ...changeData
            }, { source: 'SmartEventRouter' });
        });
        
        // Also emit general event for coordinators
        this.eventBus.emit(eventType, {
            filterType,
            interestedBlocks,
            ...changeData
        }, { source: 'SmartEventRouter' });
    }
    
    /**
     * Route a content mode change event
     * @param {string} oldMode - The previous content mode
     * @param {string} newMode - The new content mode
     * @param {object} state - Current filter state
     */
    routeContentModeChange(oldMode, newMode, state) {
        const allBlocks = Array.from(this.blockInterests.keys());
        
        console.log(`🔀 SmartEventRouter: Content mode changed ${oldMode} → ${newMode}`);
        
        // Emit to all blocks since mode changes affect visibility/rendering
        allBlocks.forEach(blockId => {
            this.eventBus.emit(`content-mode-changed:${blockId}`, {
                oldMode,
                newMode,
                state,
                blockId
            }, { source: 'SmartEventRouter' });
        });
        
        // General event for coordinators
        this.eventBus.emit('content-mode-changed', {
            oldMode,
            newMode,
            state,
            affectedBlocks: allBlocks
        }, { source: 'SmartEventRouter' });
    }
    
    /**
     * Route a data sharing event
     * @param {string} dataType - The type of data being shared
     * @param {object} data - The data being shared
     * @param {string} sourceBlock - The block that provided the data
     */
    routeDataSharing(dataType, data, sourceBlock) {
        // Determine which blocks might be interested in this data
        const potentiallyInterested = this.getBlocksInterestedInData(dataType);
        
        console.log(`🔀 SmartEventRouter: Sharing '${dataType}' data from '${sourceBlock}' to [${potentiallyInterested.join(', ')}]`);
        
        potentiallyInterested.forEach(blockId => {
            if (blockId !== sourceBlock) { // Don't send data back to the source
                this.eventBus.emit(`data-available:${blockId}`, {
                    dataType,
                    data,
                    sourceBlock,
                    blockId
                }, { source: 'SmartEventRouter' });
            }
        });
    }
    
    /**
     * Get blocks interested in a specific event type
     * @param {string} eventType - The event type
     * @returns {array} Array of interested block IDs
     */
    getInterestedBlocks(eventType) {
        // Check core mapping first
        if (this.coreEventMapping[eventType]) {
            return [...this.coreEventMapping[eventType]];
        }
        
        // Check registered block interests
        const interested = [];
        this.blockInterests.forEach((interests, blockId) => {
            if (interests.eventTypes.has(eventType)) {
                interested.push(blockId);
            }
        });
        
        return interested;
    }
    
    /**
     * Determine which blocks might be interested in specific data
     * @param {string} dataType - The type of data
     * @returns {array} Array of potentially interested block IDs
     */
    getBlocksInterestedInData(dataType) {
        // Map data types to potentially interested blocks
        const dataInterestMapping = {
            'team-data': ['team-history', 'league-comparison', 'clutch-analysis', 'consistency-metrics', 'special-matches'],
            'team-history': ['league-comparison'], // League comparison might use team history data
            'league-comparison': ['team-history'], // Team history might use league data
            'season-data': ['clutch-analysis', 'consistency-metrics', 'special-matches'],
            'clutch-data': ['consistency-metrics'], // Consistency might use clutch data
            'consistency-data': ['clutch-analysis'] // Clutch might use consistency data
        };
        
        return dataInterestMapping[dataType] || [];
    }
    
    /**
     * Update block interests dynamically
     * @param {string} blockId - The block ID
     * @param {array} newEventTypes - New event types to listen for
     */
    updateBlockInterests(blockId, newEventTypes) {
        if (this.blockInterests.has(blockId)) {
            this.blockInterests.get(blockId).eventTypes = new Set(newEventTypes);
            console.log(`🔄 SmartEventRouter: Updated interests for '${blockId}': [${newEventTypes.join(', ')}]`);
        } else {
            this.registerBlockInterests(blockId, newEventTypes);
        }
    }
    
    /**
     * Remove a block from the router
     * @param {string} blockId - The block ID to remove
     */
    unregisterBlock(blockId) {
        this.blockInterests.delete(blockId);
        console.log(`🗑️ SmartEventRouter: Unregistered block '${blockId}'`);
    }
    
    /**
     * Get routing statistics
     * @returns {object} Routing statistics
     */
    getStats() {
        return {
            registeredBlocks: this.blockInterests.size,
            coreEventTypes: Object.keys(this.coreEventMapping).length,
            blockInterests: Object.fromEntries(
                Array.from(this.blockInterests.entries()).map(([blockId, interests]) => [
                    blockId,
                    Array.from(interests.eventTypes)
                ])
            )
        };
    }
    
    /**
     * Debug method to show current routing configuration
     */
    debugInfo() {
        console.log('=== SmartEventRouter Debug Info ===');
        console.log('Stats:', this.getStats());
        console.log('Core Event Mapping:', this.coreEventMapping);
        console.log('Block Interests:', Object.fromEntries(this.blockInterests));
    }
}

// Export for use by other modules
window.SmartEventRouter = SmartEventRouter;