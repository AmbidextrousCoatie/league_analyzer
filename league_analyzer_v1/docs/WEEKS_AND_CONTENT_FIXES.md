# Weeks and Content Block Fixes

## Issues Identified

### 1. **Weeks Button Error**
**Problem**: `TypeError: candidate.replace is not a function` when processing weeks
**Root Cause**: The weeks API returns numeric values (e.g., `[1, 2, 3]`) but the code expected strings

### 2. **Content Blocks Timing Issue**
**Problem**: Content blocks were created AFTER the first render attempt, so they weren't available initially
**Root Cause**: Button manager was initialized before content blocks were created

## Fixes Applied

### 1. **Fixed Weeks Button Population** 🔧
**Problem**: `candidate.replace is not a function` error
**Solution**: Added string conversion in button population logic

```javascript
// Create buttons HTML
const buttonsHtml = candidates.map(candidate => {
    const isChecked = candidate === selectedValue;
    // Ensure candidate is a string and create safe ID
    const candidateStr = String(candidate);
    const safeId = candidateStr.replace(/\s+/g, '_').replace(/[^a-zA-Z0-9_-]/g, '');
    
    return `
        <input type="radio" class="btn-check" name="${group.name}" id="${group.name}_${safeId}" 
               value="${candidateStr}" ${isChecked ? 'checked' : ''}>
        <label class="btn btn-outline-primary" for="${group.name}_${safeId}">${candidateStr}</label>
    `;
}).join('');
```

### 2. **Fixed Content Blocks Timing** ⏰
**Problem**: Content blocks created after first render attempt
**Solution**: Reordered initialization to create content blocks first

```javascript
async initializeContentBlocks() {
    // Create content blocks FIRST (they initialize in their constructors)
    const seasonLeagueStandingsBlock = new SeasonLeagueStandingsBlock();
    // ... other blocks
    
    // Store blocks
    this.contentBlocks.set('season-league-standings', seasonLeagueStandingsBlock);
    // ... other blocks
    
    console.log('✅ Content blocks initialized');
    
    // THEN initialize button manager
    this.buttonManager = new CentralizedButtonManager(this.urlStateManager, 'league', callback);
    await this.buttonManager.initialize();
}
```

### 3. **Added Week Auto-Selection** 🎯
**Problem**: No week was auto-selected, so weeks buttons remained empty
**Solution**: Added auto-selection logic for weeks

```javascript
// Auto-select logic for week group
if (group.name === 'week' && !selectedValue && candidates.length > 0 && 
    this.constraints.season && this.constraints.league) {
    // Select the first available week
    selectedValue = String(candidates[0]); // Ensure it's a string
    this.selectedValues[group.name] = selectedValue;
    this.currentState[group.name] = selectedValue;
    this.constraints[group.name] = selectedValue;
    
    // Update URL state to reflect the auto-selection
    this.urlStateManager.setState({ [group.name]: selectedValue });
}
```

### 4. **Enhanced Debugging** 🔍
**Problem**: Difficult to debug API responses and data types
**Solution**: Added comprehensive logging

```javascript
const candidates = await response.json();
console.log(`📊 CentralizedButtonManager: Received candidates for ${group.name}:`, candidates);
console.log(`📊 CentralizedButtonManager: Candidate types:`, candidates.map(c => typeof c));
```

## How It Works Now

### 1. **Initialization Flow**:
1. Create all content blocks first
2. Store content blocks in the map
3. Initialize button manager with callback
4. Button manager processes all groups with auto-selection
5. Content blocks are available for rendering

### 2. **Button Population Flow**:
1. Fetch candidates from API
2. Convert all candidates to strings for safe processing
3. Auto-select first available option for each group
4. Create HTML buttons with proper IDs and values
5. Update state and constraints

### 3. **Auto-Selection Flow**:
1. Season: Auto-select latest season
2. League: Auto-select first available league (if season selected)
3. Week: Auto-select first available week (if season + league selected)
4. Team: No auto-selection (user must choose)

## Expected Behavior

### 1. **On Page Load**:
- ✅ Latest season auto-selected
- ✅ First league auto-selected
- ✅ First week auto-selected
- ✅ All buttons populated correctly
- ✅ Content blocks available for rendering
- ✅ Content renders with selected values

### 2. **Button Population**:
- ✅ Handles both string and numeric API responses
- ✅ Creates safe HTML IDs for all button types
- ✅ Properly converts values to strings
- ✅ No more `replace is not a function` errors

### 3. **Content Rendering**:
- ✅ Content blocks available from first render
- ✅ All blocks render with appropriate data
- ✅ No "No content blocks available" warnings

## Debugging Output

The system now provides detailed logging:

```
📊 CentralizedButtonManager: Received candidates for week: [1, 2, 3, 4, 5]
📊 CentralizedButtonManager: Candidate types: ["number", "number", "number", "number", "number"]
🎯 CentralizedButtonManager: Auto-selected first week: 1
🎯 CentralizedButtonManager: Updated constraints: {season: "25/26", league: "BZOL N1", week: "1"}
✅ CentralizedButtonManager: Populated week with 5 candidates, selected: 1
```

## Files Modified

- `app/static/js/core/centralized-button-manager.js` - Fixed string conversion and added week auto-selection
- `app/static/js/league-stats-app.js` - Fixed content blocks timing

## Testing

To verify the fixes:

1. **Check Browser Console**: Look for the detailed candidate type logging
2. **Check Weeks Buttons**: Should be populated with numbers (1, 2, 3, etc.)
3. **Check Content Rendering**: Should show content blocks immediately
4. **Test Button Changes**: All buttons should work without errors

The system should now properly handle numeric API responses and render content blocks correctly!