# Handicap Calculation Enhancement

**Date:** 2025-01-27  
**Status:** ✅ Implemented

---

## Overview

Enhanced handicap system with:
1. **Calculation Methods**: Moving window average and cumulative average
2. **Handicap Capping**: Maximum handicap value limit
3. **Score Capping**: Option to cap final handicap scores at 300
4. **Validation**: Scratch scores max 300, handicap validation

---

## Implementation

### 1. HandicapSettings Value Object (`domain/value_objects/handicap_settings.py`)

Configuration for handicap calculation:

**Properties:**
- `enabled`: Whether handicap is enabled for the league
- `calculation_method`: `MOVING_WINDOW`, `CUMULATIVE_AVERAGE`, or `FIXED`
- `base_average`: Base average for calculation (typically 200)
- `percentage`: Percentage of difference (typically 0.9 = 90%)
- `max_handicap`: Maximum handicap value (None = no limit)
- `moving_window_size`: Number of games for moving window (None = all games)
- `cap_handicap_score`: Whether to cap final score at 300
- `scratch_score_max`: Maximum scratch score (300 = perfect game)

**Methods:**
- `calculate_handicap(player_average)`: Calculate handicap from player average
- `apply_handicap_to_score(scratch_score, handicap_value)`: Apply with capping

**Formula:**
```
handicap = (base_average - player_average) * percentage
handicap = min(handicap, max_handicap)  # Apply max cap
handicap = max(handicap, 0)  # Cannot be negative
```

### 2. HandicapCalculator Domain Service (`domain/domain_services/handicap_calculator.py`)

Calculates handicap based on game results:

**Methods:**
- `calculate_handicap(game_results, settings)`: Calculate handicap from results
- `_calculate_moving_window_average()`: Average of last N games
- `_calculate_cumulative_average()`: Average of all games in season
- `apply_handicap_with_capping()`: Apply handicap with score capping
- `recalculate_handicap_for_season()`: Recalculate when new games are played

**Calculation Methods:**

1. **Moving Window Average:**
   - Uses last N games (where N = `moving_window_size`)
   - Most recent games first
   - Example: Last 3 games = [180, 190, 200] → average = 190

2. **Cumulative Average:**
   - Uses all games in the season
   - Example: All games = [150, 160, 170, 180, 190] → average = 170

### 3. Handicap Value Object Enhancement (`domain/value_objects/handicap.py`)

Updated to support capping:

- `apply_to_score(scratch_score, cap_at_300=False)`: Apply handicap with optional capping
- Validates scratch score doesn't exceed 300
- Can cap final score at 300 if requested

### 4. GameResult Enhancement (`domain/value_objects/game_result.py`)

Added method for capped scores:

- `get_handicap_score_capped(cap_at_300=True)`: Get handicap score with capping

### 5. Score Validation (`domain/value_objects/score.py`)

Updated validation:

- Allows scores > 300 for handicap scores
- Scratch scores should be validated at creation (0-300)
- Handicap can push scores above 300 (unless capped)

### 6. League Entity Enhancement (`domain/entities/league.py`)

Added handicap settings:

- `handicap_settings`: Optional HandicapSettings
- `set_handicap_settings()`: Set handicap configuration
- `has_handicap_enabled()`: Check if handicap is enabled

---

## Usage Examples

### Setting Up Handicap for a League

```python
from domain.value_objects import HandicapSettings, HandicapCalculationMethod
from domain.entities import League, Season

# Cumulative average method
settings = HandicapSettings(
    enabled=True,
    calculation_method=HandicapCalculationMethod.CUMULATIVE_AVERAGE,
    base_average=200.0,
    percentage=0.9,  # 90% of difference
    max_handicap=50.0,  # Cap handicap at 50 pins
    cap_handicap_score=True  # Cap final score at 300
)

league = League(name="Test League", season=Season("2024-25"))
league.set_handicap_settings(settings)
```

