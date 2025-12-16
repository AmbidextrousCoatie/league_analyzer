# League Selection Fixes

## Issue Identified

**Problem**: Team selection was almost always defaulting to "BZOL N1" even when user manually selected "BayL". The system was auto-selecting the first league and then using that as a constraint for fetching teams, overriding user selections.

**Root Cause**: 
1. Auto-selection logic was running during state changes, not just initial load
2. Button change events weren't properly updating constraints
3. System wasn't re-fetching teams with the new league constraint

## Fixes Applied

### 1. **Fixed Auto-Selection Timing** ⏰
**Problem**: Auto-selection was running during state changes, overriding user selections
**Solution**: Added `!this.triggerGroup` condition to auto-selection logic

```javascript
// Auto-select logic for league group (if season is available but no league selected)
// Only auto-select during initial load, not during state changes
if (group.name === 'league' && !selectedValue && candidates.length > 0 && this.constraints.season && !this.triggerGroup) {
    // Auto-select first league only during initial load
    selectedValue = candidates[0];
    // ... rest of auto-selection logic
}
```

### 2. **Fixed Button Change Event Handling** 🔧
**Problem**: Button changes weren't updating constraints properly
**Solution**: Update constraints immediately when button changes

```javascript
document.addEventListener('change', (event) => {
    if (target.type === 'radio' && this.buttonGroups[target.name]) {
        const groupName = target.name;
        const value = target.value;
        
        // Update selected values and constraints
        this.selectedValues[groupName] = value;
        this.currentState[groupName] = value;
        this.constraints[groupName] = value;
        
        console.log(`🎯 CentralizedButtonManager: Updated constraints:`, this.constraints);
        
        // Update URL state (this will trigger handleStateChange)
        this.urlStateManager.setState({ [groupName]: value });
    }
});
```

### 3. **Enhanced State Change Handling** 🔄
**Problem**: State changes weren't properly updating constraints for trigger group
**Solution**: Explicitly update constraints for the changed group

```javascript
async handleStateChange(newState) {
    // ... existing logic ...
    
    // Update constraints for the changed group
    if (this.triggerGroup && newState[this.triggerGroup]) {
        this.constraints[this.triggerGroup] = newState[this.triggerGroup];
        console.log(`🎯 CentralizedButtonManager: Updated constraints for trigger group ${this.triggerGroup}:`, this.constraints);
    }
    
    // Process button groups with constraint-based updates
    await this.processAllButtonGroups();
}
```

### 4. **Added Comprehensive Debugging** 🔍
**Problem**: Difficult to debug constraint updates and state changes
**Solution**: Added detailed logging

```javascript
console.log('🔄 CentralizedButtonManager: State changed:', newState);
console.log('🔄 CentralizedButtonManager: Previous state:', this.currentState);
console.log(`🎯 CentralizedButtonManager: Updated constraints for trigger group ${this.triggerGroup}:`, this.constraints);
```

## How It Works Now

### 1. **Initial Load Process**:
1. Load seasons → Auto-select latest season
2. Load leagues → Auto-select first league (only during initial load)
3. Load weeks → Auto-select first week (only during initial load)
4. Load teams → Use selected league constraint

### 2. **User Selection Process**:
1. User clicks different league button
2. Button change event updates constraints immediately
3. State change handler processes dependent groups
4. Teams are re-fetched with new league constraint
5. Content is re-rendered with new selection

### 3. **Constraint Flow**:
```
Initial: {season: "25/26", league: "BZOL N1"} → teams for BZOL N1
User selects BayL: {season: "25/26", league: "BayL"} → teams for BayL
```

## Expected Behavior

### 1. **Initial Load**:
- ✅ Latest season auto-selected
- ✅ First league auto-selected (BZOL N1)
- ✅ Teams loaded for BZOL N1

### 2. **User Changes League**:
- ✅ User selects "BayL"
- ✅ Constraints updated immediately
- ✅ Teams re-fetched for "BayL"
- ✅ Content re-rendered with BayL teams
- ✅ No auto-selection interference

### 3. **Subsequent Changes**:
- ✅ User selections are preserved
- ✅ Dependent groups update correctly
- ✅ No unwanted auto-selection

## Debugging Output

The system now provides detailed logging:

```
🎯 CentralizedButtonManager: Button changed - league: BayL
🎯 CentralizedButtonManager: Updated constraints: {season: "25/26", league: "BayL"}
🔄 CentralizedButtonManager: State changed: {season: "25/26", league: "BayL"}
🔄 CentralizedButtonManager: Previous state: {season: "25/26", league: "BZOL N1"}
🎯 CentralizedButtonManager: Trigger group: league
🎯 CentralizedButtonManager: Updated constraints for trigger group league: {season: "25/26", league: "BayL"}
🔗 CentralizedButtonManager: Adding constraint season=25/26 for team
🔗 CentralizedButtonManager: Adding constraint league=BayL for team
🌐 CentralizedButtonManager: Fetching candidates for team: /league/get_available_teams?season=25%2F26&league=BayL&database=db_real
```

## Files Modified

- `app/static/js/core/centralized-button-manager.js` - Fixed auto-selection timing and constraint updates

## Testing

To verify the fixes:

1. **Check Initial Load**: Should auto-select BZOL N1
2. **Change League**: Select BayL, verify teams update
3. **Check Console**: Look for constraint update logging
4. **Verify API Calls**: Teams endpoint should use correct league parameter

The system should now properly respect user selections and update teams based on the selected league!