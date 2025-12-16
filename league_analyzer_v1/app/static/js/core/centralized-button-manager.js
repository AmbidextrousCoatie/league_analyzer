/**
 * Centralized Button Manager
 * 
 * Robust, centralized system for managing filter buttons with constraint-based updates
 * Handles the complete lifecycle: fetch candidates, populate buttons, manage state
 */

class CentralizedButtonManager {
    constructor(urlStateManager, mode = 'league', onStateChange = null) {
        this.urlStateManager = urlStateManager;
        this.mode = mode; // 'team' or 'league'
        this.isInitializing = false;
        this.isProcessingUpdate = false;
        this.onStateChange = onStateChange; // Callback for state changes
        
        // Button group definitions with their dependencies and order
        this.buttonGroups = {
            season: {
                order: 1,
                dependencies: [],
                endpoint: '/league/get_available_seasons',
                containerId: 'buttonsSeason',
                name: 'season'
            },
            league: {
                order: 2,
                dependencies: [], // allow league selection without season
                endpoint: '/league/get_available_leagues',
                containerId: 'buttonsLeague',
                name: 'league'
            },
            week: {
                order: 3,
                dependencies: ['season', 'league'],
                endpoint: '/league/get_available_weeks',
                containerId: 'buttonsWeek',
                name: 'week'
            },
            round: {
                order: 4,
                dependencies: ['season', 'league', 'week'],
                endpoint: '/league/get_available_rounds',
                containerId: 'buttonsRound',
                name: 'round'
            },
            team: {
                order: 5,
                dependencies: ['season', 'league'],
                endpoint: '/league/get_available_teams',
                containerId: 'buttonsTeam',
                name: 'team'
            }
        };
        
        // Current state and constraints
        this.currentState = {};
        this.constraints = {};
        this.availableCandidates = {};
        this.selectedValues = {};
        this.leagueMetadata = new Map();
        
        // Track which button group triggered the update
        this.triggerGroup = null;
        
        // Listen for state changes from URL manager
        this.urlStateManager.onStateChange((state) => {
            this.handleStateChange(state);
        });
    }
    
    /**
     * Initialize the button manager
     */
    async initialize() {
        this.isInitializing = true;
        
        try {
            // Set up event listeners
            this.setupButtonEventListeners();
            
            // Get current state and handle initial setup
            const currentState = this.urlStateManager.getState();
            await this.handleInitialState(currentState);
            
        } catch (error) {
            console.error('❌ CentralizedButtonManager: Initialization failed:', error);
        } finally {
            this.isInitializing = false;
        }
    }
    
    /**
     * Handle initial state from URL parameters
     */
    async handleInitialState(state) {
        console.log('🚀 CentralizedButtonManager: Handling initial state:', state);
        
        // Store current state
        this.currentState = { ...state };
        this.selectedValues = { ...state };
        
        // Start with no constraints - load all available data
        this.constraints = {};
        
        // Process all button groups in order
        await this.processAllButtonGroups();
    }
    
    /**
     * Handle state changes from URL manager
     */
    async handleStateChange(newState) {
        if (this.isInitializing || this.isProcessingUpdate) {
            console.log('⚠️ CentralizedButtonManager: Skipping state change - isInitializing:', this.isInitializing, 'isProcessingUpdate:', this.isProcessingUpdate);
            return;
        }
        
        console.log('🔄 CentralizedButtonManager: State changed:', newState);
        console.log('🔄 CentralizedButtonManager: Previous state:', this.currentState);
        
        // Find which button group changed
        this.triggerGroup = this.findChangedButtonGroup(newState);
        
        if (!this.triggerGroup) {
            console.log('⚠️ CentralizedButtonManager: No trigger group found, skipping update');
            return;
        }
        
        console.log(`🎯 CentralizedButtonManager: Trigger group: ${this.triggerGroup}`);
        
        // Update current state
        this.currentState = { ...newState };
        this.selectedValues = { ...newState };
        
        // Update constraints for the changed group
        if (this.triggerGroup && newState[this.triggerGroup]) {
            this.constraints[this.triggerGroup] = newState[this.triggerGroup];
            console.log(`🎯 CentralizedButtonManager: Updated constraints for trigger group ${this.triggerGroup}:`, this.constraints);
        }
        
        // Process button groups with constraint-based updates
        await this.processAllButtonGroups();
    }
    
