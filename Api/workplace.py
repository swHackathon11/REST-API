import jwt
import pymysql
from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse
from settings import DATABASES


Workspace = Namespace('workspace', description='매장')

model_workspace = Workspace.model('Workspace Model', {
    'token': fields.String(description='token', required=True),
    'name': fields.String(description='Workspace Name', required=True),
    'employee_id': fields.String(description='Employ ID', required=True),
    'payday': fields.String(description='Pay day', required=True),
    'capacity': fields.String(description='Capacity', required=True),
})


@Workspace.route('/')
class GetWorkSpace(Resource):
    @Workspace.response(200, 'OK')
    @Workspace.response(400, 'Bad Request')
    @Workspace.response(401, 'Unauthorized')
    @Workspace.response(500, 'Internal Server Error')
    @Workspace.doc(params={'Auth': {'in': 'header', 'description': '인증 토큰', 'required': "true"}})
    def get(self):
        __auth = jwt.decode(request.headers.get('Auth'), "secret_key", algorithms="HS256")

        if __auth['user_type'] == 'employee':
            print(__auth)
            alba_db = pymysql.connect(user='root', passwd='gmldn2230#', host='127.0.0.1', db='alba_db', charset='utf8')
            cursor = alba_db.cursor(pymysql.cursors.DictCursor)
            query = 'select * from workplace where employee_id="{employee_id}"'

            cursor.execute(query.format(employee_id=__auth['id']))
            result = cursor.fetchall()
            print(result)

            return {'result': 'Success',
                    'data': result}

        else:
            return {"error": "Auth Failed"}, 401




@Workspace.route('/add')
class PostRegister(Resource):
    @Workspace.expect(model_workspace)
    @Workspace.response(200, 'OK')
    @Workspace.response(400, 'Bad Request')
    @Workspace.response(401, 'Unauthorized')
    @Workspace.response(500, 'Internal Server Error')
    def post(self):
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('name', type=str)
        __parser.add_argument('employee_id', type=str)
        __parser.add_argument('payday', type=str)
        __parser.add_argument('capacity', type=str)
        __args = __parser.parse_args()

        __token = __args['token']
        __name = __args['name']
        __employee_id = __args['employee_id']
        __payday = __args['payday']
        __capacity = __args['capacity']
        alba_db = pymysql.connect(user=DATABASES['user'],
                                  passwd=DATABASES['passwd'],
                                  host=DATABASES['db_host'],
                                  db=DATABASES['db_name'],
                                  charset=DATABASES["charset"])

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)
        max_id_query = 'select max(id) as max From workplace;'
        cursor.execute(max_id_query)
        result = cursor.fetchall()
        try:
            __id = int(result[0]['max']) + 1
        except:
            __id = 1

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)
        query = 'insert into workplace values ({id},"{name}","{employee_id}", "{payday}", "{capacity}");'
        try:
            cursor.execute(query.format(id=__id,
                                        name=__name,
                                        employee_id=__employee_id,
                                        payday=__payday,
                                        capacity=__capacity
                                        ))

            alba_db.commit()

            return {'result': 'Success'}
        except:
            return {'result': 'Fail'}


@Workspace.route('/delete')
class PostRegister(Resource):
    @Workspace.expect(model_workspace)
    @Workspace.response(200, 'OK')
    @Workspace.response(400, 'Bad Request')
    @Workspace.response(401, 'Unauthorized')
    @Workspace.response(500, 'Internal Server Error')
    def delete(self):
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

        alba_db = pymysql.connect(user=DATABASES['user'],
                                  passwd=DATABASES['passwd'],
                                  host=DATABASES['db_host'],
                                  db=DATABASES['db_name'],
                                  charset=DATABASES["charset"])

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)
        sql = 'insert into ' + __userType + ' values ("' + __userID + '", "' + __userPW + '", "' + __userName + '");'
        print(sql)
        cursor.execute(sql)
        alba_db.commit()
        return {'result': 'success'}
