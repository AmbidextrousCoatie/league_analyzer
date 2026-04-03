# Input to Legacy CSV Mapping

This document maps the current input format in `league_analyzer_v1/database/input` to the legacy flat format used by `league_analyzer_v1/database/data/bowling_ergebnisse_real.csv`.

## Context Notes

- Redundant validation records exist in the source feed (for example `BAYL-M-###_Re` and `BAYL-M-###_Li`) and represent team/opponent perspectives of the same game.
- The current input does not contain all fields required for a perfect legacy reconstruction.
- `Location` is not available in the current input and is intentionally skipped for now.

## Target Legacy Columns

`Season;Week;Date;League;Players per Team;Location;Round Number;Match Number;Team;Position;Player;Player ID;Opponent;Score;Points;Input Data;Computed Data`

## Mapping Table

| Legacy column | Input source | 1:1 mapping | Comment |
|---|---|---:|---|
| `Season` | Not present | False | Not delivered by input. For now use fixed default `25/26`. |
| `Week` | `Spiel-ID` | False | Derived from first digit of encoded game triple in `Spiel-ID` (`W##` logic). Not a direct field copy. |
| `Date` | `Datum des Eintrags` / `Aktualisierungsdatum` | False | Use the **smallest timestamp** associated with each `(League, Week)` bucket as canonical date for all results in that bucket; then format as date. |
| `League` | `Spiel-ID` / `Game-ID` prefix | False | Derived from code prefix and mapped to `league.csv` IDs. Active mapping: `BAYL-M -> BayL`, `LL-S-M -> LL S`, `LL-S-F -> LL S (D)`, `KRL-S1 -> KL S1`, `KRL-N2 -> KL N2`, `BZOL-N2 -> BZOL N2`, `BZOL-N1 -> BZOL N1`. |
| `Players per Team` | Not present (implicit in schema) | False | Use default constant `4`. |
| `Location` | Not present | False | Not delivered in input. Skip (leave empty) for now. |
| `Round Number` | `Spiel-ID` | False | Derived from second digit of encoded game triple in `Spiel-ID`. Not a direct field copy. |
| `Match Number` | `Spiel-ID` | False | Derived from third digit of encoded game triple in `Spiel-ID`. Not a direct field copy. |
| `Team` | `Teamname` | True | Direct team name mapping. |
| `Position` | Player slot columns (`Spieler 1..4`) | False | Must be generated from slot index (legacy uses lineup position values). |
| `Player` | `Spieler 1..4` | True | Direct player name values from each slot; output row expansion required (4 rows per team per game before team-total row). |
| `Player ID` | `EDV 1..4` | True | Direct player ID mapping per slot. |
| `Opponent` | `Gegner` | True | Direct opponent team mapping. |
| `Score` | `Pins 1..4` and `Pins Gesamt` | False | Player-row score comes from `Pins n`; team-total row score comes from `Pins Gesamt`. Requires row expansion and aggregation logic. |
| `Points` | `Pins n`, `Pins Gegner n`, `Pins Gesamt`, `Pins Gegner` | False | Must be calculated with standard league logic (individual matchup points + team-total points). |
| `Input Data` | Not present | False | Generated flag: player rows `True`, team-total row `False` (legacy convention). |
| `Computed Data` | Not present | False | Generated flag: player rows `False`, team-total row `True` (legacy convention). |

## Duplicate/Validation Handling (`_Re` / `_Li`)

| Topic | Rule | 1:1 mapping | Comment |
|---|---|---:|---|
| Duplicate perspective records | Detect by base game key (for example `BAYL-M-###`) and keep one canonical side | False | `_Re` and `_Li` are validation-redundant perspectives of the same game; conversion should deduplicate to avoid double counting. |
| Canonical record selection | Prefer earliest stable record or deterministic tie-breaker | False | Input does not provide explicit "canonical" flag; converter must apply a deterministic policy. |

## Known Gaps

- No explicit `Season` field in input.
- No explicit `Location` field in input.
- Several legacy fields are derivations rather than direct mappings.
