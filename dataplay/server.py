from sanic import Sanic, response, request
from sanic_openapi import swagger_blueprint
from sanic_cors import CORS, cross_origin
from dataplay.datasvc.service import dataset_svc
from dataplay.datasvc.registry import DatasetTypeRegistry
from dataplay.usersvc.usercontroller import user_svc
from dataplay.notificationsvc.service import notification_svc
from dataplay.dashboardsvc.service import dashboard_svc
from dataplay.mlsvc.service import ml_svc
from dataplay.confsvc.service import conf_svc
from dataplay.filesvc import file_svc
from dataplay.modeluploader.modelcontroller import model_svc

from dataplay.confsvc.manager import ConfigurationManager

from dataplay.session import Session, RedisSessionInterface
import uvicorn

PREFIX = '/api'
app = Sanic(__name__)

#
# @app.middleware('response')
# async def supportcors( request,response ):
#     response.headers['Access-Control-Allow-Origin'] = "*"
#     response.headers['Access-Control-Allow-Methods'] = 'POST,GET,OPTIONS,DELETE'
#     response.headers['Access-Control-Allow-Headers'] = '*'
# response.cookies['session'] = request.cookies.get('session')
# response.cookies['session']["httponly"] = True


# Add the session
Session(app, interface=RedisSessionInterface(expiry=600, sessioncookie=True, httponly=True))
# Add cors extension
CORS(app, automatic_options=True, supports_credentials=True)

# app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)

app.config.API_VERSION = '1.0.0'
app.config.API_TITLE = 'Dataplay API'
app.config.API_DESCRIPTION = 'Dataplay API'
app.config.API_CONTACT_EMAIL = 'dongdongma@cncbinternational.com'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']

server_config = ConfigurationManager.get_confs('server')
app.config.HOST = server_config.get('server', 'host')
app.config.port = 8888
app.config.DEBUG = server_config.getboolean('server', 'debug')
app.config.WORKERS = server_config.getint('server', 'workers')

dataset_type_config = ConfigurationManager.get_confs('dataset_type')
dataset_registry = DatasetTypeRegistry()
for section in dataset_type_config.sections():
    module_name = dataset_type_config.get(section, 'module')
    class_name = dataset_type_config.get(section, 'class')
    dataset_registry.register(section, class_name, module_name)

app.blueprint(file_svc)
app.blueprint(dataset_svc, url_prefix=PREFIX)
app.blueprint(user_svc, url_prefix=PREFIX)
app.blueprint(notification_svc, url_prefix=PREFIX)
app.blueprint(dashboard_svc, url_prefix=PREFIX)
app.blueprint(ml_svc, url_prefix=PREFIX)
app.blueprint(conf_svc, url_prefix=PREFIX)
app.blueprint(model_svc, url_prefix=PREFIX)

# @app.route('/')
# def handle_request(request):
#     return response.redirect('/ui/index.html')


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8888)
