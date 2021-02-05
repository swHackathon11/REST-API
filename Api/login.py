from flask_restplus import Namespace, fields, Resource, reqparse
import pymysql
import jwt
from settings import DATABASES, JWT

Login = Namespace('login', description='로그인')

model_login = Login.model('Login Data', {
    'user_id': fields.String(description='ID', required=True),
    'user_password': fields.String(description='Password', required=True),
    'user_type': fields.String(description='User Type', required=True),
})


@Login.route('')
class PostLogin(Resource):
    @Login.expect(model_login)
    @Login.response(200, 'OK')
    @Login.response(400, 'Bad Request')
    @Login.response(401, 'Unauthorized')
    @Login.response(500, 'Internal Server Error')
    def post(self):
        '''로그인'''
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

        try:
            alba_db = pymysql.connect(user=DATABASES['user'],
                                      passwd=DATABASES['passwd'],
                                      host=DATABASES['db_host'],
                                      db=DATABASES['db_name'],
                                      charset=DATABASES["charset"])
        except Exception as e:
            print(str(e))
            if '1266' in str(e):

                return {'result': 'Fail', "error": "DB Connection Error"}, 500
            else:
                return {'result': 'Fail', "error": "DB Connection Error"}, 500

        cursor = alba_db.cursor(pymysql.cursors.DictCursor)
        query = 'select pwd from {user_type} where id = "{user_id}"'
        cursor.execute(query.format(user_type=__userType, user_id=__userID))
        __result = cursor.fetchall()
        # 아이디 존재할 시
        if __result:
            login_json = {'id': __userID,
                          'pw': __userPW,
                          'user_type': __userType
                          }


            token = jwt.encode(login_json, JWT["key"], algorithm="HS256")

            # 비밀번호 일치
            if __result[0]['pwd'] == __userPW:
                __data = []
                # 고용주
                if __userType == 'employer':
                    # 운영 매장 반환
                    query = 'select w.id from employer as e right outer join workplace AS w ON e.id = w.employer_id ' \
                            'where e.id = "{employer_id}";'

                    cursor.execute(query.format(employer_id=__userID))
                    __result = cursor.fetchall()
                    __data = [r["id"] for r in __result]

                # 종업원
                elif __userType == 'employee':
                    # 일하고 있는 매장 반환
                    query = 'select ww.workplace_id as id ' \
                            'from employee as e right outer join workplace_workers AS ww ON e.id = ww.employee_id ' \
                            'where e.id = "{employee_id}";'
                    cursor.execute(query.format(employee_id=__userID))
                    __result = cursor.fetchall()
                    __data = [r["id"] for r in __result]
                    print(__data)

                return {'result': 'Success',
                        'token': token,
                        'workplace_id': __data
                        }

            # 비밀번호 불일치
            else:
                return {'result': 'Fail',
                        'error': 'PW mismatch'}

        # 아이디 존재하지 않을 시
        else:
            return {'result': 'Fail',
                    'error': 'ID does not exist'}
