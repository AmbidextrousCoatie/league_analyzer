# Trigger Group Detection Fix

## Issue Identified

**Problem**: When changing the league, the system was not detecting the change and therefore not triggering content refresh.

**Root Cause**: The button change event handler was updating `this.currentState` before `handleStateChange` was called, causing the `findChangedButtonGroup` method to compare identical values and fail to detect the change.

## The Problem Sequence

1. **User clicks league button** → "BZL N2"
2. **Button change event fires** → Updates `this.currentState[league] = "BZL N2"`
3. **URL state manager calls handleStateChange** → with new state containing "BZL N2"
4. **findChangedButtonGroup compares** → old state "BZL N2" vs new state "BZL N2"
5. **No change detected** → "No trigger group found, skipping update"

## Fix Applied

**Solution**: Remove the `this.currentState` update from the button change event handler, letting `handleStateChange` handle the state update after detecting the change.

### Before (Broken):
```javascript
document.addEventListener('change', (event) => {
    if (target.type === 'radio' && this.buttonGroups[target.name]) {
        const groupName = target.name;
        const value = target.value;
        
        // Update selected values and constraints
        this.selectedValues[groupName] = value;
        this.currentState[groupName] = value;  // ❌ This breaks change detection
        this.constraints[groupName] = value;
        
        // Update URL state (this will trigger handleStateChange)
        this.urlStateManager.setState({ [groupName]: value });
    }
});
```

### After (Fixed):
```javascript
document.addEventListener('change', (event) => {
    if (target.type === 'radio' && this.buttonGroups[target.name]) {
        const groupName = target.name;
        const value = target.value;
        
        // Update selected values and constraints, but NOT currentState yet
        this.selectedValues[groupName] = value;
        this.constraints[groupName] = value;  // ✅ Only update constraints
        
        // Update URL state (this will trigger handleStateChange)
        this.urlStateManager.setState({ [groupName]: value });
    }
});
```

## How It Works Now

### 1. **User clicks league button** → "BayL"
2. **Button change event fires** → Updates `selectedValues` and `constraints` only
3. **URL state manager calls handleStateChange** → with new state containing "BayL"
4. **findChangedButtonGroup compares** → old state "BZOL N1" vs new state "BayL"
5. **Change detected** → "Found changed group: league"
6. **Content refresh triggered** → Teams re-fetched, content re-rendered

## Expected Behavior

### 1. **League Change Detection**:
- ✅ System detects league changes properly
- ✅ Trigger group identified correctly
- ✅ Content refresh triggered

### 2. **Content Updates**:
- ✅ Teams re-fetched with new league constraint
- ✅ Content blocks re-render with new data
- ✅ API calls made with correct parameters

### 3. **Debugging Output**:
```
🎯 CentralizedButtonManager: Button changed - league: BayL
🎯 CentralizedButtonManager: Updated constraints: {season: '25/26', league: 'BayL', week: '1'}
🔄 CentralizedButtonManager: State changed: {team: '', season: '25/26', week: '1', league: 'BayL'}
🔍 CentralizedButtonManager: Finding changed button group...
🔍 CentralizedButtonManager: Checking league - old: "BZOL N1", new: "BayL"
🎯 CentralizedButtonManager: Found changed group: league
🎯 CentralizedButtonManager: Trigger group: league
🔄 CentralizedButtonManager: Triggering state change callback with state: {team: '', season: '25/26', week: '1', league: 'BayL'}
✅ CentralizedButtonManager: State change callback executed successfully
```

## Files Modified

- `app/static/js/core/centralized-button-manager.js` - Fixed button change event handler

## Testing

To verify the fix:

1. **Change the league** from "BZOL N1" to "BayL"
2. **Check console output** - should see "Found changed group: league"
3. **Verify content refresh** - teams should update, API calls should be made
4. **Check network tab** - should see new API calls with BayL parameter

The system should now properly detect league changes and trigger content refresh!