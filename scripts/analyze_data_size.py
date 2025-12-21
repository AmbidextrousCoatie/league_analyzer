"""Analyze current CSV data size and estimate future growth."""
import pandas as pd
from pathlib import Path

base = Path('league_analyzer_v1/database/relational_csv')
files = [
    'event.csv',
    'new/game_result_new.csv',
    'player.csv',
    'team_season.csv',
    'league_season.csv',
    'club.csv',
    'venue.csv'
]

total_rows = 0
total_size = 0

print("Current Data Analysis:\n")
print(f"{'File':<30} {'Rows':>8} {'Size (KB)':>12} {'Size (MB)':>12}")
print("-" * 65)

for f in files:
    p = base / f
    if p.exists():
        df = pd.read_csv(p)
        rows = len(df)
        size = p.stat().st_size
        total_rows += rows
        total_size += size
        print(f"{f:<30} {rows:>8} {size/1024:>12.2f} {size/1024/1024:>12.2f}")

print("-" * 65)
print(f"{'TOTAL':<30} {total_rows:>8} {total_size/1024:>12.2f} {total_size/1024/1024:>12.2f}")

print("\n" + "=" * 65)
print("Future Growth Estimates:")
print("=" * 65)
print(f"Current data: ~{total_size/1024:.2f} KB ({total_size/1024/1024:.2f} MB)")
print(f"Current represents: 5-10% of per-season data")
print(f"\nEstimated per-season: ~{total_size/1024*10:.2f} KB - {total_size/1024*20:.2f} KB")
print(f"Estimated per-season: ~{total_size/1024/1024*10:.2f} MB - {total_size/1024/1024*20:.2f} MB")

legacy_seasons = 10
future_years = 10
total_seasons = legacy_seasons + future_years

print(f"\nLegacy seasons to add: {legacy_seasons}")
print(f"Future years: {future_years}")
print(f"Total seasons: {total_seasons}")

estimated_total = total_size * 200  # 200x current
print(f"\nEstimated total (200x): ~{estimated_total/1024:.2f} KB ({estimated_total/1024/1024:.2f} MB)")

