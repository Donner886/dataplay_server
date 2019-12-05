from sanic import Blueprint
from sanic import response
from sanic.log import logger
from dataplay.usersvc.userservice import UserService
import json


user_svc = Blueprint('user_svc')

@user_svc.post('/register', strict_slashes=True)
async def register(request):
    try:
        accountID= UserService.registerAccount(username=request.form.get('username'),password=request.form.get('password'))
        if accountID:
            return response.json({'message':'successed to register member','username':request.form.get('username')}, status=200)
    except Exception:
        logger.exception('faile to register the member')
        return response.json({'message':'failed to register member'}, status=500)


# When open the login api, we open and save the session info
# when open another api, we first open request session and check if existed in redis and then make decision of
# redirecting.

@user_svc.post('/login',strict_slashes=True)
async def login(request):
    try:
        username = request.json['userName']
        password = request.json['password']
        authenticatedUser = UserService.authenicateUsename(username=username,password=password)
        if authenticatedUser['status']:
            request['session']['accountRef'] = str(authenticatedUser.get('result'))
            request['session']['username'] = username
            department = authenticatedUser.get('result').dump().get('department')
            team = authenticatedUser.get('result').dump().get('team')
            return response.json({"message":"Login successed",'sid': request['session'].sid,'department': department,'team': team },status=200)
        else:
            return response.json({"message": str(authenticatedUser.get('result'))}, status=200)
    except Exception:
            return response.json({'message':'Server internal error'},status=500)




@user_svc.post('/addUserInfo',strict_slashes=True)
async def addUserInfo(request):
    try:
        # Get the session content from request['session'] which is generated before request by middleware
        # if content is empty, redirect the url to login
        session_data = request['session']
        if session_data.get('username'):
            accountName = session_data.get('username')
        else:
            return response.json({'message': 'please login in first'}, status=200)
        if session_data.get('accountRef'):
            accountRef = session_data.get('accountRef')
        else:
            return response.json({'message':'please login in first'}, status=200)
        user = UserService.addUser(username=request.form.get('username'),
                        department=request.form.get('department'),
                        team=request.form.get('team'),
                        accountRef=accountRef)
        if user.get('status'):
            return response.json({'message':'successed to add user information','username':request.form.get('username')}, status=200)
    except Exception:
        return response.json({'message':'Failed to add user information'},status=500)



@user_svc.get('/getUsers', strict_slashes=True)
async def user(request):
    try:
        user = UserService.getUsers()
        return response.json({'message':user.get('result')},status=200)
    except Exception:
        logger.exception('faile to get all users')
        return response.json({'message':'Server Internal error'}, status=500)
#


#
# @user_svc.get('/auth_routes', strict_slashes=True)
# @doc.summary('get authorized routes')
# async def routes(request):
#     try:
#         routes = get_routes()
#         return response.json(routes, 200)
#     except Exception:
#         logger.exception('faile to get get routes')
#         return response.json({}, status=500)
