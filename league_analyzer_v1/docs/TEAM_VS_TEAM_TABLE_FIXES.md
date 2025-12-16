# Team vs Team Comparison Table Fixes

## Issues Fixed

### 1. **Missing Team Name Column Styling** 🎨
- **Problem**: The team name column (first column) was missing the light gray background styling
- **Root Cause**: The `ColumnGroup` for the team name column was missing the `style` property
- **Fix**: Added `style={"backgroundColor": "#f8f9fa"}` to the frozen left column group

### 2. **Hardcoded Column Titles** 🌐
- **Problem**: Several column titles were still hardcoded instead of using internationalization
- **Fixed Titles**:
  - `'Team'` → `i18n_service.get_text("team")`
  - `'Score'` → `i18n_service.get_text("score")`
  - `'Points'` → `i18n_service.get_text("points")`
  - `'Average'` → `i18n_service.get_text("average")`

## Changes Made

### **File**: `app/services/league_service.py`

#### **Before**:
```python
ColumnGroup(
    title='Team',
    frozen='left',  # Make the team name column sticky
    columns=[
        Column(title='Team', field='team', width='180px', align='left')
    ]
)
```

#### **After**:
```python
ColumnGroup(
    title=i18n_service.get_text("team"),
    frozen='left',  # Make the team name column sticky
    style={"backgroundColor": "#f8f9fa"},  # Light gray background
    columns=[
        Column(title=i18n_service.get_text("team"), field='team', width='180px', align='left')
    ]
)
```

#### **Column Titles Fixed**:
```python
# Before
Column(title='Score', field=f'{team}_score', width='80px', align='center')
Column(title='Points', field=f'{team}_points', width='80px', align='center')
Column(title='Average', field='avg_score', width='80px', align='center')

# After  
Column(title=i18n_service.get_text("score"), field=f'{team}_score', width='80px', align='center')
Column(title=i18n_service.get_text("points"), field=f'{team}_points', width='80px', align='center')
Column(title=i18n_service.get_text("average"), field='avg_score', width='80px', align='center')
```

## Result

### **Visual Improvements**:
✅ **Team Name Column**: Now has the proper light gray background (`#f8f9fa`)  
✅ **Consistent Styling**: Matches other tables in the application  
✅ **Frozen Column**: Team names remain visible when scrolling horizontally  

### **Internationalization**:
✅ **German**: "Team", "Pins", "Pkt.", "Durchschnitt"  
✅ **English**: "Team", "Score", "Points", "Average"  
✅ **Dynamic**: Column titles change when language is switched  

## Testing

1. **Visual Check**: Team name column should have light gray background
2. **Language Switch**: Column titles should update to selected language
3. **Scrolling**: Team names should remain visible when scrolling horizontally
4. **Heat Map**: Score/points cells should still have proper heat map colors

The team vs team comparison table now has proper styling and full internationalization! 🎉