import jwt
import pymysql
from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse
from settings import DATABASES, JWT
import json
import datetime

Calendar = Namespace('calendar', description='캘린더')

model_calendar = Calendar.model('Calendar Data', {
    'token': fields.String(description='Token', required=True),
    'year': fields.Integer(description='Year', required=True),
    'month': fields.Integer(description='Month', required=True),
})

model_add_schedule = Calendar.model('Calendar Data', {
    'token': fields.String(description='Token', required=True),
    'year': fields.Integer(description='Year', required=True),
    'month': fields.Integer(description='Month', required=True),
})


@Calendar.route('/<workplace_id>')
class postCalendar(Resource):
    @Calendar.expect(model_calendar)
    @Calendar.response(200, 'OK')
    @Calendar.response(400, 'Bad Request')
    @Calendar.response(401, 'Unauthorized')
    @Calendar.response(500, 'Internal Server Error')
    def post(self, workplace_id):
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('year', type=int)
        __parser.add_argument('month', type=int)
        __args = __parser.parse_args()

        __token = __args['token']
        __year = __args['year']
        __month = __args['month']

        try:
            __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")
            print(__auth)
        except Exception as e:
            return {"error": "Auth Failed (Invalid token)"}, 401


        alba_db = pymysql.connect(user=DATABASES['user'],
                                  passwd=DATABASES['passwd'],
                                  host=DATABASES['db_host'],
                                  db=DATABASES['db_name'],
                                  charset=DATABASES["charset"])

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)

        query = 'SELECT ws.id, ws.employer_id, employer.name, ws.date, ws.start_time, ws.end_time, ws.is_checked ' \
                'from workplace_schedule as ws right outer join employer ON ws.employer_id=employer.id ' \
                'where workplace_id="1" and YEAR(date) = {year} and Month(date) = {month};'

        cursor.execute(query.format(workplace_id=workplace_id,
                                    year=__year,
                                    month=__month))
        result = cursor.fetchall()

        def default(o):
            if isinstance(o, (datetime.date, datetime.datetime, datetime.timedelta)):
                return o.__str__()

        result = json.loads(json.dumps(result, default=default))
        return {'result': 'Success',
                'data': result}


@Calendar.route('schedule/<workplace_id>/add')
class postAddSchedule(Resource):
    @Calendar.expect(model_calendar)
    @Calendar.response(200, 'OK')
    @Calendar.response(400, 'Bad Request')
    @Calendar.response(401, 'Unauthorized')
    @Calendar.response(500, 'Internal Server Error')
    def post(self, workplace_id):
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('year', type=int)
        __parser.add_argument('month', type=int)
        __args = __parser.parse_args()

        __token = __args['token']
        __year = __args['year']
        __month = __args['month']

        try:
            __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")
        except Exception as e:
            return {"error": "Auth Failed"}, 401

        alba_db = pymysql.connect(user=DATABASES['user'],
                                  passwd=DATABASES['passwd'],
                                  host=DATABASES['db_host'],
                                  db=DATABASES['db_name'],
                                  charset=DATABASES["charset"])

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)

        query = 'select ws.id, ws.employer_id, employer.name, ws.date, ws.start_time, ws.end_time, ws.is_checked ' \
                'from workplace_schedule as ws right outer join employer ON ws.employer_id=employer.id ' \
                'where workplace_id="1" and YEAR(date) = {year} and Month(date) = {month};'

        cursor.execute(query.format(workplace_id=workplace_id,
                                    year=__year,
                                    month=__month))
        result = cursor.fetchall()

        def default(o):
            if isinstance(o, (datetime.date, datetime.datetime, datetime.timedelta)):
                return o.__str__()

        result = json.loads(json.dumps(result, default=default))

        return {'result': 'Success', 'data': result}
