# API URLs

This document provides working URLs for the preliminary frontend endpoints.

## Slug-Based Routes (Human-Readable) ⭐ Recommended

Slug-based routes use human-readable identifiers instead of UUIDs, making URLs shareable and SEO-friendly.

### League Standings (Slug-Based)

#### JSON Response
```
http://localhost:5000/leagues/bayl/standings?season=2025-26
http://localhost:5000/leagues/bayl/standings?season=25/26
```

#### HTML View (All Weeks)
```
http://localhost:5000/leagues/bayl/standings/view?season=2025-26
http://localhost:5000/leagues/bayl/standings/view?season=25/26
```

#### HTML View (Specific Week)
```
http://localhost:5000/leagues/bayl/standings/view?season=2025-26&week=1
http://localhost:5000/leagues/bayl/standings/view?season=25/26&week=2
```

### Team Score Sheet (Slug-Based)

#### JSON Response (All Weeks)
```
http://localhost:5000/clubs/bk-muenchen/teams/1/seasons/2025-26/score-sheet
http://localhost:5000/clubs/bc-comet-nurnberg/teams/1/seasons/25/26/score-sheet
```

#### JSON Response (Specific Week)
```
http://localhost:5000/clubs/bk-muenchen/teams/1/seasons/2025-26/score-sheet?week=1
http://localhost:5000/clubs/bc-comet-nurnberg/teams/1/seasons/25/26/score-sheet?week=2
```

#### HTML View (All Weeks)
```
http://localhost:5000/clubs/bk-muenchen/teams/1/seasons/2025-26/score-sheet/view
http://localhost:5000/clubs/bc-comet-nurnberg/teams/1/seasons/25/26/score-sheet/view
```

#### HTML View (Specific Week)
```
http://localhost:5000/clubs/bk-muenchen/teams/1/seasons/2025-26/score-sheet/view?week=1
http://localhost:5000/clubs/bc-comet-nurnberg/teams/1/seasons/25/26/score-sheet/view?week=2
```

**Note:** Club slugs are generated from club names with German umlaut handling:
- "BK München" → "bk-muenchen" (ü → ue)
- "BC Comet Nürnberg" → "bc-comet-nurnberg" (ü → ue)
- "BC EMAX Unterföhring" → "bc-emax-unterfoehring" (ö → oe)

If a slug is not found, the error message will show all available club slugs.

---

## UUID-Based Routes (Legacy)

UUID-based routes are still available for backward compatibility but are not recommended for new integrations.

## Sample Data IDs

### League
- **BayL (Bayernliga)**: `51af5c14-b721-4497-b028-c6f9a934bce3`

### League Season
- **BayL 2025-26**: `45f09c89-2e88-4073-a191-5633d7b314dd`

### Team Seasons (BayL 2025-26)
- Team 1: `295ca7c4-3450-4f97-aea0-c811e45f7f79`
- Team 2: `55a1a7b5-1768-4b2d-9193-439b8139b14b`
- Team 3: `0afd86bf-97d5-4960-b681-6821e4eaf564`
- Team 4: `ec2ad0a2-fae9-41ae-a1f2-6f0f9f40988d`
- Team 5: `c341fbda-39c1-440d-9a32-868cb1ffcee2`
- Team 6: `cc54de05-20d1-4cb5-b4f6-c4042f0bb61f`
- Team 7: `fd27f71f-a5fb-4724-a46b-f819d2e1513a`
- Team 8: `522a5f43-635f-47e3-a9bf-4e7de12c3158`
- Team 9: `e8f55104-aacd-4895-a45a-658b40fe2430`
- Team 10: `f393c019-25c2-4eef-a04d-31b9efa55521`

## League Standings URLs

### JSON Response
```
http://localhost:5000/api/v1/leagues/51af5c14-b721-4497-b028-c6f9a934bce3/standings?league_season_id=45f09c89-2e88-4073-a191-5633d7b314dd
```

### HTML View (All Weeks)
```
http://localhost:5000/api/v1/leagues/51af5c14-b721-4497-b028-c6f9a934bce3/standings/view?league_season_id=45f09c89-2e88-4073-a191-5633d7b314dd
```

### HTML View (Specific Week)
```
http://localhost:5000/api/v1/leagues/51af5c14-b721-4497-b028-c6f9a934bce3/standings/view?league_season_id=45f09c89-2e88-4073-a191-5633d7b314dd&week=1
http://localhost:5000/api/v1/leagues/51af5c14-b721-4497-b028-c6f9a934bce3/standings/view?league_season_id=45f09c89-2e88-4073-a191-5633d7b314dd&week=2
```

## Team Score Sheet URLs

### JSON Response (All Weeks)
```
http://localhost:5000/api/v1/teams/295ca7c4-3450-4f97-aea0-c811e45f7f79/score-sheet
```

### JSON Response (Specific Week)
```
http://localhost:5000/api/v1/teams/295ca7c4-3450-4f97-aea0-c811e45f7f79/score-sheet?week=1
http://localhost:5000/api/v1/teams/295ca7c4-3450-4f97-aea0-c811e45f7f79/score-sheet?week=2
```

### HTML View (All Weeks)
```
http://localhost:5000/api/v1/teams/295ca7c4-3450-4f97-aea0-c811e45f7f79/score-sheet/view
```

### HTML View (Specific Week)
```
http://localhost:5000/api/v1/teams/295ca7c4-3450-4f97-aea0-c811e45f7f79/score-sheet/view?week=1
http://localhost:5000/api/v1/teams/295ca7c4-3450-4f97-aea0-c811e45f7f79/score-sheet/view?week=2
```

## Other Team Score Sheets

Replace `{team_season_id}` with any of the team season IDs listed above:

```
http://localhost:5000/api/v1/teams/{team_season_id}/score-sheet
http://localhost:5000/api/v1/teams/{team_season_id}/score-sheet/view
http://localhost:5000/api/v1/teams/{team_season_id}/score-sheet?week=1
http://localhost:5000/api/v1/teams/{team_season_id}/score-sheet/view?week=1
```

## Notes

- All IDs are UUIDs from the `sample_data/relational_csv/` directory
- The `league_season_id` parameter is optional for both endpoints:
  - For league standings: if not provided, uses the latest league season for the league
  - For team score sheet: if not provided, derived from the team_season_id
- The `week` parameter is optional for both endpoints (None = all weeks)
- If an invalid ID is provided, the handler should return a proper error message (robustness improvement pending)

## Troubleshooting

### League Standings Showing Zeros

If the league standings show correct team names but all values are 0, this likely means:

1. **Data needs to be regenerated**: After updating the seed script (to derive matches from Team/Opponent instead of match_number), you need to regenerate the sample data:
   ```bash
   python scripts/seed_sample_data.py
   ```
   This will regenerate all match data using the new Team/Opponent pairing logic.

2. **No matches found**: The handler will now return empty standings gracefully if no events or matches are found, rather than crashing.

### Team Score Sheet Missing league_season_id

The `league_season_id` parameter is now **optional** for team score sheet endpoints. If not provided, it will be automatically derived from the `team_season_id`.
