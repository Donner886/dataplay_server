import json
from datetime import datetime
from dataplay.usersvc.User import User
from dataplay.usersvc.User import Account
from dataplay.utils.encrypt import Bcrypt

class UserService:

    @staticmethod
    def addUser(username,department,team,accountRef):
        try:
            user = User(name=username,department=department,team=team,createDate=datetime.now(),updateDate=datetime.now(),accountRef=accountRef)
            user.commit()
            return {'result':user.pk,'status':True}
        except:
            return {'result':'Insert user error','status':False}

    @staticmethod
    def registerAccount(username,password):
        try:
            # encrypt password
            passwd = Bcrypt.hashPassword(password=password)
            account = Account(username=username,password=passwd,createDate=datetime.now(),updateDate=datetime.now())
            account.commit()
            return {'result':account.pk,'status':True}
        except:
            return {'result':'Insert account error','status':False}

    @staticmethod
    def getUsers():
        try:
            userContainer = []
            users = User.find()
            for item in users:
                userContainer.append(item.dump())
            return {'result':userContainer,"status":True}
        except:
            return {'result':'Query users error','status':False}

    @staticmethod
    def getUserByAccountRef(ref):
       try:
        user = User.find({'accountRef':ref})
        userContainer = []
        for item in user:
            userContainer.append(item)
        return {'result':userContainer,'status':True}
       except:
           return {'result':"Query user error",'status':False}


    @staticmethod
    def getAccountByUserName(username):
        try:
            accounts = Account.find({'username':username})
            accountContainer = []
            for account in accounts:
                accountContainer.append(account)
            return {'result':accountContainer,'status':True}
        except:
            return {'result':"Query account by username error",'status':False}

    @staticmethod
    def isExisedUsername(username):
        try:
            results = UserService.getAccountByUserName(username)
            if results['status'] & len(results['result']):
                return {'result': 'Existed', 'status': True}
            else:
                return {'result':'NotIsExisted','status':False}
        except:
            return {'result': 'Query account failed', 'status': False}


    @staticmethod
    def authenicateUsename(username,password):
        try:
            isExisted = UserService.isExisedUsername(username)
            if isExisted['status']:
                results = UserService.getAccountByUserName(username)
                account = results['result'][0]
                # passwordEncoded = str.encode(password)
                authencated = Bcrypt.checkPassword(password, hashedPW=account['password'])
                if authencated:
                    users = UserService.getUserByAccountRef(str(account.pk))
                    return {'result':users['result'][0], 'status': True}
                else:
                    return {'result': 'Typing wrong password', 'status': False}
            else:
                return {'result': 'Account has not been registered or typing incorrent username', 'status': False}
        except Exception:
            return {'result':'Query data failed','status':False}



if __name__ == '__main__':
    results = UserService.authenicateUsename('madongdong2','abcd123')
    print(results)
