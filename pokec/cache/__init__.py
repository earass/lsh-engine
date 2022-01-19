import pandas as pd
import os
import logging

directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'files'))


class Cache:

    def __init__(self, pre_cleaning=True):
        if not os.path.exists(directory):
            os.makedirs(directory)
        if pre_cleaning:
            self.status_tag = "(Before Cleaning)"
        else:
            self.status_tag = "(After Cleaning)"

    def save_df_as_parquet(self, df, file_name):
        path = f'{directory}/{file_name}_{self.status_tag}.parquet'
        df.to_parquet(path)

    def read_parquet_df(self, filename, columns=None):
        df = pd.read_parquet(f'{directory}/{filename}_{self.status_tag}.parquet', "pyarrow", columns=columns)
        return df

    @staticmethod
    def export_df_as_csv(df, file_name):
        file_path = f'{directory}/{file_name}.csv'
        df.to_csv(file_path, index=False)
        logging.info(f"File saved on path: {file_path}")
