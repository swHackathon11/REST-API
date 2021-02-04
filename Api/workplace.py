import jwt
import pymysql
from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse
from settings import DATABASES, JWT

Workplace = Namespace('workplace', description='매장')

model_add_workplace = Workplace.model('Workspace Add Model', {
    'token': fields.String(description='token', required=True),
    'name': fields.String(description='Workspace Name', required=True),
    'payday': fields.Integer(description='Pay day', required=True),
    'capacity': fields.Integer(description='Capacity', required=True),
})

model_delete_workplace = Workplace.model('Workspace Delete Model', {
    'token': fields.String(description='token', required=True),
    'workplace_id': fields.Integer(description='workspace ID', required=True),
})


@Workplace.route('/')
class GetWorkSpace(Resource):
    @Workplace.response(200, 'OK')
    @Workplace.response(400, 'Bad Request')
    @Workplace.response(401, 'Unauthorized')
    @Workplace.response(500, 'Internal Server Error')
    @Workplace.doc(params={'Auth': {'in': 'header', 'description': '인증 토큰', 'required': "true"}})
    def get(self):
        __auth = jwt.decode(request.headers.get('Auth'), JWT["key"], algorithms="HS256")

        if __auth['user_type'] == 'employee':
            alba_db = pymysql.connect(user=DATABASES['user'],
                                      passwd=DATABASES['passwd'],
                                      host=DATABASES['db_host'],
                                      db=DATABASES['db_name'],
                                      charset=DATABASES["charset"])

            cursor = alba_db.cursor(pymysql.cursors.DictCursor)
            query = 'select * from workplace where employee_id="{employee_id}"'

            cursor.execute(query.format(employee_id=__auth['id']))
            result = cursor.fetchall()

            return {'result': 'Success',
                    'data': result}

        else:
            return {"error": "Auth Failed"}, 401


@Workplace.route('/add')
class PostRegister(Resource):
    @Workplace.expect(model_add_workplace)
    @Workplace.response(200, 'OK')
    @Workplace.response(400, 'Bad Request')
    @Workplace.response(401, 'Unauthorized')
    @Workplace.response(500, 'Internal Server Error')
    def post(self):
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('name', type=str)
        __parser.add_argument('payday', type=int)
        __parser.add_argument('capacity', type=int)
        __args = __parser.parse_args()

        __token = __args['token']
        __name = __args['name']
        __payday = __args['payday']
        __capacity = __args['capacity']

        __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")

        if __auth['user_type'] == 'employee':
            __employee_id = __auth['id']
            print(__auth)

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
            query = 'insert into workplace values ({id},"{name}","{employee_id}", {payday}, {capacity});'
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

        else:
            return {"error": "Auth Failed"}, 401


@Workplace.route('/delete')
class PostRegister(Resource):
    @Workplace.expect(model_delete_workplace)
    @Workplace.response(200, 'OK')
    @Workplace.response(400, 'Bad Request')
    @Workplace.response(401, 'Unauthorized')
    @Workplace.response(500, 'Internal Server Error')
    def delete(self):
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('workplace_id', type=int)
        __args = __parser.parse_args()

        __token = __args['token']
        __workplace_id = __args['workplace_id']

        __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")

        if __auth['user_type'] == 'employee':
            __employee_id = __auth['id']

            alba_db = pymysql.connect(user=DATABASES['user'],
                                      passwd=DATABASES['passwd'],
                                      host=DATABASES['db_host'],
                                      db=DATABASES['db_name'],
                                      charset=DATABASES["charset"])

            cursor = alba_db.cursor(pymysql.cursors.DictCursor)

            query = 'select * from workplace where employee_id = "{employee_id}" and id={id};'


            cursor.execute(query.format(employee_id=__employee_id, id=__workplace_id))
            result = cursor.fetchall()
            print(result)

            if result:
                try:
                    query = 'delete from workplace where employee_id = "{employee_id}" and id={id};'

                    cursor.execute(query.format(employee_id=__employee_id, id=__workplace_id))
                    alba_db.commit()
                    return {'result': 'Success'}
                except Exception as e:
                    return {'result': 'Fail (' + str(e) + ')'}
            else:
                return {'result': 'Fail (지울 데이터가 없음)'}

        else:
            return {"error": "Auth Failed"}, 401
