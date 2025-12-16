# Button Constraint Fixes

## Issue Identified

**Problem**: Button population was flawed - not all parameters were being passed to `get_available_XXX` endpoints. Specifically, the league parameter was not being passed when fetching weeks and teams, causing 400 errors.

**Root Cause**: The constraint handling in the centralized button manager was not properly propagating constraints between button groups during the initial load process.

## Fixes Applied

### 1. **Fixed Group Processing Logic**
**Problem**: During initial load, the system was excluding the trigger group, but there was no trigger group during initial load, so all groups should be processed.

**Solution**: Updated `getButtonGroupsInOrder()` method:
```javascript
// During initial load (no trigger group), process all groups
// During state changes, exclude the trigger group
if (this.triggerGroup) {
    return groups.filter(group => group.name !== this.triggerGroup);
}

return groups;
```

### 2. **Enhanced Constraint Debugging**
**Problem**: Difficult to debug constraint propagation issues.

**Solution**: Added comprehensive logging:
- Log constraints being added for each group
- Log current constraints when fetching candidates
- Log constraint updates during auto-selection
- Log HTTP errors with full URLs

### 3. **Added League Auto-Selection**
**Problem**: After auto-selecting a season, no league was automatically selected, so weeks and teams couldn't be fetched.

**Solution**: Added auto-selection logic for league group:
```javascript
// Auto-select logic for league group (if season is available but no league selected)
if (group.name === 'league' && !selectedValue && candidates.length > 0 && this.constraints.season) {
    // Select the first available league
    selectedValue = candidates[0];
    this.selectedValues[group.name] = selectedValue;
    this.currentState[group.name] = selectedValue;
    this.constraints[group.name] = selectedValue;
    
    // Update URL state to reflect the auto-selection
    this.urlStateManager.setState({ [group.name]: selectedValue });
}
```

### 4. **Improved Constraint Propagation**
**Problem**: Constraints weren't being properly propagated between groups during the same processing cycle.

**Solution**: 
- Enhanced logging to track constraint updates
- Ensured constraints are updated immediately when auto-selecting values
- Added debugging to see exactly what parameters are being sent to each endpoint

## How It Works Now

### 1. **Initial Load Process**:
1. Load seasons → Auto-select latest season → Update constraints
2. Load leagues (with season constraint) → Auto-select first league → Update constraints  
3. Load weeks (with season + league constraints) → Populate buttons
4. Load teams (with season + league constraints) → Populate buttons
5. Trigger content rendering

### 2. **State Change Process**:
1. Identify trigger group (e.g., season changed)
2. Process all other groups in dependency order
3. Use current constraints for each group
4. Update constraints as valid selections are found
5. Trigger content rendering

### 3. **Constraint Flow**:
```
Season selected → constraints = {season: "25/26"}
League fetched with season constraint → constraints = {season: "25/26", league: "BZOL N1"}
Weeks fetched with season + league constraints → constraints = {season: "25/26", league: "BZOL N1"}
Teams fetched with season + league constraints → constraints = {season: "25/26", league: "BZOL N1"}
```

## Debugging Output

The system now provides detailed logging:

```
🎯 CentralizedButtonManager: Auto-selected latest season: 25/26
🎯 CentralizedButtonManager: Updated constraints: {season: "25/26"}
🔗 CentralizedButtonManager: Adding constraint season=25/26 for league
🌐 CentralizedButtonManager: Fetching candidates for league: /league/get_available_leagues?season=25/26&database=db_real
🎯 CentralizedButtonManager: Auto-selected first league: BZOL N1
🎯 CentralizedButtonManager: Updated constraints: {season: "25/26", league: "BZOL N1"}
🔗 CentralizedButtonManager: Adding constraint season=25/26 for week
🔗 CentralizedButtonManager: Adding constraint league=BZOL N1 for week
🌐 CentralizedButtonManager: Fetching candidates for week: /league/get_available_weeks?season=25/26&league=BZOL%20N1&database=db_real
```

## Expected Behavior

1. **On Page Load**:
   - Latest season is auto-selected
   - First available league is auto-selected
   - Weeks and teams are populated with correct constraints
   - Content blocks render with the selected season and league

2. **On Button Changes**:
   - Dependent buttons update with proper constraints
   - All API calls include the necessary parameters
   - Content blocks re-render with new state

3. **Error Handling**:
   - HTTP errors are logged with full URLs
   - Constraint propagation is tracked
   - Missing parameters are easily identifiable

## Files Modified

- `app/static/js/core/centralized-button-manager.js` - Fixed constraint handling and added debugging

## Testing

To verify the fixes:

1. **Check Browser Console**: Look for the detailed constraint logging
2. **Check Network Tab**: Verify API calls include all necessary parameters
3. **Test Button Changes**: Ensure dependent buttons update correctly
4. **Test Content Rendering**: Verify content blocks show appropriate data

The system should now properly pass all required parameters to the backend endpoints and avoid the 400 errors you were seeing.