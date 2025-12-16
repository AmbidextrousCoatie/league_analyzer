# Database Switching Fix

## Problem
The content was fixed (500 errors resolved), but users couldn't switch to `db_real` database. The database selector would appear to work, but the application would remain on `db_sim` or not properly refresh content.

## Root Cause Analysis

### 1. **URLStateManager Default Database** 🗄️
**Issue**: The `URLStateManager` was defaulting to `'db_sim'` instead of `'db_real'`

**Location**: `app/static/js/core/url-state-manager.js`

**Fix**: Changed default database from `'db_sim'` to `'db_real'`

```javascript
parseUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        team: params.get('team') || '',
        season: params.get('season') || '',
        week: params.get('week') || '',
        league: params.get('league') || '',
        database: params.get('database') || 'db_real'  // Changed from 'db_sim'
    };
}
```

### 2. **Missing Database Change Event Handlers** 🔄
**Issue**: The team stats and league stats apps weren't listening for database change events

**Fix**: Added `databaseChanged` event listeners and handlers

#### Team Stats App (`app/static/js/team-stats-app.js`):
```javascript
// Listen for database changes
window.addEventListener('databaseChanged', (event) => {
    console.log('🔄 Database changed event received:', event.detail);
    this.handleDatabaseChange(event.detail.database);
});

// Handle database changes
async handleDatabaseChange(newDatabase) {
    console.log('🔄 Handling database change to:', newDatabase);
    
    try {
        // Update URL state with new database
        const currentState = this.urlStateManager.getState();
        const newState = {
            ...currentState,
            database: newDatabase,
            team: '', // Reset team selection
            season: '', // Reset season selection
            week: '' // Reset week selection
        };
        
        // Update URL state
        this.urlStateManager.setState(newState);
        
        // Repopulate team dropdown with new database
        await this.populateTeamDropdown();
        
        // Reinitialize button manager with new state
        if (this.buttonManager) {
            await this.buttonManager.handleStateChange(newState);
        }
        
        // Render content with new state
        if (this.contentRenderer) {
            this.contentRenderer.renderContent(newState);
        }
        
        console.log('✅ Database change handled successfully');
        
    } catch (error) {
        console.error('❌ Error handling database change:', error);
    }
}
```

#### League Stats App (`app/static/js/league-stats-app.js`):
```javascript
// Listen for database changes
window.addEventListener('databaseChanged', (event) => {
    console.log('🔄 Database changed event received:', event.detail);
    this.handleDatabaseChange(event.detail.database);
});

// Handle database changes
async handleDatabaseChange(newDatabase) {
    console.log('🔄 Handling database change to:', newDatabase);
    
    try {
        // Update URL state with new database
        const currentState = this.urlStateManager.getState();
        const newState = {
            ...currentState,
            database: newDatabase,
            team: '', // Reset team selection
            season: '', // Reset season selection
            week: '', // Reset week selection
            league: '' // Reset league selection
        };
        
        // Update URL state
        this.urlStateManager.setState(newState);
        
        // Reinitialize button manager with new state
        if (this.buttonManager) {
            await this.buttonManager.handleStateChange(newState);
        }
        
        // Render content with new state
        this.renderContent();
        
        console.log('✅ Database change handled successfully');
        
    } catch (error) {
        console.error('❌ Error handling database change:', error);
    }
}
```

## How Database Switching Works

### 1. **Database Selector Component** 🎛️
- Located in `app/templates/components/database_selector.html`
- Provides UI dropdown for database selection
- Handles AJAX switching via `/main/switch-database` endpoint

### 2. **Database Switch Process** 🔄
1. User selects new database from dropdown
2. AJAX request sent to `/main/switch-database` endpoint
3. Server validates and switches database
4. `databaseChanged` event dispatched to frontend
5. Apps listen for event and handle database change
6. URL state updated with new database
7. Content refreshed with new data

### 3. **State Reset on Database Change** 🔄
When database changes:
- All filter selections reset (team, season, week, league)
- Team dropdown repopulated with new database data
- Button groups refreshed with new constraints
- Content blocks re-rendered with new data

## Files Modified

### 1. **`app/static/js/core/url-state-manager.js`**
- Changed default database from `'db_sim'` to `'db_real'`

### 2. **`app/static/js/team-stats-app.js`**
- Added `databaseChanged` event listener
- Added `handleDatabaseChange` method
- Added team dropdown repopulation on database change

### 3. **`app/static/js/league-stats-app.js`**
- Added `databaseChanged` event listener
- Added `handleDatabaseChange` method
- Added button manager reinitialization on database change

## Expected Behavior After Fix

### 1. **Database Switching** ✅
- Database selector should work properly
- Switching to `db_real` should succeed
- Content should refresh with new data

### 2. **State Management** ✅
- URL should update with new database parameter
- Filter selections should reset on database change
- New data should load from selected database

### 3. **Content Refresh** ✅
- Team dropdown should repopulate with new teams
- Button groups should refresh with new constraints
- Content blocks should render with new data

### 4. **Error Handling** ✅
- Graceful fallback if AJAX switching fails
- Page reload fallback for database switching
- Proper error logging and user feedback

## Testing Database Switching

1. **Open team stats page** - should default to `db_real`
2. **Switch to `db_sim`** - should work and show simulated data
3. **Switch back to `db_real`** - should work and show real data
4. **Check URL** - should contain `?database=db_real` or `?database=db_sim`
5. **Verify content** - should show different data for each database

The database switching should now work properly on both team and league stats pages!