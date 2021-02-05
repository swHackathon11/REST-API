import datetime
import json

from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse
import pymysql
import jwt
from settings import DATABASES, JWT

Substitute = Namespace('substitute', description='대타')

model_substitute = Substitute.model('Substitute Data', {
    'token': fields.String(description='Token', required=True),
    'year': fields.Integer(description='Year', required=True),
    'month': fields.Integer(description='Month', required=True),
    'day': fields.Integer(description='Day', required=False),
})

model_add_substitute = Substitute.model('Substitute Add Data', {
    'token': fields.String(description='Token', required=True),
    'workplace_schedule_id': fields.String(description='Year', required=True),
})

model_change_substitute = Substitute.model('Substitute Change Data', {
    'token': fields.String(description='Token', required=True),
    'workplace_schedule_id': fields.String(description='Year', required=True),
})

@Substitute.route('/<workplace_id>')
class GetSubstitute(Resource):
    @Substitute.expect(model_substitute)
    @Substitute.response(200, 'OK')
    @Substitute.response(400, 'Bad Request')
    @Substitute.response(401, 'Unauthorized')
    @Substitute.response(500, 'Internal Server Error')
    def post(self, workplace_id):
        '''대타 조회'''
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('year', type=str)
        __parser.add_argument('month', type=int)
        __parser.add_argument('day', type=int)
        __args = __parser.parse_args()

        __token = __args['token']
        __year = __args['year']
        __month = __args['month']
        __day = __args['day']

        try:
            __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")
        except:
            return {'result': 'Fail', "error": "Auth Failed"}, 401

        try:
            alba_db = pymysql.connect(user=DATABASES['user'],
                                      passwd=DATABASES['passwd'],
                                      host=DATABASES['db_host'],
                                      db=DATABASES['db_name'],
                                      charset=DATABASES["charset"])
        except:
            return {'result': 'Fail', "error": "DB Connection Error"}, 500

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)

        query = 'select sw.id, sw.workplace_id, e.name, sw.employee_id, ws.date, ws.start_time, ws.end_time, sw.is_checked ' \
                'from sub_wanted as sw ' \
                'right outer join workplace_schedule as ws ' \
                'ON sw.workplace_schedule_id = ws.id ' \
                'right outer join employee as e ' \
                'ON sw.employee_id = e.id ' \
                'where sw.workplace_id = "{workplace_id}" ' \
                'AND YEAR(date) = {year} AND Month(date) = {month} AND DAY(date) = {day};'

        cursor.execute(query.format(workplace_id=workplace_id,
                                    year=__year,
                                    month=__month,
                                    day=__day))

        __result = cursor.fetchall()

        def default(o):
            if isinstance(o, (datetime.date, datetime.datetime, datetime.timedelta)):
                return o.__str__()

        __result = json.loads(json.dumps(__result, default=default))

        return {'result': 'Success', 'data': __result}


@Substitute.route('/<workplace_id>/add')
class AddSubstitute(Resource):

    @Substitute.expect(model_add_substitute)
    @Substitute.response(200, 'OK')
    @Substitute.response(400, 'Bad Request')
    @Substitute.response(401, 'Unauthorized')
    @Substitute.response(500, 'Internal Server Error')
    def post(self, workplace_id):
        '''대타 등록'''
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('workplace_schedule_id', type=str)

        __args = __parser.parse_args()
        __token = __args['token']
        __workplace_schedule_id = __args['workplace_schedule_id']

        try:
            __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")
        except:
            return {'result': 'Fail', "error": "Auth Failed"}, 401

        try:
            alba_db = pymysql.connect(user=DATABASES['user'],
                                      passwd=DATABASES['passwd'],
                                      host=DATABASES['db_host'],
                                      db=DATABASES['db_name'],
                                      charset=DATABASES["charset"])
        except:
            return {'result': 'Fail', "error": "DB Connection Error"}, 500

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)

        max_id_query = 'select max(id) as max From sub_wanted;'
        cursor.execute(max_id_query)
        result = cursor.fetchall()
        try:
            __id = int(result[0]['max']) + 1
        except:
            __id = 1

        query = 'insert into sub_wanted values({id},{workplace_id}, "{employer_id}",{workplace_schedule_id}, 0);'
        cursor.execute(query.format(id=__id,
                                    workplace_id=workplace_id,
                                    employer_id=__auth['id'],
                                    workplace_schedule_id=__workplace_schedule_id
                                    ))
        alba_db.commit()
        return {'result': 'success'}


@Substitute.route('/<workplace_id>/change')
class ChangeSubstitute(Resource):

    @Substitute.expect(model_change_substitute)
    @Substitute.response(200, 'OK')
    @Substitute.response(400, 'Bad Request')
    @Substitute.response(401, 'Unauthorized')
    @Substitute.response(500, 'Internal Server Error')
    def patch(self, workplace_id):
        '''대타로 변경'''
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('workplace_schedule_id', type=str)

        __args = __parser.parse_args()
        __token = __args['token']
        __workplace_schedule_id = __args['workplace_schedule_id']

        try:
            __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")
        except:
            return {'result': 'Fail', "error": "Auth Failed"}, 401

        try:
            alba_db = pymysql.connect(user=DATABASES['user'],
                                      passwd=DATABASES['passwd'],
                                      host=DATABASES['db_host'],
                                      db=DATABASES['db_name'],
                                      charset=DATABASES["charset"])
        except:
            return {'result': 'Fail', "error": "DB Connection Error"}, 500

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)

        max_id_query = 'select max(id) as max From sub_wanted;'
        cursor.execute(max_id_query)
        result = cursor.fetchall()
        try:
            __id = int(result[0]['max']) + 1
        except:
            __id = 1

        query = 'insert into sub_wanted values({id},{workplace_id}, "{employee_id}",{workplace_schedule_id}, 0);'
        cursor.execute(query.format(id=__id,
                                    workplace_id=workplace_id,
                                    employee_id=__auth['id'],
                                    workplace_schedule_id=__workplace_schedule_id
                                    ))
        alba_db.commit()
        return {'result': 'success'}