# Test Data Errors Summary

This file (`bowling_ergebnisse_test_errors.csv`) contains intentional errors for testing the validation script.

## League: BZL N2, Season 25/26, Week 1
- **Number of teams**: 6 (should be: Albrecht Dürer 71 Stein 1, RW Lichtenhof 69 Stein 4, Donaubowler Regensburg 3, Kings Club Bayreuth Land 2, Eintracht Lauf 3, Gute Laune Lauf 2)
- **Players per team**: 4
- **Scoring system**: liga_bayern_3pt (1 point per individual win, 3 points per team win)

## Errors Included:

### 1. Multiple Players at Same Position
- **Round 3, Position 3**: Test Player 3 (ID: 99903) appears at both position 2 and position 3 for team "Albrecht Dürer 71 Stein 1" in the match against "Eintracht Lauf 3"
- **Round 6, Position 3**: Test Player 1 (ID: 99901) appears at both position 0 and position 3 for team "Albrecht Dürer 71 Stein 1" in the match against "RW Lichtenhof 69 Stein 4"

### 2. Match Points Sum Error
- **Round 3, Match: Donaubowler Regensburg 3 vs RW Lichtenhof 69 Stein 4**
  - Expected total points: 4 individual matches × (1 win + 0 loss) + 1 team match × (3 win + 0 loss) = 4 + 3 = 7
  - Actual total points: 4 individual wins (4 points) + 10.0 team points = 14.0
  - Error: Team points are 10.0 instead of 3.0

### 3. Round Match Count Error
- **Round 6**: Contains 4 matches instead of 3
  - Expected: 6 teams / 2 = 3 matches
  - Actual: 4 matches (includes duplicate match between RW Lichtenhof 69 Stein 4 and Donaubowler Regensburg 3)

### 4. Player-Team Association Errors
- All test players (IDs 99901-99924) are not associated with any teams in the `game_result_new.csv` table
- This will cause the player-team association check to fail for all players
- Note: This is expected since these are synthetic test players

### 5. Missing Teams (Potential)
- Round 7 has all 6 teams present
- For a true missing teams error, one team should be absent from a round
- This can be tested by removing one team's data from a specific round

## Expected Validation Results:

When running the validation script on this file, you should see:
- ✅ `one_player_per_position`: 2 issues (Round 3 and Round 6)
- ✅ `match_points_sum`: 1 issue (Round 3, Donaubowler vs RW Lichtenhof)
- ✅ `round_points_sum`: 1 issue (Round 6 has 4 matches instead of 3)
- ✅ `player_team_association`: Multiple issues (all test players)
- ⚠️ `all_teams_present`: May pass if all teams appear in at least one round
- ⚠️ `week_points_sum`: May pass depending on round structure

## Usage:

```bash
# Run validation on test file
python data_access/validate_data.py --source test_with_errors

# Or use custom file path
python data_access/validate_data.py --file database/data/bowling_ergebnisse_test_errors.csv

# Run only specific checks
python data_access/validate_data.py --source test_with_errors --disable-all-teams --disable-week-points
```

