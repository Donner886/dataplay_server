import json
from datetime import datetime
from dataplay.modeluploader.mlmodel import MLmodel
from umongo import Instance, Document, fields, validate
import pickle
from joblib import dump, load

class ModelService:

    @staticmethod
    def addModel(filename, path, description, department, team, version, features, name ,isDeployed):
        try:
            model = MLmodel(description=description, filename=filename, path=path, version=version,
                            department=department,features=features,
                            team=team, name=name, createDate=datetime.now(), updateDate=datetime.now(), isDeployed=isDeployed)
            model.commit()
            return {'result': model.pk, 'status': True}
        except:
            return {'result': 'Insert model description error', 'status': False}

    @staticmethod
    def findAllModels():
        try:
            modelContainers = [];
            models = MLmodel.find()
            for model in models:
                modelContainers.append(model.dump())
            return {'result': modelContainers, 'status': True}
        except:
            return {'result': 'Find models error', 'status': False}

    @staticmethod
    def updateStutusById(id, status):
        try:
            modelwrap = MLmodel.find({'_id': fields.ObjectId(id)})
            for model in modelwrap:
                model.isDeployed = status
                model.commit()
            return {'result': id, "status": True}
        except Exception:
            return {'result': 'Failed to updateStatus', 'status': False}

    @staticmethod
    def getModelById(id):
        try:
            modelwrap = MLmodel.find({'_id':fields.ObjectId(id)})
            modelContainers = []
            for model in modelwrap:
                if model.isDeployed:
                    modelContainers.append(model.dump())
            return modelContainers
        except Exception:
            return {'result': 'Failed to get model by id', 'status': False}





    @staticmethod
    def getModelsByDepartmentAndTeam(department, team):
        try:
            modelwrap = MLmodel.find({'department':department,'team':team})
            modelContainers = []
            for model in modelwrap:
                if model.isDeployed:
                    modelContainers.append(model.dump())
            return modelContainers
        except Exception:
            return {'result': 'Failed to get models beylond the user', 'status':False}


    @staticmethod
    def loadModel(id):
        modelwrap = MLmodel.find({'_id': fields.ObjectId(id)})
        for model in modelwrap:
            modelpath = model['path']
            modelname = model['filename']
        url = modelpath + modelname;
        clf = load(url)
        return clf



# if __name__ == '__main__':
#     model = ModelService.updateStutusById('5db7f95b2fcb81375085a047','ddd')
#     for m in model:
#         m.isDeployed = True
#         m.commit()
#         print(m)
