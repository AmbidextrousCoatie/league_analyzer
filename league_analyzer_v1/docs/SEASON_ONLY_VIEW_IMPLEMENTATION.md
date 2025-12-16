# Season-Only View Implementation

## Changes Made

**Goal**: Allow users to enter the league stats page with only the latest season selected, without auto-selecting a league, enabling a season-only overview view.

## Modifications Applied

### 1. **Disabled League Auto-Selection** 🚫
**Before**: System auto-selected first available league (e.g., "BayL")
**After**: No league auto-selection, allowing season-only view

```javascript
// Auto-select logic for league group (if season is available but no league selected)
// Only auto-select during initial load, not during state changes
// DISABLED: No auto-selection of league to allow season-only view
if (group.name === 'league' && !selectedValue && candidates.length > 0 && this.constraints.season && !this.triggerGroup) {
    // Don't auto-select league - let user choose or view season-only
    console.log(`🎯 CentralizedButtonManager: Skipping league auto-selection - allowing season-only view`);
}
```

### 2. **Disabled Week Auto-Selection** 🚫
**Before**: System auto-selected first available week when league was selected
**After**: No week auto-selection since it requires league selection

```javascript
// Auto-select logic for week group (if season and league are available but no week selected)
// Only auto-select during initial load, not during state changes
// DISABLED: No auto-selection of week since it requires league selection
if (group.name === 'week' && !selectedValue && candidates.length > 0 && this.constraints.season && this.constraints.league && !this.triggerGroup) {
    // Don't auto-select week - requires league to be selected first
    console.log(`🎯 CentralizedButtonManager: Skipping week auto-selection - requires league selection first`);
}
```

### 3. **Enhanced League Button Message** 💬
**Before**: Generic "Wählen Sie Saison aus" message
**After**: Specific message explaining season-only option

```javascript
getClearMessage(group) {
    const depNames = group.dependencies.map(dep => this.buttonGroups[dep].name).join(', ');
    
    // Special message for league group when no league is selected
    if (group.name === 'league' && this.constraints.season && !this.constraints.league) {
        return 'Wählen Sie eine Liga aus oder lassen Sie leer für Saison-Übersicht';
    }
    
    return `Wählen Sie ${depNames} aus`;
}
```

## Expected Behavior

### 1. **Initial Page Load**:
- ✅ **Latest season auto-selected** (e.g., "25/26")
- ✅ **No league auto-selected** - league buttons show with helpful message
- ✅ **No week auto-selected** - week buttons show "Wählen Sie Liga aus"
- ✅ **No team auto-selected** - team buttons show "Wählen Sie Liga aus"

### 2. **Season-Only View**:
- ✅ **Content blocks render** with season-only data
- ✅ **User can select league** to drill down to specific league data
- ✅ **User can leave league unselected** to see season overview

### 3. **User Experience**:
- ✅ **Clear guidance** - league buttons show "Wählen Sie eine Liga aus oder lassen Sie leer für Saison-Übersicht"
- ✅ **Flexible navigation** - users can choose their level of detail
- ✅ **No forced selections** - users aren't forced into specific leagues

## Content Block Behavior

### 1. **Season-Only Content**:
- Content blocks that support season-only view will render
- Content blocks requiring league selection will show appropriate messages
- Users get a high-level season overview

### 2. **League Selection**:
- When user selects a league, dependent content (weeks, teams) becomes available
- Content blocks update to show league-specific data
- Full functionality available for selected league

## Debugging Output

The system now provides clear logging:

```
🎯 CentralizedButtonManager: Auto-selected latest season: 25/26
🎯 CentralizedButtonManager: Skipping league auto-selection - allowing season-only view
🎯 CentralizedButtonManager: Skipping week auto-selection - requires league selection first
```

## Files Modified

- `app/static/js/core/centralized-button-manager.js` - Disabled league and week auto-selection, enhanced messages

## Benefits

### 1. **Better User Experience**:
- Users aren't forced into specific leagues
- Clear season overview available immediately
- Flexible navigation options

### 2. **Reduced Cognitive Load**:
- No unexpected auto-selections
- Users control their level of detail
- Clear guidance on available options

### 3. **Improved Usability**:
- Season-only view for high-level analysis
- League selection for detailed analysis
- No forced navigation paths

The system now provides a much more flexible and user-friendly experience!