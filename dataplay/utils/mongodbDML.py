from dataplay.confsvc.manager import ConfigurationManager
from pymongo import MongoClient
import numpy as np


class MongodbUtils:
    @staticmethod
    def getdbClient():
        dbconf = ConfigurationManager.get_confs('database')
        for section in dbconf.sections():
            if section == 'mongodb':
                host = dbconf.get(section,'host')
                port = np.int(dbconf.get(section,'port'))
        return MongoClient(host,port)


class RedisUtils:
    @staticmethod
    def getPoolConfig():
        dbconf = ConfigurationManager.get_confs('database')
        for section in dbconf.sections():
            if section == 'redis':
                host = dbconf.get(section, 'host')
                port = np.int(dbconf.get(section, 'port'))
        return {'host': host, 'port': port}


