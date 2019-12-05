from dataplay.utils.mongodbDML import MongodbUtils
import json
import numpy as np
import pandas as pd

class DataSet:

    def __init__(self):
        self.db_client = MongodbUtils.getdbClient()
        self.db = self.db_client.inmotion

    def saveDocuments(self, connection, documents=[]):
        results = self.db[connection].insert_many(documents)
        return results

    def getConnection(self,connection):
        results = self.db[connection].find({},{'_id':False})
        return results

    def getConnectionByCondition(self,connection,timeRange,startTime,endTime):
        results = self.db[connection].find({}, {'_id': False})
        contain = []
        for result in results:
            contain.append(result)
        df = pd.DataFrame(contain)
        df[timeRange] = pd.to_datetime(df[timeRange])
        startTime = pd.Timestamp(startTime)
        endTime = pd.Timestamp(endTime)
        subset = df[(df[timeRange] > startTime) & (df[timeRange] < endTime) ]
        return { 'message': 'got dataset you wanted','result':subset , 'status': True}

    def getConnectionPredictedByCondition(self,connection,startTime,endTime):
        results = self.db[connection].find({'$and':[{'index':{'$gt':startTime}},{'index':{'$lt':endTime}}]}, {'_id': False})
        container = []
        for result in results:
            container.append(result)
        return container
