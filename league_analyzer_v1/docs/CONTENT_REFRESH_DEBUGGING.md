# Content Refresh Debugging

## Issue Identified

**Problem**: When both season and week are selected, and user changes the league, the button behaves correctly but no content refresh is triggered (no routes are called).

**Root Cause**: Need to investigate why the content rendering callback isn't being triggered when the league changes.

## Debugging Enhancements Added

### 1. **Enhanced State Change Logging** 🔍
**Added**: Detailed logging to track state changes and processing flags

```javascript
async handleStateChange(newState) {
    if (this.isInitializing || this.isProcessingUpdate) {
        console.log('⚠️ CentralizedButtonManager: Skipping state change - isInitializing:', this.isInitializing, 'isProcessingUpdate:', this.isProcessingUpdate);
        return;
    }
    
    console.log('🔄 CentralizedButtonManager: State changed:', newState);
    console.log('🔄 CentralizedButtonManager: Previous state:', this.currentState);
    // ... rest of method
}
```

### 2. **Enhanced Trigger Group Detection** 🎯
**Added**: Detailed logging to track which button group changed

```javascript
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
```

### 3. **Enhanced Callback Execution Logging** 🔄
**Added**: Detailed logging to track callback execution

```javascript
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
```

## Expected Debugging Output

When you change the league, you should see output like this:

```
🎯 CentralizedButtonManager: Button changed - league: BayL
🎯 CentralizedButtonManager: Updated constraints: {season: "25/26", league: "BayL"}
🔄 CentralizedButtonManager: State changed: {season: "25/26", week: "1", league: "BayL"}
🔄 CentralizedButtonManager: Previous state: {season: "25/26", week: "1", league: "BZL N2"}
🔍 CentralizedButtonManager: Finding changed button group...
🔍 CentralizedButtonManager: Checking season - old: "25/26", new: "25/26"
🔍 CentralizedButtonManager: Checking league - old: "BZL N2", new: "BayL"
🎯 CentralizedButtonManager: Found changed group: league
🎯 CentralizedButtonManager: Trigger group: league
🎯 CentralizedButtonManager: Updated constraints for trigger group league: {season: "25/26", league: "BayL"}
📋 CentralizedButtonManager: Processing groups: ["season", "week", "team"]
🔄 CentralizedButtonManager: Triggering state change callback with state: {season: "25/26", week: "1", league: "BayL"}
🔄 CentralizedButtonManager: Callback function: function
✅ CentralizedButtonManager: State change callback executed successfully
```

## What to Look For

### 1. **State Change Detection**:
- Check if `handleStateChange` is being called
- Check if the trigger group is being detected correctly
- Check if the state is being updated properly

### 2. **Callback Execution**:
- Check if the callback function is registered
- Check if the callback is being executed
- Check if there are any errors in the callback

### 3. **Processing Flags**:
- Check if `isProcessingUpdate` is preventing execution
- Check if `isInitializing` is preventing execution

## Possible Issues to Investigate

### 1. **Race Condition**:
- Multiple state changes happening simultaneously
- `isProcessingUpdate` flag not being reset properly

### 2. **Callback Not Registered**:
- The callback function might not be properly registered
- The callback might be undefined or null

### 3. **State Comparison Issue**:
- The `findChangedButtonGroup` might not be detecting the change
- String vs number comparison issues

### 4. **URL State Manager Issue**:
- The URL state manager might not be triggering the callback
- The state might not be properly propagated

## Next Steps

1. **Test the debugging output** by changing the league
2. **Check the console logs** to see where the process is failing
3. **Identify the specific issue** based on the debugging output
4. **Apply the appropriate fix** based on the findings

The enhanced debugging should help identify exactly where the content refresh process is failing!