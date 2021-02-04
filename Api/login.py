import json
from flask_restplus import Namespace, fields, Resource, reqparse
import pymysql

Login = Namespace('login', description='로그인')

model_login = Login.model('Login Data', {
    'user_id': fields.String(description='ID', required=True),
    'user_password': fields.String(description='Password', required=True)
})


@Login.route('')
class PostLogin(Resource):
    @Login.expect(model_login)
    @Login.response(200, 'OK')
    @Login.response(400, 'Bad Request')
    @Login.response(401, 'Unauthorized')
    @Login.response(500, 'Internal Server Error')
    def post(self):
        __parser = reqparse.RequestParser()
        __parser.add_argument('user_id', type=str)
        __parser.add_argument('user_password', type=str)
        __args = __parser.parse_args()

        __userID = __args['user_id']
        __userPW = __args['user_password']
        alba_db = pymysql.connect(user='root', passwd='', host='127.0.0.1', db='alba-db', charset='utf8')

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)
        sql = 'select pwd from user where id =' + __userID
        cursor.execute(sql)

        result = cursor.fetchall()
        print(result)
        return {'result': 'Login Success'}
