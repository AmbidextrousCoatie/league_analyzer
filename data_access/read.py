import pandas as pd
from data_access.schema import Columns

def read(data_df: pd.DataFrame, columns: list[Columns] | Columns | None = None, filters: dict[Columns, list[str]]=None, unique: bool=False, as_list: bool=False):
    """Reads and filters data from a DataFrame, returning results in simple Python data types.

    Args:
        data_df (pd.DataFrame): Input DataFrame to read from.
        columns (list[str] | str | None, optional): Column name(s) to extract. Can be a single string, list of strings,
            or None to select all columns. Defaults to None.
        filters (dict[str, list[str]], optional): Dictionary of filters to apply, where keys are column names
            and values are lists of acceptable values. Defaults to None.
        unique (bool, optional): If True, removes duplicate rows from the result. Defaults to False.
        as_list (bool, optional): Controls output format. If True, returns Python lists/dicts. 
            If False, returns pandas DataFrame. Defaults to True.

    Returns:
        Union[list, list[dict], pd.DataFrame]: Depending on the parameters:
            - If as_list=True and single column: returns list of values
            - If as_list=True and multiple columns: returns list of dictionaries
            - If as_list=False: returns pandas DataFrame

    Examples:
        >>> df = pd.DataFrame({'A': [1, 2, 2, 3], 'B': ['x', 'y', 'y', 'z']})
        >>> read(df, 'A')
        [1, 2, 2, 3]
        
        >>> read(df, 'A', unique=True)
        [1, 2, 3]
        
        >>> read(df, ['A', 'B'], filters={'A': [2, 3]})
        [{'A': 2, 'B': 'y'}, {'A': 2, 'B': 'y'}, {'A': 3, 'B': 'z'}]
        
        >>> read(df, ['A', 'B'], as_list=False)
           A  B
        0  1  x
        1  2  y
        2  2  y
        3  3  z
    """
    if filters is None:
        filters = {}

    if columns is None:
        columns = data_df.columns.tolist()
    elif not isinstance(columns, list):
        columns = [columns]

    for key, value in filters.items():
        if value is None:
            continue
        if not isinstance(value, list):
            value = [value]
        data_df = data_df[data_df[key].isin(value)]

    result_df = data_df[columns].drop_duplicates() if unique else data_df[columns]
    
    if as_list:
        if len(columns) == 1:
            return result_df[columns[0]].tolist()
        return result_df.to_dict('records')
    return result_df
    
