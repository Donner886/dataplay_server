from sanic import Blueprint
from sanic import response
from sanic.log import logger
from dataplay.modeluploader.modelservice import ModelService
from dataplay.confsvc.manager import ConfigurationManager
import os
from datetime import datetime

model_svc = Blueprint('model_svc')


@model_svc.get('/getAllModels', strict_slashes=True)
async def getAllModels(request):
    try:
        models = ModelService.findAllModels()
        return response.json({'message': 'successed to get all models', 'result': models['result']}, status=200)
    except Exception:
        logger.exception('faile to register the member')
        return response.json({'message': 'failed to register member'}, status=500)


@model_svc.post('/saveModel', strict_slashes=True)
async def saveModel(request):
    try:
        if 'content' in request.json.keys():
            filename = request.json['content']
        else:
            filename = 'Service with specific functionality'
        server_config = ConfigurationManager.get_confs('server')
        path = server_config.get('server', 'filePath')
        department = request.json['department']
        team = request.json['team']
        version = request.json['version']
        description = request.json['description']
        features = request.json['features']
        name = request.json['name']
        model = ModelService.addModel(filename=filename, path=path, department=department, team=team, version=version,
                                      description=description, features=features,isDeployed=False,name=name)
        return response.json({'message': 'Add model successfully'}, status=200)
    except Exception:
        logger.error(Exception)
        return response.json({'message': 'Add model failed'}, status=500)


@model_svc.post('/uploadModelFile')
async def uploadModelFile(request):
    server_config = ConfigurationManager.get_confs('server')
    filepath = server_config.get('server', 'filePath')
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    test_file = request.files.get('file')
    file_parameters = {
        'body': test_file.body,
        'name': test_file.name,
        'type': test_file.type,
    }

    try:
        file_path = filepath + file_parameters.get('name')
        with open(file_path, 'wb') as f:
            f.write(file_parameters['body'])
        f.close()
        print('file wrote to disk')
        return response.json(
            {"message": 'Upload file successfully', "file_names": request.files.keys(), "success": True}, status=200)
    except Exception:
        print(Exception)
        return response.json({"message": 'Upload file failed', "file_names": request.files.keys(), "success": False},
                             status=500)


@model_svc.post('/updateDeployStatus', strict_slashes=True)
async def updateDeployStatus(request):
    try:
        id = request.json['id']
        status = request.json['isDeployed']
        result = ModelService.updateStutusById(id=id, status=status)
        return response.json({'message': 'successed to update deploy status'}, status=200)
    except Exception:
        logger.exception('faile to update deploy status')
        return response.json({'message': 'failed to  deploy status'}, status=500)


@model_svc.post('getModelByDepartAndTeam', strict_slashes=True)
async def getModelsByDepartTeam(request):
    try:
        department = request.json['department']
        team = request.json['team']
        models = ModelService.getModelsByDepartmentAndTeam(department=department, team=team)
        return response.json(models,
                             status=200)
    except Exception:
        logger.exception('failed to get models by department and team')
        return response.json({'message': 'failed to get models by department and team'}, status=500)

