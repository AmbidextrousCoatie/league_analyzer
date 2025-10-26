/**
 * Centralized Button Integration
 * 
 * Example integration of the CentralizedButtonManager with existing systems
 * This shows how to replace the current button management with the centralized approach
 */

class CentralizedButtonIntegration {
    constructor() {
        this.urlStateManager = null;
        this.buttonManager = null;
        this.contentRenderer = null;
    }
    
    /**
     * Initialize the integrated button system
     */
    async initialize() {
        try {
            // Initialize URL state manager (assuming it exists)
            this.urlStateManager = new URLStateManager();
            
            // Initialize centralized button manager
            this.buttonManager = new CentralizedButtonManager(this.urlStateManager, 'league');
            
            // Initialize content renderer (assuming it exists)
            this.contentRenderer = new ContentRenderer(this.urlStateManager);
            
            // Initialize all components
            await Promise.all([
                this.urlStateManager.initialize(),
                this.buttonManager.initialize(),
                this.contentRenderer.initialize()
            ]);
            
            console.log('✅ CentralizedButtonIntegration: All components initialized');
            
        } catch (error) {
            console.error('❌ CentralizedButtonIntegration: Initialization failed:', error);
        }
    }
    
    /**
     * Get current filter state
     */
    getCurrentState() {
        return this.buttonManager ? this.buttonManager.getState() : {};
    }
    
    /**
     * Get selected values
     */
    getSelectedValues() {
        return this.buttonManager ? this.buttonManager.getSelectedValues() : {};
    }
    
    /**
     * Get available candidates for a specific group
     */
    getCandidates(groupName) {
        return this.buttonManager ? this.buttonManager.getCandidates(groupName) : [];
    }
}

// Example usage in your existing templates:
/*
// Replace this in your existing code:
// const filterManager = new SimpleFilterManager(urlStateManager, 'league');
// await filterManager.initialize();

// With this:
const buttonIntegration = new CentralizedButtonIntegration();
await buttonIntegration.initialize();
*/

// Example of how to integrate with existing content rendering:
/*
// In your content rendering code, instead of:
// await contentRenderer.renderContentBlocks(mode, state);

// Use:
const currentState = buttonIntegration.getCurrentState();
await contentRenderer.renderContentBlocks('league', currentState);
*/