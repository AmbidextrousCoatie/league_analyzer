# Centralized Button Management System

## Overview

The centralized button management system provides a robust, constraint-based approach to managing filter buttons in the league analyzer application. It replaces the scattered button management code with a single, centralized solution.

## Key Features

### 1. **Centralized State Management**
- Single source of truth for all button states
- Automatic constraint propagation
- Consistent state across all button groups

### 2. **Constraint-Based Updates**
- When a button changes, only dependent buttons are updated
- Maintains valid selections when possible
- Clears invalid selections automatically

### 3. **Robust Error Handling**
- Graceful handling of API failures
- Clear error messages for users
- Fallback to safe states

### 4. **Dependency Management**
- Button groups are processed in dependency order
- Prerequisites are checked before fetching candidates
- Automatic clearing of dependent selections when prerequisites change

## Button Group Configuration

The system defines button groups with their dependencies and order:

```javascript
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
        dependencies: ['season'],
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
    team: {
        order: 4,
        dependencies: ['season', 'league'],
        endpoint: '/league/get_available_teams',
        containerId: 'buttonsTeam',
        name: 'team'
    }
};
```

## How It Works

### 1. **Button Change Detection**
When a button is clicked, the system:
- Identifies which button group changed (the trigger group)
- Updates the current state
- Stores the new selection as a constraint

### 2. **Constraint Propagation**
The system processes all button groups in order, excluding the trigger group:
- Uses current constraints to fetch candidates
- Checks if current selection is still valid
- If valid: keeps selection and adds to constraints
- If invalid: clears selection and removes from constraints

### 3. **Button Population**
For each button group:
- Fetches candidates using current constraints
- Populates buttons with candidates
- Marks the selected button as checked
- Shows appropriate messages when no candidates available

## Usage

### Basic Integration

```javascript
// Initialize the system
const buttonManager = new CentralizedButtonManager(urlStateManager, 'league');
await buttonManager.initialize();

// Get current state
const currentState = buttonManager.getState();

// Get selected values
const selectedValues = buttonManager.getSelectedValues();

// Get candidates for a specific group
const teamCandidates = buttonManager.getCandidates('team');
```

### Advanced Integration

```javascript
// Use the integration helper
const buttonIntegration = new CentralizedButtonIntegration();
await buttonIntegration.initialize();

// Access all functionality through the integration
const state = buttonIntegration.getCurrentState();
const candidates = buttonIntegration.getCandidates('week');
```

## Migration from Existing System

### 1. **Replace SimpleFilterManager**
```javascript
// OLD:
const filterManager = new SimpleFilterManager(urlStateManager, 'league');
await filterManager.initialize();

// NEW:
const buttonManager = new CentralizedButtonManager(urlStateManager, 'league');
await buttonManager.initialize();
```

### 2. **Update Button Population**
```javascript
// OLD: Manual button population
function updateTeamButtons() {
    fetch('/league/get_available_teams?season=' + season + '&league=' + league)
        .then(response => response.json())
        .then(teams => {
            // Manual button creation...
        });
}

// NEW: Automatic button population
// The centralized system handles this automatically
```

### 3. **Update State Management**
```javascript
// OLD: Manual state updates
function handleButtonChange(buttonName, value) {
    currentState[buttonName] = value;
    // Manual dependent button updates...
}

// NEW: Automatic state management
// The centralized system handles this automatically
```

## Benefits

1. **Reduced Code Duplication**: Single implementation for all button management
2. **Consistent Behavior**: All buttons work the same way
3. **Easier Maintenance**: Changes in one place affect all buttons
4. **Better Error Handling**: Centralized error management
5. **Improved Performance**: Constraint-based updates reduce unnecessary API calls
6. **Easier Testing**: Single system to test instead of multiple scattered functions

## API Endpoints

The system uses the following backend endpoints:

- `/league/get_available_seasons` - Get available seasons
- `/league/get_available_leagues` - Get available leagues
- `/league/get_available_weeks` - Get available weeks (requires season, league)
- `/league/get_available_teams` - Get available teams (requires season, league)

All endpoints support the `database` parameter for database selection.

## Error Handling

The system provides comprehensive error handling:

- **API Failures**: Shows error messages in button containers
- **Missing Containers**: Logs warnings and continues
- **Invalid Selections**: Automatically clears invalid selections
- **Network Issues**: Graceful degradation with retry logic

## Future Enhancements

1. **Caching**: Add caching for frequently accessed data
2. **Debouncing**: Add debouncing for rapid button changes
3. **Loading States**: Show loading indicators during API calls
4. **Custom Validation**: Add custom validation rules for button groups
5. **Analytics**: Track button usage and performance metrics