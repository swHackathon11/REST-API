import datetime
import json

from flask_restplus import Namespace, fields, Resource, reqparse
import pymysql
import jwt
from settings import DATABASES, JWT

Pay = Namespace('pay', description='급여')

model_pay = Pay.model('Pay Data', {
    'token': fields.String(description='로그인 토큰', required=True),
    'workplace_id': fields.String(description='매장 아이디', required=True),
    'employee_id': fields.String(description='알바 아이디', required=True),
})


@Pay.route('')
class PostLogin(Resource):
    @Pay.expect(model_pay)
    @Pay.response(200, 'OK')
    @Pay.response(400, 'Bad Request')
    @Pay.response(401, 'Unauthorized')
    @Pay.response(500, 'Internal Server Error')
    def post(self):
        '''급여 조회'''
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('workplace_id', type=str)
        __parser.add_argument('employee_id', type=str)
        __args = __parser.parse_args()

        __token = __args['token']
        __workplace_id = __args['workplace_id']
        __employee_id = __args['employee_id']

        try:
            __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")
        except:
            return {'result': 'Fail', "error": "Auth Failed"}, 401

        # 고용주 전용ㄴ
        if __auth['user_type'] != 'employer':
            return {'result': 'Fail', 'error': 'Only for employer'}

        alba_db = pymysql.connect(user=DATABASES['user'],
                                  passwd=DATABASES['passwd'],
                                  host=DATABASES['db_host'],
                                  db=DATABASES['db_name'],
                                  charset=DATABASES["charset"])

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)
        query = 'select * from workplace_schedule ' \
                'where workplace_id = "{workplace_id}" and employee_id = "{employee_id}" and is_checked = 2;'

        cursor.execute(query.format(workplace_id=__workplace_id, employee_id=__employee_id))
        __result = cursor.fetchall()

        def default(o):
            if isinstance(o, (datetime.date, datetime.datetime, datetime.timedelta)):
                return o.__str__()

        __result = json.loads(json.dumps(__result, default=default))
        print(__result)

        return {
            'result': 'Success',
            'data': __result
        }