### Moving Window Method

```python
# Moving window (last 5 games)
settings = HandicapSettings(
    enabled=True,
    calculation_method=HandicapCalculationMethod.MOVING_WINDOW,
    base_average=200.0,
    percentage=0.9,
    max_handicap=50.0,
    moving_window_size=5  # Last 5 games
)
```

### Calculating Handicap

```python
from domain.domain_services import HandicapCalculator
from domain.value_objects import Score, Points, GameResult

# Player's game results (scratch scores)
results = [
    GameResult(player_id=player.id, position=1, 
               scratch_score=Score(180), points=Points(2.0)),
    GameResult(player_id=player.id, position=1, 
               scratch_score=Score(190), points=Points(2.0)),
    GameResult(player_id=player.id, position=1, 
               scratch_score=Score(185), points=Points(2.0)),
]

# Calculate handicap
handicap = HandicapCalculator.calculate_handicap(results, settings)
# Result: Handicap(9.0) for average 190: (200 - 190) * 0.9 = 9.0
```

### Applying Handicap with Capping

```python
scratch_score = Score(280)
handicap = Handicap(20.0)

# Apply with capping (caps at 300)
final_score = HandicapCalculator.apply_handicap_with_capping(
    scratch_score, handicap, settings
)
# Result: Score(300) - capped at 300 even though 280 + 20 = 300
```

### Recalculating During Season

```python
# Initial handicap
initial_handicap = HandicapCalculator.calculate_handicap(results, settings)

# Player bowls more games
new_results = results + [
    GameResult(player_id=player.id, position=1, 
               scratch_score=Score(200), points=Points(2.0))
]

# Recalculate (handicap may change)
updated_handicap = HandicapCalculator.recalculate_handicap_for_season(
    new_results, settings, initial_handicap
)
```

---

## Business Rules

### 1. Scratch Score Validation
- **Maximum**: 300 (perfect game)
- **Minimum**: 0
- **Validation**: Enforced when creating Score value object

### 2. Handicap Calculation
- **Formula**: `(base_average - player_average) * percentage`
- **Minimum**: 0 (cannot be negative)
- **Maximum**: `max_handicap` if set
- **Methods**: Moving window or cumulative average

### 3. Handicap Capping
- **Max Handicap**: Configurable per league (e.g., 50 pins)
- **Applied**: Before adding to scratch score
- **Purpose**: Prevent excessive handicap advantage

### 4. Score Capping
- **Option**: `cap_handicap_score` in settings
- **When enabled**: Final score capped at 300
- **When disabled**: Handicap can push score above 300
- **Example**: Scratch 280 + Handicap 30 = 310 (capped) or 310 (uncapped)

### 5. Handicap Updates
- **Frequency**: Can be recalculated after each game
- **Method**: Based on calculation method (moving window or cumulative)
- **Tracking**: Stored per player per season

---

## Validation Summary

✅ **Scratch Score**: 0-300 (enforced in Score value object)  
✅ **Handicap Value**: Non-negative, optionally capped at max_handicap  
✅ **Final Score**: Optionally capped at 300 if `cap_handicap_score=True`  
✅ **Calculation**: Validates sufficient game results exist  
✅ **Settings**: Validates all configuration parameters  

---

## Testing

All functionality tested:
- ✅ Moving window calculation
- ✅ Cumulative average calculation
- ✅ Handicap capping (max_handicap)
- ✅ Score capping (cap at 300)
- ✅ Scratch score validation (max 300)
- ✅ Handicap recalculation
- ✅ League handicap settings

---

## Future Enhancements

1. **Handicap History Tracking**: Track handicap changes over time
2. **Automatic Recalculation**: Auto-recalculate after each game
3. **Different Formulas**: Support other handicap formulas (e.g., 100% of difference)
4. **Per-Player Settings**: Allow different handicap settings per player
5. **Handicap Reports**: Show handicap progression during season

