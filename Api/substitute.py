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


@Substitute.route('/<workplace_schedule_id>')
class PostSubstitute(Resource):

    @Substitute.expect(model_substitute)
    @Substitute.response(200, 'OK')
    @Substitute.response(400, 'Bad Request')
    @Substitute.response(401, 'Unauthorized')
    @Substitute.response(500, 'Internal Server Error')
    def post(self, workplace_schedule_id):
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('year', type=str)
        __parser.add_argument('month', type=str)
        __parser.add_argument('day', type=str)
        __args = __parser.parse_args()

        __token = __args['token']
        __year = __args['year']
        __month = __args['month']
        __day = __args['day']

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

                query = 'select ww.workplace_id ' \
                        'from employer as e right outer join workplace_workers AS ww ON e.id = ww.employer_id ' \
                        'where e.id = "{employer_id}";'

                cursor.execute(query.format(employer_id=__userID))
                __result = cursor.fetchall()
                print(__result)

                return {'result': 'Success',
                        'token': token,
                        'data': __result
                        }

            else:
                return {'result': 'Fail',
                        'error': 'PW mismatch'}
        else:
            return {'result': 'Fail',
                    'error': 'ID does not exist'}
