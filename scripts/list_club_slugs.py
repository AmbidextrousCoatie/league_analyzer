"""
List all club slugs for debugging slug-based routes.

Run with (PowerShell):
    & 'C:\Users\cfell\python_venvs\league_analyzer\Scripts\Activate.ps1'
    python scripts/list_club_slugs.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from presentation.api.v1.queries.slug_utils import slugify

# Load clubs
club_csv = project_root / "sample_data" / "relational_csv" / "club.csv"
if not club_csv.exists():
    print(f"Error: Club CSV not found at {club_csv}")
    sys.exit(1)

df_clubs = pd.read_csv(club_csv)

print("=" * 70)
print("Club Names and Their Slugs")
print("=" * 70)
print()

for _, row in df_clubs.iterrows():
    club_name = str(row['name']).strip()
    club_slug = slugify(club_name)
    print(f"  {club_name:40} -> {club_slug}")

print()
print("=" * 70)
print("Example URLs:")
print("=" * 70)
print()

# Show first few examples
for i, row in df_clubs.head(5).iterrows():
    club_name = str(row['name']).strip()
    club_slug = slugify(club_name)
    print(f"  /clubs/{club_slug}/teams/1/seasons/2025-26/score-sheet/view")
