This directory contains CSV exports for the pandas-emulated relational model.

Generated files
- venue.csv — distinct venues extracted from `database/data/bowling_ergebnisse_real.csv`.

How to regenerate
1) python -m data_access.build_relational_csv

Schema
- Defined in `database/schema.json`. Creator scripts coerce dtypes and validate basic constraints (PK, unique, nullability).


