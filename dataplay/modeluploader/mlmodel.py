from datetime import datetime
import pandas as pd
from umongo import Instance,Document,fields,validate
from dataplay.utils.mongodbDML import MongodbUtils

db_connection = MongodbUtils.getdbClient()
db = db_connection.inmotion
instance = Instance(db)

#  here we design model for machine learning model
@instance.register
class MLmodel(Document):
    #
    description = fields.StringField(required=True)  # to remember the functionality of the pkl file
    filename = fields.StringField(required=True)  # plk file name
    path = fields.StringField(required=True)  # path of the plk file
    version = fields.StringField(required=True)  # plk file version
    department = fields.StringField(required=True) # assign the model to department
    team = fields.StringField(required=True) # assign the model to team
    features = fields.StringField(required=True) # features have to be assigned
    name = fields.StringField(required=True)  # model name
    isDeployed = fields.BooleanField(required=True,default=False)
    createDate = fields.DateTimeField(validate=validate.Range(min=pd.Timestamp(1990,1,1)),required=True)
    updateDate = fields.DateTimeField(validate=validate.Range(min=pd.Timestamp(1990,1,1)),required=True)
    class Meta():
        collection = db.mlmodel