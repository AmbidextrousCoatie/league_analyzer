# Handicap Feature - Domain Model Enhancement

**Date:** 2025-01-27  
**Status:** ✅ Implemented

---

## Overview

Added support for individual handicap in bowling leagues/tournaments. Handicap is additional pins added to a player's scratch score and can change during a season.

---

## Implementation

### 1. Handicap Value Object (`domain/value_objects/handicap.py`)

Immutable value object representing a bowling handicap:

- **Properties:**
  - `value`: The handicap value (non-negative)
  - `max_handicap`: Optional maximum handicap limit (0 = no limit)

- **Validation:**
  - Handicap cannot be negative
  - Handicap cannot exceed maximum (if set)

- **Methods:**
  - `apply_to_score(scratch_score)`: Apply handicap to a scratch score, returns Score
  - Arithmetic operations: `__add__`, `__sub__`
  - Comparisons: `__lt__`, `__le__`, `__gt__`, `__ge__`, `__eq__`

### 2. GameResult Enhancement (`domain/value_objects/game_result.py`)

Updated to support both scratch and handicap scores:

- **New Properties:**
  - `scratch_score`: The actual score (pins knocked down)
  - `handicap`: Optional handicap value object
  - `handicap_score`: Computed property (scratch_score + handicap)

- **Backward Compatibility:**
  - `score` property returns `handicap_score` if handicap exists, otherwise `scratch_score`
  - Existing code using `result.score` continues to work

- **Methods:**
  - `has_handicap()`: Check if handicap is applied

### 3. Player Entity Enhancement (`domain/entities/player.py`)

Added season-based handicap tracking:

- **New Properties:**
  - `_handicaps`: Dictionary mapping season -> handicap

- **New Methods:**
  - `set_handicap(season, handicap)`: Set handicap for a season
  - `get_handicap(season)`: Get handicap for a season (returns Optional[Handicap])
  - `has_handicap(season)`: Check if player has handicap for season
  - `remove_handicap(season)`: Remove handicap for a season

- **Design Decision:**
  - Handicap is tracked per season (can change during season)
  - Handicap is stored as a dictionary to allow updates

### 4. Game Entity Enhancement (`domain/entities/game.py`)

Updated to handle handicap in results:

- **Updated Methods:**
  - `update_result()`: Now accepts optional handicap parameter
  - `add_result()`: Uses `handicap_score` for domain events

---

## Usage Examples

### Setting Player Handicap

```python
from domain.entities import Player
from domain.value_objects import Season, Handicap

player = Player(name="John Doe")
season = Season("2024-25")
handicap = Handicap(20.0)  # 20 pins handicap

player.set_handicap(season, handicap)
print(player.get_handicap(season))  # Handicap(20.0)
```

### Creating Game Result with Handicap

```python
from domain.value_objects import Score, Points, GameResult, Handicap

scratch_score = Score(180)
handicap = Handicap(20.0)
points = Points(2.0)

result = GameResult(
    player_id=player.id,
    position=1,
    scratch_score=scratch_score,
    points=points,
    handicap=handicap
)

print(result.scratch_score)      # Score(180)
print(result.handicap_score)     # Score(200.0)
print(result.has_handicap())     # True
```

### Updating Handicap During Season

```python
# Initial handicap
player.set_handicap(season, Handicap(20.0))

# Update handicap mid-season (e.g., after recalculating average)
player.set_handicap(season, Handicap(25.0))  # Handicap increased

print(player.get_handicap(season))  # Handicap(25.0)
```

---

## Business Rules

1. **Handicap is Optional:**
   - Not all leagues/tournaments use handicap
   - Players may not have handicap set
   - GameResult can be created without handicap

2. **Handicap Can Change:**
   - Handicap is tracked per season
   - Can be updated during the season
   - Updates affect future games, not past games

3. **Scratch vs Handicap Scores:**
   - Scratch score = actual pins knocked down
   - Handicap score = scratch score + handicap
   - Both are tracked in GameResult

4. **Handicap Application:**
   - Handicap is applied when creating GameResult
   - Handicap can push score above 300 (perfect game)
   - Some leagues cap handicap scores at 300 (not implemented yet)

---

## Future Enhancements

1. **Handicap Calculation:**
   - Create `HandicapCalculator` domain service
   - Calculate handicap based on player average
   - Support different handicap formulas (e.g., 90% of difference from 200)

2. **Handicap Capping:**
   - Add option to cap handicap scores at 300
   - Configurable per league/tournament

3. **Handicap History:**
   - Track handicap changes over time
   - Show handicap progression during season

4. **League/Tournament Handicap Settings:**
   - Add handicap configuration to League entity
   - Enable/disable handicap per league
   - Set maximum handicap per league

---

## Testing

All handicap functionality has been tested:
- ✅ Handicap value object validation
- ✅ Handicap application to scores
- ✅ Player handicap tracking per season
- ✅ GameResult with handicap
- ✅ Backward compatibility with existing code