    /**
     * Find which button group triggered the change
     */
    findChangedButtonGroup(newState) {
        console.log('🔍 CentralizedButtonManager: Finding changed button group...');
        for (const [groupName, groupConfig] of Object.entries(this.buttonGroups)) {
            const oldValue = this.currentState[groupConfig.name];
            const newValue = newState[groupConfig.name];
            
            console.log(`🔍 CentralizedButtonManager: Checking ${groupName} - old: "${oldValue}", new: "${newValue}"`);
            
            if (oldValue !== newValue) {
                console.log(`🎯 CentralizedButtonManager: Found changed group: ${groupName}`);
                return groupName;
            }
        }
        console.log('⚠️ CentralizedButtonManager: No changed group found');
        return null;
    }
    
    /**
     * Process all button groups in dependency order
     */
    async processAllButtonGroups() {
        this.isProcessingUpdate = true;
        
        try {
            // Get button groups in order
            const groupsToProcess = this.getButtonGroupsInOrder();
            
            console.log('📋 CentralizedButtonManager: Processing groups:', groupsToProcess.map(g => g.name));
            console.log('📋 CentralizedButtonManager: Current constraints:', this.constraints);
            
            // Process each group sequentially
            for (const group of groupsToProcess) {
                await this.processButtonGroup(group);
            }
            
            // Trigger state change callback for content rendering
            if (this.onStateChange) {
                console.log('🔄 CentralizedButtonManager: Triggering state change callback with state:', this.currentState);
                console.log('🔄 CentralizedButtonManager: Callback function:', typeof this.onStateChange);
                try {
                    this.onStateChange(this.currentState);
                    console.log('✅ CentralizedButtonManager: State change callback executed successfully');
                } catch (error) {
                    console.error('❌ CentralizedButtonManager: Error in state change callback:', error);
                }
            } else {
                console.warn('⚠️ CentralizedButtonManager: No state change callback registered');
            }
            
        } catch (error) {
            console.error('❌ CentralizedButtonManager: Error processing button groups:', error);
        } finally {
            this.isProcessingUpdate = false;
        }
    }
    
    /**
     * Get button groups in dependency order
     */
    getButtonGroupsInOrder() {
        const groups = Object.entries(this.buttonGroups)
            .map(([name, config]) => ({ name, ...config }))
            .sort((a, b) => a.order - b.order);
        
        // During initial load (no trigger group), process all groups
        // During state changes, exclude the trigger group
        if (this.triggerGroup) {
            return groups.filter(group => group.name !== this.triggerGroup);
        }
        
        return groups;
    }
    
    /**
     * Process a single button group
     */
    async processButtonGroup(group) {
        console.log(`🔧 CentralizedButtonManager: Processing group ${group.name}`);
        
        try {
            // Check if prerequisites are met
            if (!this.arePrerequisitesMet(group)) {
                console.log(`⚠️ CentralizedButtonManager: Prerequisites not met for ${group.name}`);
                // Do NOT clear league selection when season is deselected
                if (group.name === 'league') {
                    console.log('ℹ️ Keeping existing league selection despite missing prerequisites');
                    return;
                }
                console.log(`⚠️ CentralizedButtonManager: Clearing buttons for ${group.name}`);
                this.clearButtonGroup(group);
                return;
            }
            
            // Fetch candidates for this group
            const rawCandidates = await this.fetchCandidates(group);
            const candidates = this.normalizeCandidates(group, rawCandidates);
            
            if (!candidates || candidates.length === 0) {
                console.log(`⚠️ CentralizedButtonManager: No candidates for ${group.name}, clearing buttons`);
                this.clearButtonGroup(group);
                return;
            }
            
            // Store candidates
            this.availableCandidates[group.name] = candidates;
            
            // Check if current selection is still valid
            const currentSelection = this.selectedValues[group.name];
            const isValidSelection = currentSelection && candidates.some(candidate => 
                String(this.getCandidateValue(candidate, group.name)) === String(currentSelection)
            );
            
            if (isValidSelection) {
                console.log(`✅ CentralizedButtonManager: Keeping current selection for ${group.name}: ${currentSelection}`);
                // Add to constraints for next groups
                this.constraints[group.name] = currentSelection;
                if (group.name === 'league') {
                    const selectedCandidate = candidates.find(candidate => 
                        String(this.getCandidateValue(candidate, group.name)) === String(currentSelection)
                    );
                    const longName = selectedCandidate 
                        ? (selectedCandidate.longName || selectedCandidate.long_name || selectedCandidate.label || currentSelection) 
                        : '';
                    this.currentState.league_long = longName;
                    this.selectedValues.league_long = longName;
                    
                     // Ensure URL state also carries the long name (replace state to avoid new history entries)
                    const urlState = this.urlStateManager.getState();
                    if (longName && urlState.league_long !== longName) {
                        this.urlStateManager.setState({ league_long: longName }, true);
                    }
                }
            } else {
                console.log(`🔄 CentralizedButtonManager: Invalid selection for ${group.name}, clearing selection`);
                // Clear this group's selection and don't add constraints
                this.selectedValues[group.name] = '';
                this.currentState[group.name] = '';
                delete this.constraints[group.name];
                if (group.name === 'league') {
                    this.selectedValues.league_long = '';
                    this.currentState.league_long = '';
                }
            }
            
            // Always populate buttons with candidates, regardless of current selection validity
            console.log(`🎨 CentralizedButtonManager: Populating buttons for ${group.name} with ${candidates.length} candidates`);
            this.populateButtonGroup(group, candidates);
            
        } catch (error) {
            console.error(`❌ CentralizedButtonManager: Error processing group ${group.name}:`, error);
            this.showError(group, error.message);
        }
    }
    
