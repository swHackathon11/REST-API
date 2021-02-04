import json

import pymysql
from flask_restplus import Namespace, fields, Resource, reqparse
from flask import request

Register = Namespace('register', description='회원가입')

model_register = Register.model('Register Model', {
    'user_id': fields.String(description='ID', required=True),
    'user_password': fields.String(description='Password', required=True),
    'user_name': fields.String(description='User Name', required=True),
    'user_type': fields.String(description='User Type', required=True),
})

model_check_id = Register.model('Check Id Model', {
    'user_id': fields.String(description='ID', required=True),
    'user_type': fields.String(description='User Type', required=True),
})


# 회원가입
@Register.route('')
class PostRegister(Resource):
    @Register.expect(model_register)
    @Register.response(200, 'OK')
    @Register.response(400, 'Bad Request')
    @Register.response(401, 'Unauthorized')
    @Register.response(500, 'Internal Server Error')
    def post(self):
        __parser = reqparse.RequestParser()
        __parser.add_argument('user_id', type=str)
        __parser.add_argument('user_password', type=str)
        __parser.add_argument('user_name', type=str)
        __parser.add_argument('user_type', type=str)
        __args = __parser.parse_args()

        __userID = __args['user_id']
        __userPW = __args['user_password']
        __userName = __args['user_name']
        __userType = __args['user_type']

        alba_db = pymysql.connect(user='root', passwd='gmldn2230#', host='127.0.0.1', db='alba_db', charset='utf8')

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)
        sql = 'insert into ' + __userType + ' values ("' + __userID + '", "' + __userPW + '", "' + __userName + '");'
        print(sql)
        cursor.execute(sql)
        alba_db.commit()
        return {'result': 'success'}

# 아이디 중복 체크
@Register.route('/check')
class PostRegister(Resource):
    @Register.expect(model_check_id)
    @Register.response(200, 'OK')
    @Register.response(400, 'Bad Request')
    @Register.response(401, 'Unauthorized')
    @Register.response(500, 'Internal Server Error')
    def post(self):
        __parser = reqparse.RequestParser()
        __parser.add_argument('user_id', type=str)
        __parser.add_argument('user_type', type=str)

        __args = __parser.parse_args()
        __userID = __args['user_id']
        __userType = __args['user_type']

        alba_db = pymysql.connect(user='root', passwd='gmldn2230#', host='127.0.0.1', db='alba_db', charset='utf8')

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)

        sql = 'select id from ' + __userType + ' where id = "' + __userID + '";'
        print(sql)
        cursor.execute(sql)

        result = cursor.fetchall()

        if result:
            return {'result': 'no'}
        else:
            return {'result': 'yes'}
