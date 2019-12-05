import os
import base64
from datetime import datetime

from sanic.log import logger
from dataplay.confsvc.manager import ConfigurationManager
from dataplay.datasvc.registry import get_dataset_class
from dataplay.datasvc.csv import CSV_DATASET_PATH
from dataplay.datasvc.datasetsM import DataSets
from .predicted import Predicted
from dataplay.datasvc.dataset import DataSet
from umongo import Instance, Document, fields, validate


class DatasetManager:

    @staticmethod
    def list_datasets(department, team):
        datasets = []
        setWrap = DataSets.find({'department': department, 'team': team})
        for set in setWrap:
            datasets.append(set.dump())
        return datasets

    @staticmethod
    def get_dataset(id):
        config = ConfigurationManager.get_confs('datasets')
        content = config.get(id, 'content')
        name = config.get(id, 'name')
        description = config.get(id, 'description')
        dataset_type = config.get(id, 'type')
        dataset_class = get_dataset_class(dataset_type)

        dataset = dataset_class(id, name, content, description)
        return dataset

# ####################################################### Predicted Dataset ################################################
    @staticmethod
    def get_predicted(id):
        predicted = Predicted.find({'_id':fields.ObjectId(id)});
        for result in predicted:
            predicted_dataset = result
        return predicted_dataset


    @staticmethod
    def getAllPredictedDataset(department,team):
        cursorPred = Predicted.find({'department': department,
                                    'team': team})
        container = []
        for item in cursorPred:
            container.append(item.dump())
        return container

    @staticmethod
    def getPredictedConnection(connection):
        wrapped = DataSet().getConnection(connection)
        container = [];
        for cursor in wrapped:
            container.append(cursor)
        return container


    @staticmethod
    def add_predictedMeta(predictedName, department, team):
        try:
            #  update or add
            result = Predicted.find({'predicted': predictedName,
                                     'department': department,
                                 'team': team})
            container = []
            for data in result:
                container.append(data)
            if len(container) > 0:
                container[0].updateDate = datetime.now()
                container[0].commit()
                return {'result': container[0].pk, 'status': True}
            else:
                predicted = Predicted(predicted=predictedName,
                                      department=department, team=team,
                                      createDate=datetime.now(),
                                      updateDate=datetime.now())
                predicted.commit()
                return {'result': predicted.pk, 'status': True}
        except Exception:
            return {'result': 'failed to insert predicted meta data', 'status': False}

    @staticmethod
    def add_dataset(payload):
        try:
            datasetName = payload['dataSetName']
            description = payload['description']
            team = payload['team']
            department = payload['department']
            createDate = datetime.now()
            updateDate = datetime.now()
            # confirm whether the dataset existed
            datasets = DatasetManager.getByDataset(datasetName, department, team)
            action = ''
            if datasets['status']:
                if len(datasets['result']) == 0:
                    dataset = DataSets(dataSetName=datasetName, description=description, department=department,
                                       team=team,
                                       createDate=createDate, updateDate=updateDate)
                    dataset.commit()
                    action = 'add'
                else:
                    datasets['result'][0]['description'] = description
                    datasets['result'][0]['updateDate'] = updateDate
                    datasets['result'][0].commit()
                    action = 'update'
            return {'result': datasetName, 'action': action, 'status': 200}
        except Exception:
            print(Exception)
            return {'result': 'failed to insert dataset', 'status': 500}

    @staticmethod
    def getByDataset(dataSetName, department, team):
        try:
            result = DataSets.find({'dataSetName': dataSetName,
                                    'department': department,
                                    'team': team})
            container = []
            for data in result:
                container.append(data)
            return {'result': container, 'status': True}
        except Exception:
            return {'result': [], 'status': False}



# ################################################## end #####################################################



    @staticmethod
    def delete_dataset(id):
        dataset = DatasetManager.get_dataset(id)
        domain = 'datasets'
        ConfigurationManager.remove_section(domain, id)

        try:
            dataset.delete()
        except Exception:
            logger.warning(f'faile to delete dataset {id}')

    #  I have to change the logic of uploading DataSet so as to persist with mongodb.
    @staticmethod
    def upload_dataset(name, content):
        # TODO check dir based on file type
        upload_dir = CSV_DATASET_PATH
        filepath = os.path.join(upload_dir, name)
        with open(filepath, "wb") as f:
            f.write(content)
            f.close()

    @staticmethod
    def query2dataset(
            source_dataset_id, query_type, query, dataset_id, dataset_name, dataset_description
    ):
        dataset = DatasetManager.get_dataset(source_dataset_id)
        query_df = dataset.query(query, query_type)
        content = query_df.to_csv()
        filename = f'{dataset_id}.csv'
        DatasetManager.upload_dataset(filename, content.encode())

        creation_payload = {}
        creation_payload['id'] = dataset_id
        creation_payload['name'] = dataset_name
        creation_payload['content'] = filename
        creation_payload['type'] = 'csv'
        creation_payload['description'] = dataset_description

        DatasetManager.add_dataset(creation_payload)
