import json
import os
from datetime import datetime
from sanic import Blueprint
from sanic import response
from sanic.log import logger
from sanic_openapi import doc

import pandas as pd
from .manager import DatasetManager
from .dataset import DataSet
from dataplay.modeluploader.modelservice import ModelService
import wordcloud
from dataplay.confsvc.manager import ConfigurationManager

from NLP.sentiment.sentiment_classification import sentiment_classify
from NLP.keywords.keywords_extractions import get_keywords,frequency_wordcloud

from dataplay.datasvc.csv import CSV_DATASET_PATH
import ujson
import numpy as np

dataset_svc = Blueprint('dataset_svc')


@dataset_svc.post('/datasets', strict_slashes=True)
async def list_datasets(request):
    try:
        department = request.json['payload']['department']
        team = request.json['payload']['team']
        datasets = DatasetManager.list_datasets(department=department, team=team)
        models = ModelService.getModelsByDepartmentAndTeam(department=department, team=team)
        return response.json({'datasets': datasets, 'models': models}, status=200)
    except Exception:
        logger.exception('faile to list dataset')
        return response.json({}, status=500)


@dataset_svc.get('/datasets/<id>', strict_slashes=True)
async def get_dataset(request, id):
    try:
        results = DataSet().getConnection(id)
        DataList = []
        for result in results:
            DataList.append(result)

        # dataset = DatasetManager.get_dataset(id)
        # payload = dataset.get_payload()
        df_dataset = pd.DataFrame(DataList)
        columns_dataset = df_dataset.columns
        return response.json({'rows': DataList, 'cols': columns_dataset}, status=200)
    except Exception:
        logger.exception('faile to get dataset')
        return response.json({'faile to get dataset'}, status=500)


@dataset_svc.delete('/datasets/<id>', strict_slashes=True)
@doc.summary('delete one dataset')
async def delete_dataset(request, id):
    try:
        DatasetManager.delete_dataset(id)
        return response.json({}, status=204)
    except Exception:
        logger.exception('faile to delete dataset')
        return response.json({}, status=500)


@dataset_svc.post('/datasets/<id>/query', strict_slashes=True)
@doc.summary('run a dataset query')
@doc.produces({"cols": [str], "rows": [[object]]}, content_type="application/json")
@doc.consumes(
    doc.JsonBody({"type": str, "query": str}), content_type="application/json", location="body"
)
async def query_dataset(request, id):
    logger.debug(f'query dataset query payload={request.body} on {id}')
    try:
        dataset = DatasetManager.get_dataset(id)
        request_body = json.loads(request.body)
        query_result = dataset.query(request_body['query'], request_body['type'], True)
        return response.json(query_result, status=200)
    except Exception:
        logger.exception('faile to query dataset')
        return response.json({}, status=500)


# first: store the file into folder with timestamp in filename
# insert into mongodb
@dataset_svc.post('/dataset_upload', strict_slashes=True)
@doc.summary('upload a dataset file')
async def upload_dataset(request):
    name = datetime.now().strftime('%Y%m%d %H%M%S') + '_' + request.files["file"][0].name
    connection = request.files['file'][0].name.split('.')[0]
    try:
        DatasetManager.upload_dataset(name, request.files["file"][0].body)
        # And then read the data
        filepath = os.path.join(CSV_DATASET_PATH, name)
        data = pd.read_csv(filepath).to_json(orient='records')
        result = DataSet().saveDocuments(connection=connection, documents=json.loads(data))

        return response.json({'message': 'success to upload the file'}, status=200)

    except Exception:
        logger.exception('faile to upload dataset')
        return response.json({'message': 'faile to query dataset'}, status=500)


