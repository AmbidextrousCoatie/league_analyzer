/**
 * Event Bus
 * 
 * Central event coordination system for cross-component communication
 * Enables loose coupling between content blocks and state management
 */

class EventBus {
    constructor() {
        this.listeners = new Map();
        this.eventLog = [];
        this.maxLogSize = 100;
        this.debug = false;
    }
    
    /**
     * Subscribe to an event type
     * @param {string} eventType - The event type to listen for
     * @param {function} callback - Function to call when event is emitted
     * @param {object} context - Optional context (this binding) for the callback
     * @param {object} options - Optional configuration
     * @returns {function} Unsubscribe function
     */
    subscribe(eventType, callback, context = null, options = {}) {
        if (!this.listeners.has(eventType)) {
            this.listeners.set(eventType, []);
        }
        
        const listener = {
            callback,
            context,
            options: {
                once: options.once || false,
                priority: options.priority || 0
            },
            id: Date.now() + Math.random()
        };
        
        this.listeners.get(eventType).push(listener);
        
        // Sort by priority (higher priority first)
        this.listeners.get(eventType).sort((a, b) => b.options.priority - a.options.priority);
        
        if (this.debug) {
            console.log(`📝 EventBus: Subscribed to '${eventType}' (${this.listeners.get(eventType).length} listeners)`);
        }
        
        // Return unsubscribe function
        return () => this.unsubscribe(eventType, listener.id);
    }
    
    /**
     * Subscribe to an event only once
     * @param {string} eventType - The event type to listen for
     * @param {function} callback - Function to call when event is emitted
     * @param {object} context - Optional context for the callback
     * @returns {function} Unsubscribe function
     */
    once(eventType, callback, context = null) {
        return this.subscribe(eventType, callback, context, { once: true });
    }
    
    /**
     * Unsubscribe from an event
     * @param {string} eventType - The event type
     * @param {string} listenerId - The listener ID to remove
     */
    unsubscribe(eventType, listenerId) {
        if (this.listeners.has(eventType)) {
            const listeners = this.listeners.get(eventType);
            const index = listeners.findIndex(l => l.id === listenerId);
            if (index !== -1) {
                listeners.splice(index, 1);
                if (this.debug) {
                    console.log(`🗑️ EventBus: Unsubscribed from '${eventType}' (${listeners.length} listeners remaining)`);
                }
            }
        }
    }
    
    /**
     * Emit an event to all subscribers
     * @param {string} eventType - The event type to emit
     * @param {object} data - Data to pass to listeners
     * @param {object} options - Emission options
     */
    emit(eventType, data = {}, options = {}) {
        const timestamp = Date.now();
        const eventData = {
            type: eventType,
            data,
            timestamp,
            source: options.source || 'unknown'
        };
        
        // Log the event
        this.logEvent(eventData);
        
        if (this.debug) {
            console.log(`📢 EventBus: Emitting '${eventType}' from ${eventData.source}:`, data);
        }
        
        if (!this.listeners.has(eventType)) {
            if (this.debug) {
                console.log(`⚠️ EventBus: No listeners for '${eventType}'`);
            }
            return;
        }
        
        const listeners = [...this.listeners.get(eventType)];
        let handled = 0;
        
        listeners.forEach(listener => {
            try {
                if (listener.context) {
                    listener.callback.call(listener.context, eventData);
                } else {
                    listener.callback(eventData);
                }
                handled++;
                
                // Remove one-time listeners
                if (listener.options.once) {
                    this.unsubscribe(eventType, listener.id);
                }
                
            } catch (error) {
                console.error(`❌ EventBus: Error in listener for '${eventType}':`, error);
            }
        });
        
        if (this.debug) {
            console.log(`✅ EventBus: '${eventType}' handled by ${handled}/${listeners.length} listeners`);
        }
    }
    
    /**
     * Log an event for debugging
     * @param {object} eventData - The event data to log
     */
    logEvent(eventData) {
        this.eventLog.push(eventData);
        
        // Maintain log size limit
        if (this.eventLog.length > this.maxLogSize) {
            this.eventLog.shift();
        }
    }
    
    /**
     * Get recent event history
     * @param {number} count - Number of recent events to return
     * @returns {array} Recent events
     */
    getEventHistory(count = 10) {
        return this.eventLog.slice(-count);
    }
    
    /**
     * Clear all listeners and event log
     */
    clear() {
        this.listeners.clear();
        this.eventLog = [];
        if (this.debug) {
            console.log('🧹 EventBus: Cleared all listeners and event log');
        }
    }
    
    /**
     * Get current listener statistics
     * @returns {object} Listener statistics
     */
    getStats() {
        const stats = {
            totalEventTypes: this.listeners.size,
            totalListeners: 0,
            eventTypes: {}
        };
        
        this.listeners.forEach((listeners, eventType) => {
            stats.totalListeners += listeners.length;
            stats.eventTypes[eventType] = listeners.length;
        });
        
        return stats;
    }
    
    /**
     * Enable or disable debug logging
     * @param {boolean} enabled - Whether to enable debug mode
     */
    setDebug(enabled) {
        this.debug = enabled;
        console.log(`🐛 EventBus: Debug mode ${enabled ? 'enabled' : 'disabled'}`);
    }
    
    /**
     * Debug method to show current state
     */
    debugInfo() {
        console.log('=== EventBus Debug Info ===');
        console.log('Stats:', this.getStats());
        console.log('Recent Events:', this.getEventHistory(5));
        console.log('Event Types:', Array.from(this.listeners.keys()));
    }
}

// Create global EventBus instance
window.EventBus = new EventBus();

// Enable debug mode by default in development
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.EventBus.setDebug(true);
}

// Global debug functions
window.debugEventBus = () => window.EventBus.debugInfo();
window.eventBusStats = () => window.EventBus.getStats();