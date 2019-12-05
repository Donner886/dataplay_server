from datetime import datetime
import pandas as pd
from umongo import Instance,Document,fields,validate
from dataplay.utils.mongodbDML import MongodbUtils

db_connection = MongodbUtils.getdbClient()
db = db_connection.inmotion
instance = Instance(db)

@instance.register
class User(Document):
    #
    name = fields.StringField(required=True)
    department = fields.StringField(required=True)
    team = fields.StringField(required=True)
    createDate = fields.DateTimeField(validate=validate.Range(min=pd.Timestamp(1990,1,1)),required=True)
    updateDate = fields.DateTimeField(validate=validate.Range(min=pd.Timestamp(1990,1,1)),required=True)
    accountRef = fields.StringField(required=True)
    class Meta():
        collection = db.user




@instance.register
class Account(Document):
    #
    username = fields.StringField(required=True)
    password = fields.StringField(required=True)
    createDate = fields.DateTimeField(validate=validate.Range(min=datetime(1990,1,1)),required=True)
    updateDate = fields.DateTimeField(validate=validate.Range(min=datetime(1990,1,1)),required=True)

    class Meta():
        collection = db.account