@dataset_svc.post('/getService', strict_slashes=True)
async def getService(request):
    try:
        department = request.json['userInfo']['department']
        team = request.json['userInfo']['team']
        datasetname = request.json['dataset']['name']
        datasetstart = request.json['dataset']['startTime']
        datasetEnd = request.json['dataset']['endTime']
        timeRangeColumn = request.json['dataset']['timeRangeColumn']
        # datasetTimeColumn = request.json['datatimeColumn']
        modelName = request.json['model']['filename']
        modelPath = request.json['model']['path']
        modelversion = request.json['model']['version']
        modelid = request.json['model']['id']
        model = ModelService.getModelById(modelid)
        if (len(model) >= 1):
            modelname = model[0]['name']
            modelFeatures = model[0]['features'].split(',')
        if modelname == 'NLP':
            print('we want to nlp function to comprehend the sentimental and keyword')
            comment = modelFeatures[0]
            datasets = DataSet().getConnectionByCondition(datasetname,timeRangeColumn ,datasetstart, datasetEnd);
            if datasets['status'] == True:
                tobe_predict = datasets['result']
                features = comment
                #   and then insert the result into mongodb
                tobe_predict['sentimental'] = tobe_predict[comment].apply(lambda x: sentiment_classify(x))
                tobe_predict['keyWords'] = tobe_predict[comment].apply(lambda x: get_keywords(x))
                connection_predicted = datasetname + '_predictoin'
                tobe_predict['index'] = tobe_predict[timeRangeColumn].dt.strftime('%Y-%m-%d %H:%M:%S')
                ids = DataSet().saveDocuments(connection_predicted,
                                              documents=json.loads(tobe_predict.to_json(orient='records')))
                # insert the meta data into
                predictMeta = DatasetManager.add_predictedMeta(predictedName=connection_predicted,
                                                               department=department, team=team)
                if predictMeta['status']:
                    return response.json({'message': 'predict successfully', 'result': str(predictMeta['result'])},
                                         status=200)
                else:
                    return response.json(
                        {'message': 'error hanppend when insert data into db', 'result': str(predictMeta['result'])},
                        status=200)


        else:
            # first, get the dataset with features want to be predict
            datasets = DataSet().getConnectionByCondition(datasetname, timeRangeColumn, datasetstart, datasetEnd);
            if datasets['status'] == True:
                tobe_predict = datasets['result']
                features = modelFeatures
                #  second, we load the model and predict data
                clf = ModelService.loadModel(modelid)
                # before predict, should check the features fitting to the model,
                tobe_predict['prediction'] = clf.predict(tobe_predict[list(features)])
                #   and then insert the result into mongodb
                connection_predicted = datasetname + '_predictoin'
                tobe_predict['index'] = tobe_predict[timeRangeColumn].dt.strftime('%Y-%m-%d %H:%M:%S')
                ids = DataSet().saveDocuments(connection_predicted,
                                              documents=json.loads(tobe_predict.to_json(orient='records')))
                # insert the meta data into
                predictMeta = DatasetManager.add_predictedMeta(predictedName=connection_predicted,
                                                               department=department, team=team)
                if predictMeta['status']:
                    return response.json({'message': 'predict successfully', 'result': str(predictMeta['result'])},
                                         status=200)
                else:
                    return response.json(
                        {'message': 'error hanppend when insert data into db', 'result': str(predictMeta['result'])},
                        status=200)
            else:
                return response.json(
                    {'message': 'specific column name does not existed', 'result': datasets['columns']},
                    status=200)
    except Exception:
        logger.exception(Exception)
        return response.json({'message': 'failed to predict the dataset'}, status=500)


# ###################################################################### Predicted dateset ###################################
@dataset_svc.post('/getPredictResult', strict_slashes=True)
async def getPredictResult(request):
    try:
        department = request.json['userInfo']['department']
        team = request.json['userInfo']['team']
        datasetname = request.json['dataset']['name']
        datasetstart = request.json['dataset']['startTime'].replace('/', '-')
        datasetEnd = request.json['dataset']['endTime'].replace('/', '-')
        timeRangeColumn = request.json['dataset']['timeRangeColumn']
        id = request.json['predictSetId']
        predicted = DatasetManager.get_predicted(id)
        datasets = DataSet().getConnectionPredictedByCondition(predicted['predicted'], datasetstart, datasetEnd);
        columns = pd.DataFrame(datasets).columns
        return response.json({'rows': datasets, 'cols': columns}, status=200)
    except Exception:
        logger.error(Exception)
        return response.json({'message': 'failed to get predicted result'}, status=500)


@dataset_svc.post('/getPredictsList', strict_slashes=True)
async def getPredictedDatasetList(request):
    try:
        department = request.json['payload']['department'];
        team = request.json['payload']['team'];
        result = DatasetManager.getAllPredictedDataset(department=department, team=team)
        return response.json({'result': result}, status=200)
    except Exception:
        return response.json({'result': 'error happend'}, status=500)


@dataset_svc.post('/getDescriptionOfConnection', strict_slashes=True)
async def getPredictedConnectionDecription(request):
    try:
        connection = request.json['payload']
        result = DatasetManager.getPredictedConnection(connection)
        df = pd.DataFrame(result)
        columns = df.columns
        selectedDatasetInfo = dict()
        for column in columns:
            selectedDatasetInfo[column] = dict()
            dtype = str(df[column].dtype)
            print(dtype)
            if ('datetime' in dtype):
                selectedDatasetInfo[column] = dict(dtype=str(df[column].dtype),
                                                   drange=[str(df[column].min()), str(df[column].max())])
            elif ('str' in dtype):
                selectedDatasetInfo[column] = dict(dtype=str(df[column].dtype), drange=df[column].unique())
            elif ('object' in dtype):
                selectedDatasetInfo[column] = dict(dtype=str(df[column].dtype),
                                                   drange=[str(df[column].astype('str').min()), str(df[column].astype('str').max())])
            else:
                selectedDatasetInfo[column] = dict(dtype=str(df[column].dtype),
                                                   drange=[str(df[column].min()),
                                                           str(df[column].max())])
        return response.json({'result': selectedDatasetInfo,'dataset':connection}, status=200)
    except Exception:
        logger.error(Exception)
        return response.json({'result': 'failed to get the description of connection'}, status=500)


