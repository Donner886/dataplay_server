from datetime import datetime
import pandas as pd
from umongo import Instance, Document, fields, validate
from dataplay.utils.mongodbDML import MongodbUtils

db_connection = MongodbUtils.getdbClient()
db = db_connection.inmotion
instance = Instance(db)



@instance.register
class DataSets(Document):
    description = fields.StringField(required=True)  # to remember the description of the dataset
    dataSetName = fields.StringField(required=True)  # dataset name
    department = fields.StringField(required=True)  # assign the dataset to department
    team = fields.StringField(required=True)  # assign the dateset to team
    createDate = fields.DateTimeField(validate=validate.Range(min=pd.Timestamp(1990, 1, 1)), required=True)
    updateDate = fields.DateTimeField(validate=validate.Range(min=pd.Timestamp(1990, 1, 1)), required=True)
    class Meta():
        collection = db.dataset
