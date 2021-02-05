from flask_restplus import Namespace, fields, Resource, reqparse
import pymysql
import jwt
from settings import DATABASES, JWT

Pay = Namespace('pay', description='급여')

model_pay = Pay.model('Pay Data', {
    'token': fields.String(description='로그인 토큰', required=True),
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
        __parser.add_argument('user_id', type=str)
        __parser.add_argument('user_password', type=str)
        __parser.add_argument('user_type', type=str)
        __args = __parser.parse_args()

        __userID = __args['user_id']
        __userPW = __args['user_password']
        __userType = __args['user_type']

        if __userType != 'employee' and __userType != 'employer':
            return {'result': 'Fail',
                    'error': 'User Type is Incorrect'}

        alba_db = pymysql.connect(user=DATABASES['user'],
                                  passwd=DATABASES['passwd'],
                                  host=DATABASES['db_host'],
                                  db=DATABASES['db_name'],
                                  charset=DATABASES["charset"])

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)
        query = 'select pwd from {user_type} where id = "{user_id}"'
        cursor.execute(query.format(user_type=__userType, user_id=__userID))
        __result = cursor.fetchall()

        if __result:
            login_json = {'id': __userID,
                          'pw': __userPW,
                          'user_type': __userType
                          }


            token = jwt.encode(login_json, JWT["key"], algorithm="HS256")

            if __result[0]['pwd'] == __userPW:
                if __userType == 'employer':
                    query = 'select ww.workplace_id as id ' \
                            'from employer as e right outer join workplace_workers AS ww ON e.id = ww.employer_id ' \
                            'where e.id = "{employer_id}";'

                    cursor.execute(query.format(employer_id=__userID))
                    __result = cursor.fetchall()
                    __data = [r["id"] for r in __result]


                elif __userType == 'employee':
                    query = 'select w.id from employee as e right outer join workplace AS w ON e.id = w.employee_id where e.id = "{employee_id}";'
                    cursor.execute(query.format(employee_id=__userID))
                    __result = cursor.fetchall()
                    __data = [r["id"] for r in __result]
                    print(__data)



                return {'result': 'Success',
                        'token': token,
                        'workplace_id': __data
                        }

            else:
                return {'result': 'Fail',
                        'error': 'PW mismatch'}
        else:
            return {'result': 'Fail',
                    'error': 'ID does not exist'}
