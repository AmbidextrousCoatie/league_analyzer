# Team vs Team Description Internationalization

## Overview
Added multilanguage support for the team vs team comparison matrix description string that includes dynamic week/season information.

## Changes Made

### 1. **Added Translation Keys** 🌐
- **File**: `app/services/i18n_service.py`
- **Added Keys**:
  - `average_scores_and_match_points_between_teams`
  - `week` (already existed, but ensured consistency)
  - `season` (already existed, but ensured consistency)

#### English Translations:
```javascript
"average_scores_and_match_points_between_teams": "Average scores and match points between teams",
"week": "Week",
"season": "Season"
```

#### German Translations:
```javascript
"average_scores_and_match_points_between_teams": "Durchschnittliche Ergebnisse und Matchpunkte zwischen Teams",
"week": "Spieltag", 
"season": "Saison"
```

### 2. **Updated Backend Translation Route** 🔄
- **File**: `app/routes/league_routes.py`
- **Change**: Added new translation keys to the `/league/get_translations` endpoint
- **Added**: `"average_scores_and_match_points_between_teams"`, `"week"`, `"season"`

### 3. **Internationalized Description String** 📝
- **File**: `app/services/league_service.py` (Line 3099)
- **Before**:
  ```python
  description=f"Average scores and match points between teams{f' (Week {week})' if week else ' (Season)'}"
  ```
- **After**:
  ```python
  description=f"{i18n_service.get_text('average_scores_and_match_points_between_teams')}{f' ({i18n_service.get_text('week')} {week})' if week else f' ({i18n_service.get_text('season')})'}"
  ```

## Result

### English Version:
- **With Week**: "Average scores and match points between teams (Week 5)"
- **Without Week**: "Average scores and match points between teams (Season)"

### German Version:
- **With Week**: "Durchschnittliche Ergebnisse und Matchpunkte zwischen Teams (Spieltag 5)"
- **Without Week**: "Durchschnittliche Ergebnisse und Matchpunkte zwischen Teams (Saison)"

## Benefits

✅ **Consistent Translation**: All parts of the description are now properly translated  
✅ **Dynamic Content**: Week/season information adapts to the current language  
✅ **Maintainable**: Easy to update translations without touching business logic  
✅ **User Experience**: German users see familiar terminology throughout  

## Testing

1. **English Mode**: Description shows "Average scores and match points between teams (Week X)"
2. **German Mode**: Description shows "Durchschnittliche Ergebnisse und Matchpunkte zwischen Teams (Spieltag X)"
3. **Season Mode**: Shows "Season" in English or "Saison" in German
4. **Language Switch**: Description updates immediately when language is changed

The team vs team comparison matrix description is now fully internationalized! 🌐