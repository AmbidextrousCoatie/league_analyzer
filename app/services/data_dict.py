from typing import List


class DataDict:
    def __init__(self):
        self.data = {}

    def transform_dict(self, data_dict):
        self.data = {
            'headerGroups': [
                {'title': group[0], 'colspan': group[1]} 
                for group in data_dict['headerGroups']
            ],
            'columns': [
                {'title': col, 'key': str(i)} 
                for i, col in enumerate(data_dict['columns'])
            ],
            'data': [
                {str(i): value for i, value in enumerate(row)}
                for row in data_dict['data']
            ],
            'rowNumbering': True
        }
        return self.data

    def add_data(self, key, value):
        self.data[key] = value

    def make_sortable(self, columns_to_make_sortable):
        
        if not isinstance(columns_to_make_sortable, list):
            columns_to_make_sortable = [columns_to_make_sortable]

        for column in columns_to_make_sortable:
            if isinstance(column, str):
                print("need to find column : " + str(column))
                
            if isinstance(column, int):
                print("can directly set column : " + str(column) + " to sortable")
                self.data['columns'][column]['sortable'] = True

    def get_data(self, key):
        return self.data.get(key, None)