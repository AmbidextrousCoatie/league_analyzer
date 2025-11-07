"""
Compare input CSV with reconstructed CSV, ignoring row ordering.

This script loads both files, normalizes them, and reports differences.
"""

import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "database" / "data" / "bowling_ergebnisse_real.csv"
OUTPUT_CSV = ROOT / "database" / "data" / "bowling_ergebnisse_reconstructed.csv"


def normalize_dataframe(df: pd.DataFrame, name: str) -> pd.DataFrame:
	"""Normalize a DataFrame for comparison."""
	print(f"Normalizing {name}: {len(df)} rows, {len(df.columns)} columns")
	
	# Make a copy
	df = df.copy()
	
	# Define meaningful sort order (matching the original CSV structure)
	sort_columns = [
		"Season", "League", "Week", "Date", "Round Number", 
		"Team", "Position", "Player", "Player ID", "Opponent" #, "Match Number"
	]
	
	# Use only columns that exist in the DataFrame
	available_sort_cols = [col for col in sort_columns if col in df.columns]
	if not available_sort_cols:
		# Fallback: use all columns if none of the expected columns exist
		available_sort_cols = df.columns.tolist()
	
	# Sort by meaningful columns, handling numeric columns properly
	def numeric_sort_key(col_series):
		col_name = col_series.name
		if col_name in ["Week", "Round Number", "Match Number", "Position"]:
			return pd.to_numeric(col_series, errors="coerce").fillna(0)
		return col_series
	
	df = df.sort_values(
		by=available_sort_cols,
		key=numeric_sort_key
	).reset_index(drop=True)
	
	# Convert all columns to string for comparison (handles NaN and type differences)
	# Normalize numeric values: treat "0" and "0.0" as equivalent, "1" and "1.0" as equivalent, etc.
	for col in df.columns:
		df[col] = df[col].astype(str).replace('nan', '').replace('None', '')
		# Normalize numeric strings: convert "1.0" to "1", "0.0" to "0", etc.
		# But preserve non-numeric strings
		def normalize_numeric(val):
			if val == '':
				return val
			try:
				# Try to parse as float
				fval = float(val)
				# If it's a whole number, return as integer string
				if fval == int(fval):
					return str(int(fval))
				# Otherwise return with one decimal place
				return f"{fval:.1f}"
			except (ValueError, TypeError):
				# Not numeric, return as-is
				return val
		df[col] = df[col].apply(normalize_numeric)
	
	return df


def compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame, name1: str, name2: str) -> bool:
	"""Compare two DataFrames and report differences."""
	
	print(f"\n{'='*60}")
	print(f"Comparing {name1} vs {name2}")
	print(f"{'='*60}\n")
	
	# Check column differences
	cols1 = set(df1.columns)
	cols2 = set(df2.columns)
	
	if cols1 != cols2:
		only_in_1 = cols1 - cols2
		only_in_2 = cols2 - cols1
		print(f"Column differences:")
		if only_in_1:
			print(f"  Columns only in {name1}: {sorted(only_in_1)}")
		if only_in_2:
			print(f"  Columns only in {name2}: {sorted(only_in_2)}")
		print()
		# Use intersection of columns for comparison
		common_cols = sorted(cols1 & cols2)
		df1 = df1[common_cols]
		df2 = df2[common_cols]
	else:
		common_cols = sorted(cols1)
		print(f"Columns match: {len(common_cols)} columns")
	
	# Check row count
	len1, len2 = len(df1), len(df2)
	print(f"\nRow counts: {name1}={len1}, {name2}={len2}")
	
	if len1 != len2:
		print(f"  [WARN] Row count mismatch: {abs(len1 - len2)} rows difference")
	
	# Check for exact duplicates within each dataset
	dup1 = df1.duplicated().sum()
	dup2 = df2.duplicated().sum()
	if dup1 > 0:
		print(f"  [WARN] {name1} contains {dup1} duplicate rows")
	if dup2 > 0:
		print(f"  [WARN] {name2} contains {dup2} duplicate rows")
	
	# Compare row by row
	if len1 == len2:
		# Sort both by meaningful columns (same as normalization)
		sort_columns = [
			"Season", "League", "Week", "Date", "Round Number",
			"Team", "Position", "Player", "Player ID", "Opponent"
		]
		available_sort_cols = [col for col in sort_columns if col in common_cols]
		if not available_sort_cols:
			available_sort_cols = common_cols[:min(10, len(common_cols))]  # Use first 10 columns as fallback
		
		def numeric_sort_key(col_series):
			col_name = col_series.name
			if col_name in ["Week", "Round Number", "Position"]:
				return pd.to_numeric(col_series, errors="coerce").fillna(0)
			return col_series
		
		df1_sorted = df1.sort_values(
			by=available_sort_cols,
			key=numeric_sort_key
		).reset_index(drop=True)
		df2_sorted = df2.sort_values(
			by=available_sort_cols,
			key=numeric_sort_key
		).reset_index(drop=True)
		
		# Compare
		diffs = df1_sorted != df2_sorted
		
		if not diffs.any().any():
			print(f"\n[OK] DataFrames are identical!")
			return True
		else:
			print(f"\n[X] DataFrames differ!")
			
			# Count differences per column
			col_diffs = diffs.sum()
			print(f"\nDifferences per column:")
			for col in common_cols:
				count = col_diffs[col]
				if count > 0:
					print(f"  {col}: {count} differences ({count/len1*100:.1f}%)")
			
			# Show differences grouped by column (first 20 per column)
			print(f"\nDifferences by column (showing first 20 per column):")
			all_diffs = diffs[diffs.any(axis=1)]
			print(f"Total rows with differences: {len(all_diffs)}")
			
			if not all_diffs.empty:
				# Group differences by column
				for col in common_cols:
					col_mask = diffs[col]
					if col_mask.any():
						diff_indices = col_mask[col_mask].index[:20]  # First 20
						print(f"\n  Column '{col}' ({int(col_mask.sum())} total differences, showing first {min(20, len(diff_indices))}):")
						for idx in diff_indices:
							val1 = df1_sorted.loc[idx, col]
							val2 = df2_sorted.loc[idx, col]
							# Show context: Season, League, Week, Player for identification
							context_cols = ["Season", "League", "Week", "Player"]
							context = []
							for ctx_col in context_cols:
								if ctx_col in df1_sorted.columns:
									context.append(f"{ctx_col}={df1_sorted.loc[idx, ctx_col]}")
							context_str = ", ".join(context) if context else f"Row {idx}"
							print(f"    [{context_str}] '{val1}' vs '{val2}'")

			# Additionally, print first N rows with all differing columns for quick inspection
			print("\nSample of first 20 differing rows with all differing columns:")
			first_diff_indices = all_diffs.index[:20]
			for idx in first_diff_indices:
				row_diff_cols = [c for c in common_cols if diffs.loc[idx, c]]
				context_cols = ["Season", "League", "Week", "Date", "Round Number", "Match Number", "Team", "Player"]
				context = {c: df1_sorted.loc[idx, c] for c in context_cols if c in df1_sorted.columns}
				print(f"\n  Row {idx} context: {context}")
				for c in row_diff_cols:
					print(f"    {c}: '{df1_sorted.loc[idx, c]}' vs '{df2_sorted.loc[idx, c]}'")
			
			return False
	else:
		# Different row counts - find what's missing/extra
		print(f"\n[WARN] Cannot do row-by-row comparison due to different row counts")
		
		# Create a key for each row based on identifying columns
		key_cols = ["Season", "League", "Week", "Date", "Round Number", "Team", "Position", "Player", "Player ID"]
		available_key_cols = [col for col in key_cols if col in common_cols]
		
		# Create string keys for comparison
		df1["_row_key"] = df1[available_key_cols].apply(lambda x: "|".join(x.astype(str)), axis=1)
		df2["_row_key"] = df2[available_key_cols].apply(lambda x: "|".join(x.astype(str)), axis=1)
		
		# Count occurrences of each key
		df1_key_counts = df1["_row_key"].value_counts().to_dict()
		df2_key_counts = df2["_row_key"].value_counts().to_dict()
		
		all_keys = set(df1_key_counts.keys()) | set(df2_key_counts.keys())
		
		# Find keys with different counts
		only_in_1_keys = []
		only_in_2_keys = []
		different_count_keys = []
		
		for key in all_keys:
			count1 = df1_key_counts.get(key, 0)
			count2 = df2_key_counts.get(key, 0)
			if count1 == 0:
				only_in_2_keys.append(key)
			elif count2 == 0:
				only_in_1_keys.append(key)
			elif count1 != count2:
				different_count_keys.append((key, count1, count2))
		
		print(f"\nRows only in {name1}: {len(only_in_1_keys)}")
		if only_in_1_keys:
			only_in_1_rows = df1[df1["_row_key"].isin(only_in_1_keys)].drop(columns=["_row_key"]).drop_duplicates()
			print(f"  Showing all {len(only_in_1_rows)} unique rows:")
			for idx, row in only_in_1_rows.iterrows():
				row_dict = {col: row[col] for col in common_cols}
				print(f"    {row_dict}")
		
		print(f"\nRows only in {name2}: {len(only_in_2_keys)}")
		if only_in_2_keys:
			only_in_2_rows = df2[df2["_row_key"].isin(only_in_2_keys)].drop(columns=["_row_key"]).drop_duplicates()
			print(f"  Showing all {len(only_in_2_rows)} unique rows:")
			for idx, row in only_in_2_rows.iterrows():
				row_dict = {col: row[col] for col in common_cols}
				print(f"    {row_dict}")
		
		if different_count_keys:
			print(f"\nRows with different counts: {len(different_count_keys)}")
			for key, count1, count2 in different_count_keys[:10]:  # Show first 10
				print(f"  Key: {key[:100]}... (appears {count1} times in {name1}, {count2} times in {name2})")
				# Show all rows from both datasets
				rows1 = df1[df1["_row_key"] == key].drop(columns=["_row_key"])
				rows2 = df2[df2["_row_key"] == key].drop(columns=["_row_key"])
				
				if not rows1.empty:
					print(f"    All {len(rows1)} occurrence(s) from {name1}:")
					for idx, row in rows1.iterrows():
						row_dict = {col: row[col] for col in common_cols}
						print(f"      {row_dict}")
				
				if not rows2.empty:
					print(f"    All {len(rows2)} occurrence(s) from {name2}:")
					for idx, row in rows2.iterrows():
						row_dict = {col: row[col] for col in common_cols}
						print(f"      {row_dict}")
		
		# Clean up
		df1 = df1.drop(columns=["_row_key"])
		df2 = df2.drop(columns=["_row_key"])
		
		return False


