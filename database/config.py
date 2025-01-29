import pathlib
import os

# Use os.path.join for cross-platform compatibility
path_to_csv_data = pathlib.Path(
    os.path.join(
        "database",
        "data",
        "bowling_ergebnisse.csv"
    )
).absolute()