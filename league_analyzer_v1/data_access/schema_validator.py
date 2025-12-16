import json
from typing import Dict, Any, List

import pandas as pd


def load_schema(schema_path: str) -> Dict[str, Any]:

	with open(schema_path, "r", encoding="utf-8") as f:
		return json.load(f)


def get_table_spec(schema: Dict[str, Any], table_name: str) -> Dict[str, Any]:

	tables = {t["name"]: t for t in schema.get("tables", [])}
	if table_name not in tables:
		raise KeyError(f"Table not found in schema: {table_name}")
	return tables[table_name]


def validate_dataframe_against_schema(df: pd.DataFrame, table_spec: Dict[str, Any]) -> List[str]:

	errors: List[str] = []
	cols_spec = {c["name"]: c for c in table_spec.get("columns", [])}

	# Required columns exist
	for col_name, col in cols_spec.items():
		if not col.get("nullable", True) and col_name not in df.columns:
			errors.append(f"Missing required column '{col_name}'")

	# Nullability
	for col_name, col in cols_spec.items():
		if col_name in df.columns and not col.get("nullable", True):
			if df[col_name].isna().any():
				errors.append(f"Column '{col_name}' contains NULLs but is not nullable")

	# Primary key uniqueness
	pk_cols = [c["name"] for c in table_spec.get("columns", []) if c.get("pk")]
	if pk_cols:
		if df[pk_cols].duplicated().any():
			errors.append(f"Primary key duplicate detected on columns {pk_cols}")

	# Unique constraints
	for uniq in table_spec.get("unique", []):
		if all(c in df.columns for c in uniq):
			if df[uniq].duplicated().any():
				errors.append(f"Unique constraint violation on columns {uniq}")

	return errors


def coerce_dtypes(df: pd.DataFrame, table_spec: Dict[str, Any]) -> pd.DataFrame:

	result = df.copy()
	for col in table_spec.get("columns", []):
		name = col["name"]
		type_name = col.get("type", "string")
		if name not in result.columns:
			continue
		if type_name == "integer":
			result[name] = pd.to_numeric(result[name], errors="coerce").astype("Int64")
		elif type_name == "number":
			result[name] = pd.to_numeric(result[name], errors="coerce")
		elif type_name == "boolean":
			result[name] = result[name].astype("boolean")
		elif type_name in ("date", "datetime"):
			result[name] = pd.to_datetime(result[name], errors="coerce").dt.date
		else:
			result[name] = result[name].astype("string")
	return result


def get_ordered_column_names(table_spec: Dict[str, Any]) -> List[str]:

	return [c["name"] for c in table_spec.get("columns", [])]


def ensure_schema_columns(df: pd.DataFrame, table_spec: Dict[str, Any]) -> pd.DataFrame:

	result = df.copy()
	ordered_cols = get_ordered_column_names(table_spec)
	for col in ordered_cols:
		if col not in result.columns:
			result[col] = pd.NA
	# Reorder columns to match schema
	result = result[ordered_cols]
	return result