def main():
	"""Main function."""
	
	if not INPUT_CSV.exists():
		print(f"Error: Input file not found: {INPUT_CSV}", file=sys.stderr)
		sys.exit(1)
	
	if not OUTPUT_CSV.exists():
		print(f"Error: Output file not found: {OUTPUT_CSV}", file=sys.stderr)
		sys.exit(1)
	
	print(f"Loading {INPUT_CSV.name}...")
	df_input = pd.read_csv(INPUT_CSV, sep=";", dtype=str, keep_default_na=False)
	
	print(f"Loading {OUTPUT_CSV.name}...")
	df_output = pd.read_csv(OUTPUT_CSV, sep=";", dtype=str, keep_default_na=False)
	
	# Normalize both DataFrames
	df_input_norm = normalize_dataframe(df_input, INPUT_CSV.name)
	df_output_norm = normalize_dataframe(df_output, OUTPUT_CSV.name)
	
	# Compare
	are_identical = compare_dataframes(
		df_input_norm,
		df_output_norm,
		INPUT_CSV.name,
		OUTPUT_CSV.name
	)
	
	if are_identical:
		print("\n" + "="*60)
		print("[OK] COMPARISON PASSED: Files are identical!")
		print("="*60)
		sys.exit(0)
	else:
		print("\n" + "="*60)
		print("[X] COMPARISON FAILED: Files differ!")
		print("="*60)
		sys.exit(1)


if __name__ == "__main__":
	main()

