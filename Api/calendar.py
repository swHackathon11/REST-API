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
    'day': fields.Integer(description='Day', required=False),
})

return_calendar_data_model = Calendar.model('Return Calendar Data',{
    'id': fields.String(description='캘린더 ID', required=True),
    'employer_id': fields.String(description='알바 아이디', required=True),
    'name': fields.String(description='알바 이름', required=True),
    'date': fields.String(description='날짜', required=True),
    'start_time': fields.String(description='시작 시간', required=True),
    'end_time': fields.String(description='종료 시간', required=True),
    'is_checked': fields.Integer(description='출근 여부', required=True),
})

calendar_response_model = Calendar.model('Attendance Response Model', {
    'result': fields.String(description='성공 여부'),
    'data': fields.List(fields.Nested(return_calendar_data_model)),
})


@Calendar.route('/<workplace_id>')
class postCalendar(Resource):
    @Calendar.expect(model_calendar)
    @Calendar.response(200, 'OK', model=calendar_response_model)
    @Calendar.response(400, 'Bad Request')
    @Calendar.response(401, 'Unauthorized')
    @Calendar.response(500, 'Internal Server Error')
    def post(self, workplace_id):
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('year', type=int)
        __parser.add_argument('month', type=int)
        __parser.add_argument('day', type=int)
        __args = __parser.parse_args()

        __token = __args['token']
        __year = __args['year']
        __month = __args['month']
        __day = __args['day']

        print(__day)
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
        if __day is None:
            query = 'SELECT ws.id, ws.employer_id, employer.name, ws.date, ws.start_time, ws.end_time, ws.is_checked ' \
                    'from workplace_schedule as ws right outer join employer ON ws.employer_id=employer.id ' \
                    'where workplace_id="1" and YEAR(date) = {year} and Month(date) = {month};'

            cursor.execute(query.format(workplace_id=workplace_id,
                                        year=__year,
                                        month=__month))
        else:
            query = 'SELECT ws.id, ws.employer_id, employer.name, ws.date, ws.start_time, ws.end_time, ws.is_checked ' \
                    'from workplace_schedule as ws right outer join employer ON ws.employer_id=employer.id ' \
                    'where workplace_id="1" and YEAR(date) = {year} and Day(date) = {day};'

            cursor.execute(query.format(workplace_id=workplace_id,
                                        year=__year,
                                        month=__month,
                                        day = __day))


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
