import os
import pandas as pd
from sanic.log import logger

from dataplay.datasvc.base import BaseDataset
from dataplay.datasvc.constant import CSV_DATASET_PATH


class CSV(BaseDataset):
    def __init__(self, id, name, content, description):
        BaseDataset.__init__(self, id, name, content, description)
        self.file = content
        self.path = os.path.join(CSV_DATASET_PATH, self.file)

    def _load(self):
        logger.debug(f'load csv from {self.path}')
        self.df = pd.read_csv(self.path)
        logger.debug(f'load csv from {self.path} success')

    # Here I also want to change the logic of saving DataSet so as to save it in mongodb
    def save(self):
        if self.df is None:
            self._load()
        file_name = f'{self.id}.csv'
        file_path = os.path.join(CSV_DATASET_PATH, file_name)
        self.df.to_csv(file_path)

    def delete(self):
        file_name = f'{self.id}.csv'
        file_path = os.path.join(CSV_DATASET_PATH, file_name)
        os.remove(file_path)