# ######################################## Multiple-dimensional analysis ################################################
# Here we want to fulfil a filter and groupby functionality base on the specific conditions
@dataset_svc.post('/multiDimensionAnalysis', strict_slashes=True)
async def multiDimensionAnalysis(request):
    conditions = request.json['payload']
    #  'iris_v3_predictoin'
    dataset = conditions['dataset']
    # <class 'list'>: ['2019/11/01 09:52:06', '2019/11/30 09:52:06']
    dataRange = conditions['dataRange']
    # <class 'list'>: [{'id': 6, 'column': 'petal width (cm)', 'operation': 'lt', 'value': '4'}]
    filters = conditions['filters']
    #  <class 'list'>: ['petal width (cm)', 'petal length (cm)']
    groups = conditions['groups']
    # <class 'list'>: [{'id': 4, 'column': 'prediction', 'metric': 'sum'}]
    metric = conditions['metric']
    #  when the dataset is large enough, we wil change the search strategy to mongodb aggregation strategy
    startDate = dataRange[0].replace('/','-')
    endDate = dataRange[1].replace('/','-')
    subset = DataSet().getConnectionPredictedByCondition(dataset,startDate,endDate)
    df = pd.DataFrame(subset)
    for filter in filters:
        column = filter['column']
        operation = filter['operation']
        value = filter['value']
        if operation == 'lg':
            df = df[df[column] > np.float(value)]
        elif operation == 'lt':
            df = df[df[column] < np.float(value)]
        elif operation == 'eq':
            df = df[df[column] == np.float(value)]
        elif operation == 'lge':
            df = df[df[column] >= np.float(value)]
        elif operation == 'lte':
            df = df[df[column] <= np.float(value)]
    metrics = {}
    for met in metric:
        column = met['column']
        metric = met['metric']
        metrics[column] = metric
    df_group = df.groupby(groups).agg(metrics)
    df_group.reset_index(inplace=True)

    result = []
    for index, row in df_group.iterrows():
        obj = {}
        for idx in row.index:
            if idx in groups:
                obj[idx] = str(row.loc[idx])
            else:
                obj[idx] = float(row.loc[idx])
        result.append(obj)
    return response.json({'message': result}, status=200)



@dataset_svc.post('/drawWordCloud',strict_slashes=True)
def drawWordCloud(request):
    try:
        appname = request.json['appname']
        connection = request.json['name']
        channel = request.json['channel']
        sentiment = request.json['sentiment']
        startTime = request.json['startTime'].replace('/','-')
        endTime = request.json['endTime'].replace('/','-')
        keywordColumn = request.json['keywordColumn']
        result = DataSet().getConnectionPredictedByCondition(connection,startTime,endTime)
        if len(result) > 0:
            df = pd.DataFrame(result)

            df['keywords_counts'] = df[keywordColumn].apply(lambda x: len(x))
            df = df[df['keywords_counts'] > 0]
            comments_keyword  = df[(df[channel] == appname) & (df['sentimental'] == sentiment)][keywordColumn]
            # keywords = ','
            # keywords = keywords.join(comments_keyword.apply(lambda x:str(x[0])))
            server_config = ConfigurationManager.get_confs('server')
            filepath = server_config.get('server', 'wordcloudPath')
            filename = 'wordcloud' + datetime.now().strftime('%Y%m%d%H%M%S')
            data  = frequency_wordcloud(list(comments_keyword),filepath,filename,sentiment)
            filename_suffix = filename + '.jpeg'
            return response.json({'message':'successd to generate wordcloud','result':filename_suffix},status=200)
        else:
            return response.json({'message':'there is no record during the period',result:[]},status=200)
    except Exception:
        logger.error(Exception);
        response.json({'message':'failed to draw wordCloud'},status=500)


@dataset_svc.get('/getfile/<file>',strict_slashes=True)
async def handle_request(request,file):
    server_config = ConfigurationManager.get_confs('server')
    filepath = server_config.get('server', 'wordcloudPath')
    return await response.file(filepath + file)



# first: store the file into folder with timestamp in filename
# insert into mongodb
@dataset_svc.post('/registeDataSet', strict_slashes=True)
@doc.summary('register the dataset')
async def registeDataSet(request):
    try:
        payload = {
            'dataSetName': request.json['name'],
            'description': request.json['description'],
            'department': request.json['department'],
            'team': request.json['team']
        }

        result = DatasetManager.add_dataset(payload=payload)
        if result['status'] == 200:
            return response.json({'message': 'success to add dataset information'}, status=200)
        else:
            return response.json({'message': 'fail to add dataset information'}, status=500)
    except Exception:
        logger.exception('faile to add dataset information')
        return response.json({'faile to add dataset information'}, status=500)


@dataset_svc.post('/query2dataset', strict_slashes=True)
@doc.summary('export a query result as dataset')
@doc.produces({}, content_type="application/json")
@doc.consumes(
    doc.JsonBody(
        {
            "source_dataset_id": str,
            "query_type": str,
            "query": str,
            "dataset_id": str,
            "dataset_name": str,
            "dataset_description": str,
        }
    ),
    content_type="application/json",
    location="body",
)
async def query2dataset(request):
    try:
        request_body = json.loads(request.body)
        DatasetManager.query2dataset(**request_body)
        return response.json({}, status=200)
    except Exception:
        logger.exception('faile to query dataset')
        return response.json({}, status=500)
