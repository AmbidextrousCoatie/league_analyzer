# Filter Combinations Matrix

## Quick Reference: What Shows When

| Filters Selected | Primary Content Block | Key Components Displayed |
|------------------|----------------------|---------------------------|
| **League Only** | LeagueAggregationBlock | • League averages over time<br/>• Points to win history<br/>• All-time top performers<br/>• Record games |
| **League + Season** | LeagueSeasonOverviewBlock | • Season timetable<br/>• Final standings<br/>• Season progress charts<br/>• Individual averages |
| **League + Season + Week** | MatchDayBlock | • Week standings<br/>• Honor scores for week |
| **League + Season + Week + Team** | TeamDetailsBlock | • Team score sheet (3 views)<br/>• Player details for week |
| **League + Season + Team** | TeamSeasonBlock | • Team season history<br/>• Team-specific charts<br/>• Season progress for team |

## Data Flow Architecture

```
User Selects Filters
        ↓
Filter State Updated
        ↓
Content Blocks Check shouldRender()
        ↓
Matching Block Loads Data
        ↓
API Calls with Filtered Parameters
        ↓
Components Render with Data
```

## Implementation Status

### ✅ Currently Working (Phase 1)
- League + Season + Week (MatchDayBlock)
- League + Season + Week + Team (TeamDetailsBlock)
- Basic League + Season (partial LeagueSeasonOverviewBlock)

### 🚧 Needs Backend Endpoints (Phase 2)
- League Only (LeagueAggregationBlock)
- Complete League + Season (missing timetable, averages)
- League + Season + Team (TeamSeasonBlock - not created yet)

### 📋 Next Steps
1. **Create missing backend endpoints** for aggregation data
2. **Implement TeamSeasonBlock** for team season analysis
3. **Remove debugging logs** once system is stable
4. **Add loading states** for better UX

## Filter Validation Rules

### Valid Combinations
- ✅ League only
- ✅ League + Season  
- ✅ League + Season + Week
- ✅ League + Season + Week + Team
- ✅ League + Season + Team

### Invalid Combinations (Auto-Clear)
- ❌ Season without League → Clear season
- ❌ Week without Season → Clear week  
- ❌ Team without Season → Clear team
- ❌ Week + Team without both League + Season → Clear both

## Performance Considerations

### Data Loading Strategy
- **Parallel Loading**: Multiple API calls simultaneously where possible
- **Caching**: Consider caching static data (league history, etc.)
- **Progressive Enhancement**: Show available data immediately, load optional data later
- **Error Isolation**: One failed endpoint doesn't break entire view

### User Experience
- **Immediate Feedback**: Show loading states during data fetch
- **Graceful Degradation**: Missing data shows placeholder, not error
- **Responsive Design**: Charts and tables adapt to screen size
- **Consistent Navigation**: Filter changes maintain context where logical