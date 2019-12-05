import os
from dataplay.confsvc.manager import ConfigurationManager


server_config = ConfigurationManager.get_confs('server')
filepath = server_config.get('server', 'datasetPath')

# CSV_DATASET_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dataset', 'csv')

CSV_DATASET_PATH = filepath
QUERY_TYPE_NORMAL = 'query'
QUERY_TYPE_SQL = 'sql'
QUERY_TYPES = [QUERY_TYPE_NORMAL, QUERY_TYPE_SQL]
