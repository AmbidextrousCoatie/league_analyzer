import pandas as pd
from typing import Union, List, Optional

def fetch_data(
    database_df: pd.DataFrame, 
    columns_to_fetch: Union[str, List[str], None] = None, 
    values_to_filter_for: dict = None,
    group_by: Union[str, List[str], None] = None

) -> pd.DataFrame:
    """
    Creates a new DataFrame with requested rows and columns
    
    Args:
        database_df: Source DataFrame
        columns: Single column name or list of column names to fetch
        filters: Dictionary of {column: [values]} to filter rows
    
    Returns:
        New DataFrame containing only requested data
    """
    # Create boolean mask for row filtering
    mask = pd.Series(True, index=database_df.index)
    if values_to_filter_for:
        for filter_col, values in values_to_filter_for.items():
            if values not in [None,[], [None]]:
                values = [values] if not isinstance(values, List) else values
                mask &= database_df[filter_col].isin(values)
    
    database_fetched = 0

    # Handle column selection
    if columns_to_fetch is not None:
        # Convert single column to list
        selected_columns = [columns_to_fetch] if not isinstance(columns_to_fetch, List) else columns_to_fetch
        # Ensure all filter columns are included if needed for the operation
        if group_by is not None:
            selected_columns = list(set(selected_columns + [group_by]))
        #    filter_cols = list(values_to_filter_for.keys())
        #    selected_columns = list(set(selected_columns + filter_cols))
        
        # Return selected rows and columns
        database_fetched = database_df.loc[mask, selected_columns].copy()
    else:
        # Return all columns for selected rows
        database_fetched = database_df.loc[mask].copy() 
    
    if group_by is not None:
        database_fetched = database_fetched.groupby(group_by)

    return database_fetched

def filter_data(
    database_df: pd.DataFrame, 
    columns: Union[str, List[str], None] = None, 
    filters: dict = None,
) -> None:
    """
    Modifies DataFrame in place using filters and column selection
    
    Args:
        database_df: DataFrame to modify
        columns: Single column name or list of column names to keep
        filters: Dictionary of {column: [values]} to filter rows
    """
    # Apply row filters first
    if filters:
        for filter_col, values in filters.items():
            if values is not None:
                database_df.query(f"{filter_col} in @values", inplace=True)
    
    # Then select columns if specified
    if columns is not None:
        # Convert single column to list
        selected_columns = [columns] if isinstance(columns, str) else columns
        # Drop columns not in the selection
        to_drop = [col for col in database_df.columns if col not in selected_columns]
        database_df.drop(columns=to_drop, inplace=True)


def fetch_column(database_df: pd.DataFrame, column_name: str, filters: dict = None, unique: bool = False, as_list: bool = False, group_by: str = None):
    fetched_data = fetch_data(database_df, columns_to_fetch=column_name, values_to_filter_for=filters, group_by=group_by)
    if unique:
        fetched_data = fetched_data.drop_duplicates()
    if as_list:
        fetched_data = fetched_data[column_name].tolist()
    return fetched_data