    /**
     * Check if prerequisites are met for a button group
     */
    arePrerequisitesMet(group) {
        return group.dependencies.every(dep => this.selectedValues[dep]);
    }
    
    /**
     * Fetch candidates for a button group
     */
    async fetchCandidates(group) {
        const params = new URLSearchParams();
        
        // Add constraints as parameters
        Object.entries(this.constraints).forEach(([key, value]) => {
            if (value) {
                params.append(key, value);
                console.log(`🔗 CentralizedButtonManager: Adding constraint ${key}=${value} for ${group.name}`);
            }
        });
        
        // Add database parameter
        const urlParams = new URLSearchParams(window.location.search);
        const database = urlParams.get('database') || 'db_sim';
        params.append('database', database);
        
        const url = `${group.endpoint}?${params.toString()}`;
        console.log(`🌐 CentralizedButtonManager: Fetching candidates for ${group.name}: ${url}`);
        console.log(`🌐 CentralizedButtonManager: Current constraints for ${group.name}:`, this.constraints);
        
        const response = await fetch(url);
        if (!response.ok) {
            console.error(`❌ CentralizedButtonManager: HTTP ${response.status} for ${group.name}: ${url}`);
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const candidates = await response.json();
        console.log(`📊 CentralizedButtonManager: Received candidates for ${group.name}:`, candidates);
        //console.log(`📊 CentralizedButtonManager: Candidate types:`, candidates.map(c => typeof c));
        
        return candidates;
    }
    
    /**
     * Populate button group with candidates
     */
    populateButtonGroup(group, candidates) {
        const container = document.getElementById(group.containerId);
        if (!container) {
            console.warn(`⚠️ CentralizedButtonManager: Container not found: ${group.containerId}`);
            return;
        }
        
        let selectedValue = this.selectedValues[group.name] || '';
        selectedValue = selectedValue != null ? String(selectedValue) : '';
        
        if (group.name === 'league') {
            this.leagueMetadata.clear();
        }
        
        console.log(`🎨 CentralizedButtonManager: Populating ${group.name} - current selection: "${selectedValue}", candidates:`, candidates);
        
        // Auto-select logic for season group ONLY when explicitly set to 'latest'
        if (group.name === 'season' && selectedValue === 'latest' && candidates.length > 0) {
            // Sort seasons and select the latest one
            const sortedCandidates = [...candidates].sort((a, b) => {
                const aNum = parseInt(a);
                const bNum = parseInt(b);
                if (!isNaN(aNum) && !isNaN(bNum)) return bNum - aNum; // Latest first
                return b.localeCompare(a); // String comparison, latest first
            });
            const latest = sortedCandidates[0];
            this.selectedValues[group.name] = latest;
            this.currentState[group.name] = latest;
            this.constraints[group.name] = latest;
            console.log(`🎯 CentralizedButtonManager: Resolved season 'latest' -> ${latest}`);
            this.urlStateManager.setState({ [group.name]: latest });
            selectedValue = latest;
        }
        
        // Auto-select logic for league group (if season is available but no league selected)
        // Only auto-select during initial load, not during state changes
        // DISABLED: No auto-selection of league to allow season-only view
        if (group.name === 'league' && !selectedValue && candidates.length > 0 && this.constraints.season && !this.triggerGroup) {
            // Don't auto-select league - let user choose or view season-only
            console.log(`🎯 CentralizedButtonManager: Skipping league auto-selection - allowing season-only view`);
        }
        
        // Auto-select logic for week group (if season and league are available but no week selected)
        // Only auto-select during initial load, not during state changes
        // DISABLED: No auto-selection of week since it requires league selection
        if (group.name === 'week' && !selectedValue && candidates.length > 0 && this.constraints.season && this.constraints.league && !this.triggerGroup) {
            // Don't auto-select week - requires league to be selected first
            console.log(`🎯 CentralizedButtonManager: Skipping week auto-selection - requires league selection first`);
        }
        
        // Create buttons HTML
        const buttonsHtml = candidates.map(candidate => {
            if (group.name === 'league') {
                const value = String(this.getCandidateValue(candidate, group.name));
                const longName = candidate.longName || candidate.long_name || candidate.label || value;
                const isChecked = value === selectedValue;
                const safeId = this.createSafeId(value, group.name);
                const escapedValue = this.escapeAttribute(value);
                const escapedLong = this.escapeAttribute(longName);
                const escapedLabel = this.escapeHtml(value);
                
                this.leagueMetadata.set(value, longName);
                
                return `
                    <input type="radio" class="btn-check" name="${group.name}" id="${group.name}_${safeId}" 
                           value="${escapedValue}" data-long-name="${escapedLong}" ${isChecked ? 'checked' : ''}>
                    <label class="btn btn-outline-primary" for="${group.name}_${safeId}" title="${this.escapeAttribute(longName)}">
                        ${escapedLabel}
                    </label>
                `;
            }
            
            const candidateStr = String(candidate);
            const isChecked = candidateStr === selectedValue;
            const safeId = this.createSafeId(candidateStr, group.name);
            const escapedValue = this.escapeAttribute(candidateStr);
            const escapedLabel = this.escapeHtml(candidateStr);
            
            return `
                <input type="radio" class="btn-check" name="${group.name}" id="${group.name}_${safeId}" 
                       value="${escapedValue}" ${isChecked ? 'checked' : ''}>
                <label class="btn btn-outline-primary" for="${group.name}_${safeId}">${escapedLabel}</label>
            `;
        }).join('');
        
        container.innerHTML = buttonsHtml;
        
        console.log(`✅ CentralizedButtonManager: Populated ${group.name} with ${candidates.length} candidates, selected: ${selectedValue}`);
        console.log(`✅ CentralizedButtonManager: Created ${candidates.length} buttons for ${group.name}`);
    }
    
    /**
     * Clear a button group
     */
    clearButtonGroup(group) {
        const container = document.getElementById(group.containerId);
        if (container) {
            const message = this.getClearMessage(group);
            container.innerHTML = `<span class="text-muted">${message}</span>`;
        }
        
        // Clear selection
        this.selectedValues[group.name] = '';
        this.currentState[group.name] = '';
        delete this.constraints[group.name];
        
        if (group.name === 'league') {
            this.leagueMetadata.clear();
            this.selectedValues.league_long = '';
            this.currentState.league_long = '';
            delete this.constraints.league_long;
        }
    }
    
    /**
     * Get appropriate message when clearing button group
     */
    getClearMessage(group) {
        const depNames = group.dependencies.map(dep => this.buttonGroups[dep].name).join(', ');
        
        // Special message for league group when no league is selected
        if (group.name === 'league' && this.constraints.season && !this.constraints.league) {
            return 'Wählen Sie eine Liga aus oder lassen Sie leer für Saison-Übersicht';
        }
        
        return `Wählen Sie ${depNames} aus`;
    }
    
    /**
     * Show error message for a button group
     */
    showError(group, message) {
        const container = document.getElementById(group.containerId);
        if (container) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Error loading ${group.name}:</strong> ${message}
                </div>
            `;
        }
    }
    
    /**
     * Set up event listeners for button changes
     */
    setupButtonEventListeners() {
        // Use event delegation for all filter buttons
        document.addEventListener('change', (event) => {
            const target = event.target;
            
            if (target.type === 'radio' && this.buttonGroups[target.name]) {
                const groupName = target.name;
                const value = target.value;
                
                console.log(`🎯 CentralizedButtonManager: Button changed - ${groupName}: ${value}`);
                
                // Update selected values and constraints, but NOT currentState yet
                this.selectedValues[groupName] = value;
                this.constraints[groupName] = value;
                
                const stateUpdate = { [groupName]: value };
                
                if (groupName === 'league') {
                    const longName = target.dataset.longName || this.getLeagueLongName(value) || '';
                    stateUpdate.league_long = longName;
                    this.selectedValues.league_long = longName;
                }
                
                console.log(`🎯 CentralizedButtonManager: Updated constraints:`, this.constraints);
                
                // Update URL state (this will trigger handleStateChange)
                this.urlStateManager.setState(stateUpdate);
            }
        });
        
        // Add click event listeners for deselection functionality
        document.addEventListener('click', (event) => {
            let target = event.target;
            
            // Find the radio input if clicking on label
            if (target.tagName === 'LABEL' && target.htmlFor) {
                const radioInput = document.getElementById(target.htmlFor);
                if (radioInput && radioInput.type === 'radio') {
                    target = radioInput;
                }
            }
            
            if (target.type === 'radio' && this.buttonGroups[target.name]) {
                const groupName = target.name;
                const value = target.value;
                const currentlySelected = this.selectedValues[groupName];
                
                // Check if clicking the same button that was already selected
                if (currentlySelected === value) {
                    console.log(`🎯 CentralizedButtonManager: Deselecting ${groupName}: ${value}`);
                    
                    // Prevent the default radio button behavior
                    event.preventDefault();
                    event.stopPropagation();
                    target.checked = false;
                    
                    // Clear selection and update state
                    this.selectedValues[groupName] = '';
                    if (groupName === 'league') {
                        this.selectedValues.league_long = '';
                        this.urlStateManager.setState({ league: '', league_long: '' });
                    } else {
                        this.urlStateManager.setState({ [groupName]: '' });
                    }
                }
            }
        });
    }
    
    normalizeCandidates(group, candidates) {
        if (!Array.isArray(candidates)) {
            return [];
        }
        
        if (group.name === 'league') {
            return this.normalizeLeagueCandidates(candidates);
        }
        
        return candidates;
    }
    
    normalizeLeagueCandidates(candidates) {
        return candidates.map(candidate => {
            if (candidate && typeof candidate === 'object') {
                const value = candidate.value || candidate.short_name || candidate.code || candidate.id || candidate.name || '';
                const longName = candidate.long_name || candidate.longName || candidate.label || candidate.name || value;
                const label = candidate.label || longName || value;
                
                return {
                    value: value != null ? String(value) : '',
                    longName: longName != null ? String(longName) : '',
                    label: label != null ? String(label) : ''
                };
            }
            
            const strValue = candidate != null ? String(candidate) : '';
            return {
                value: strValue,
                longName: strValue,
                label: strValue
            };
        }).filter(candidate => candidate.value);
    }
    
    getCandidateValue(candidate, groupName) {
        if (groupName === 'league' && candidate && typeof candidate === 'object') {
            return candidate.value;
        }
        return candidate;
    }
    
    getLeagueLongName(value) {
        if (!value) {
            return '';
        }
        return this.leagueMetadata.get(value) || '';
    }
    
    createSafeId(value) {
        return String(value || '').replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_-]/g, '');
    }
    
    escapeAttribute(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }
    
    escapeHtml(value) {
        return String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }
    
    /**
     * Get current state
     */
    getState() {
        return { ...this.currentState };
    }
    
    /**
     * Get selected values
     */
    getSelectedValues() {
        return { ...this.selectedValues };
    }
    
    /**
     * Get available candidates for a group
     */
    getCandidates(groupName) {
        return this.availableCandidates[groupName] || [];
    }
}