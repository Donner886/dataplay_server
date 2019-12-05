'''
The class provide functions of encrypt including password and so on
'''
import bcrypt


class Bcrypt:

    @staticmethod
    def hashPassword(password):
        hashPW = bcrypt.hashpw(str.encode(password),bcrypt.gensalt())
        return hashPW

    @staticmethod
    def checkPassword(password, hashedPW):
        if bcrypt.checkpw(str.encode(password), str.encode(hashedPW)):
            return True
        else:
            return False

#
# if __name__ == '__main__':
#     password = 'abcd123'
#     print('begin hash password')
#     print(Bcrypt.hashPassword(password))
#     hashed = Bcrypt.hashPassword(password)
#     if Bcrypt.checkPassword(password,hashed):
#         print('It matches')
#     else:
#         print('It doesnot matched')