import jwt
import pymysql
from flask import request
from flask_restplus import Namespace, fields, Resource, reqparse
from settings import DATABASES, JWT

Workplace = Namespace('workplace', description='매장')

model_add_workplace = Workplace.model('Workplace Add Model', {
    'token': fields.String(description='token', required=True),
    'name': fields.String(description='Workspace Name', required=True),
    'payday': fields.Integer(description='Pay day', required=True),
    'capacity': fields.Integer(description='Capacity', required=True),
})

model_delete_workplace = Workplace.model('Workspace Delete Model', {
    'token': fields.String(description='token', required=True),
    'workplace_id': fields.Integer(description='workspace ID', required=True),
})

model_workplace_hire = Workplace.model('Workplace Hire Model', {
    'token': fields.String(description='token', required=True),
    'employer_id': fields.String(description='Employer ID', required=True),
    'hourly': fields.String(description='Hourly Wage', required=True),
    'tax_included': fields.Integer(description='Tax', required=True),
})

model_workplace_fire = Workplace.model('Workspace Fire Model', {
    'token': fields.String(description='token', required=True),
    'employer_id': fields.String(description='Employer ID', required=True),
})

model_workplace_attendance = Workplace.model('Workplace Attendance Model', {
    'token': fields.String(description='token', required=True),
    'year': fields.Integer(description='Year', required=True),
    'month': fields.Integer(description='Month', required=True),
    'day': fields.Integer(description='Day', required=True),
})

model_workplace_leave = Workplace.model('Workplace Leave Model', {
    'token': fields.String(description='token', required=True),
    'year': fields.Integer(description='Year', required=True),
    'month': fields.Integer(description='Month', required=True),
    'day': fields.Integer(description='Day', required=True),
})


@Workplace.route('/')
class GetWorkSpace(Resource):
    @Workplace.response(200, 'OK')
    @Workplace.response(400, 'Bad Request')
    @Workplace.response(401, 'Unauthorized')
    @Workplace.response(500, 'Internal Server Error')
    @Workplace.doc(params={'Auth': {'in': 'header', 'description': '인증 토큰', 'required': "true"}})
    def get(self):
        '''매장 조회'''
        try:
            __auth = jwt.decode(request.headers.get('Auth'), JWT["key"], algorithms="HS256")
        except:
            return {'result': 'Fail', "error": "Auth Failed"}, 401
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
        '''매장 추가'''
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

        try:
            __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")
        except:
            return {'result': 'Fail', "error": "Auth Failed"}, 401

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
        '''매장 삭제'''
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('workplace_id', type=int)
        __args = __parser.parse_args()

        __token = __args['token']
        __workplace_id = __args['workplace_id']

        try:
            __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")
        except:
            return {'result': 'Fail', "error": "Auth Failed"}, 401

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


@Workplace.route('/<workplace_id>')
class WorkplaceWorker(Resource):
    @Workplace.response(200, 'OK')
    @Workplace.response(400, 'Bad Request')
    @Workplace.response(401, 'Unauthorized')
    @Workplace.response(500, 'Internal Server Error')
    @Workplace.doc(params={'Auth': {'in': 'header', 'description': '인증 토큰', 'required': "true"}})
    def get(self, workplace_id):
        '''매장 직원 찾기'''
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __args = __parser.parse_args()
        __token = __args['token']

        try:
            __auth = jwt.decode(request.headers.get('Auth'), JWT["key"], algorithms="HS256")
        except:
            return {'result': 'Fail', "error": "Auth Failed"}, 401

        if __auth['user_type'] == 'employee':
            alba_db = pymysql.connect(user=DATABASES['user'],
                                      passwd=DATABASES['passwd'],
                                      host=DATABASES['db_host'],
                                      db=DATABASES['db_name'],
                                      charset=DATABASES["charset"])
            query = 'select * from workplace where employee_id = "{employee_id}" and id={id};'
            cursor = alba_db.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query.format(employee_id=__auth["id"], id=workplace_id))
            result = cursor.fetchall()

            if result:
                query = 'select ww.id, ww.employer_id, e.name, ww.hourly, ww.tax_included, ww.workplace_id ' \
                        'from workplace_workers as ww right outer join employer as e ON ww.employer_id=e.id ' \
                        'where workplace_id = {workplace_id}'

                print(query.format(workplace_id=workplace_id))
                cursor.execute(query.format(workplace_id=workplace_id))
                result = cursor.fetchall()

                return {'result': 'Success', 'data': result}

            else:
                return {'result': 'Fail', "error": "Auth Failed"}, 401
        else:
            return {'result': 'Fail', "error": "Auth Failed"}, 401


@Workplace.route('/<workplace_id>/hire')
class Hire(Resource):
    @Workplace.expect(model_workplace_hire)
    @Workplace.response(200, 'OK')
    @Workplace.response(400, 'Bad Request')
    @Workplace.response(401, 'Unauthorized')
    @Workplace.response(500, 'Internal Server Error')
    def post(self, workplace_id):
        '''매장 직원 추가'''
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('employer_id', type=str)
        __parser.add_argument('hourly', type=int)
        __parser.add_argument('tax_included', type=int)
        __args = __parser.parse_args()

        __token = __args['token']
        __employer_id = __args['employer_id']
        __hourly = __args['hourly']
        __tax_included = __args['tax_included']

        try:
            __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")
        except:
            return {'result': 'Fail', "error": "Auth Failed"}, 401

        if __auth['user_type'] == 'employee':
            __employee_id = __auth['id']
            print(__auth)

            alba_db = pymysql.connect(user=DATABASES['user'],
                                      passwd=DATABASES['passwd'],
                                      host=DATABASES['db_host'],
                                      db=DATABASES['db_name'],
                                      charset=DATABASES["charset"])

            cursor = alba_db.cursor(pymysql.cursors.DictCursor)

            max_id_query = 'select max(id) as max From workplace_workers;'
            cursor.execute(max_id_query)
            result = cursor.fetchall()
            try:
                __id = int(result[0]['max']) + 1
            except:
                __id = 1

            cursor = alba_db.cursor(pymysql.cursors.DictCursor)
            query = 'insert into workplace_workers values ({id},"{employer_id}","{hourly}", {tax_indcluded}, {workplace_id});'

            try:
                cursor.execute(query.format(id=__id,
                                            employer_id=__employer_id,
                                            hourly=__hourly,
                                            tax_indcluded=__tax_included,
                                            workplace_id=workplace_id
                                            ))
                alba_db.commit()
                return {'result': 'Success'}

            except:
                return {'result': 'Fail', "error": "Auth Failed"}

        else:
            return {'result': 'Fail', "error": "Auth Failed"}, 401


@Workplace.route('/<workplace_id>/fire')
class Fire(Resource):
    @Workplace.expect(model_workplace_fire)
    @Workplace.response(200, 'OK')
    @Workplace.response(400, 'Bad Request')
    @Workplace.response(401, 'Unauthorized')
    @Workplace.response(500, 'Internal Server Error')
    def delete(self, workplace_id):
        '''매장 직원 삭제'''
        __parser = reqparse.RequestParser()
        __parser.add_argument('token', type=str)
        __parser.add_argument('employer_id', type=str)
        __args = __parser.parse_args()

        __token = __args['token']
        __employer_id = __args['employer_id']

        try:
            __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")
        except:
            return {'result': 'Fail', "error": "Auth Failed"}, 401

        if __auth['user_type'] == 'employee':
            __employee_id = __auth['id']
            print(__auth)

            alba_db = pymysql.connect(user=DATABASES['user'],
                                      passwd=DATABASES['passwd'],
                                      host=DATABASES['db_host'],
                                      db=DATABASES['db_name'],
                                      charset=DATABASES["charset"])

            cursor = alba_db.cursor(pymysql.cursors.DictCursor)

            query = 'select * from workplace_workers where employer_id = "{employer_id}" and workplace_id={workplace_id};'

            cursor.execute(query.format(employer_id=__employer_id, workplace_id=workplace_id))
            result = cursor.fetchall()
            print(result)

            if result:
                try:
                    query = 'delete from workplace_workers where employer_id = "{employer_id}" and workplace_id={workplace_id};'
                    cursor.execute(query.format(employer_id=__employer_id, workplace_id=workplace_id))
                    alba_db.commit()
                    return {'result': 'Success'}
                except Exception as e:
                    return {'result': 'Fail (' + str(e) + ')'}
            else:
                return {'result': 'Fail (지울 데이터가 없음)'}

        else:
            return {"error": "Auth Failed"}, 401


@Workplace.route('/<workplace_id>/attendance')
class Attendance(Resource):
    @Workplace.expect(model_workplace_attendance)
    @Workplace.response(200, 'OK')
    @Workplace.response(400, 'Bad Request')
    @Workplace.response(401, 'Unauthorized')
    @Workplace.response(500, 'Internal Server Error')
    def patch(self, workplace_id):
        '''출근'''
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

        try:
            __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")
        except:
            return {'result': 'Fail', "error": "Auth Failed"}, 401

        if __auth['user_type'] == 'employer':
            __employer_id = __auth['id']
            print(__auth)

            alba_db = pymysql.connect(user=DATABASES['user'],
                                      passwd=DATABASES['passwd'],
                                      host=DATABASES['db_host'],
                                      db=DATABASES['db_name'],
                                      charset=DATABASES["charset"])

            cursor = alba_db.cursor(pymysql.cursors.DictCursor)
            query = 'UPDATE workplace_schedule ' \
                    'SET is_checked = 1 ' \
                    'WHERE employer_id="{employer_id}" AND workplace_id = {workplace_id} ' \
                    'AND YEAR(date) = {year} AND Month(date) = {month} AND DAY(date) = {day};'

            try:
                cursor.execute(query.format(employer_id=__employer_id,
                                            workplace_id=workplace_id,
                                            year=__year,
                                            month=__month,
                                            day=__day
                                            ))
                alba_db.commit()

                return {'result': 'Success'}
            except:
                return {'result': 'Fail', "error": "Auth Failed"}, 401

        else:
            return {'result': 'Fail', "error": "Auth Failed"}, 401


@Workplace.route('/<workplace_id>/leave')
class Leave(Resource):
    @Workplace.expect(model_workplace_leave)
    @Workplace.response(200, 'OK')
    @Workplace.response(400, 'Bad Request')
    @Workplace.response(401, 'Unauthorized')
    @Workplace.response(500, 'Internal Server Error')
    def patch(self, workplace_id):
        '''퇴근'''
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

        try:
            __auth = jwt.decode(__token, JWT["key"], algorithms="HS256")
        except:
            return {'result': 'Fail', "error": "Auth Failed"}, 401

        if __auth['user_type'] == 'employer':
            __employer_id = __auth['id']
            print(__auth)

            alba_db = pymysql.connect(user=DATABASES['user'],
                                      passwd=DATABASES['passwd'],
                                      host=DATABASES['db_host'],
                                      db=DATABASES['db_name'],
                                      charset=DATABASES["charset"])

            cursor = alba_db.cursor(pymysql.cursors.DictCursor)
            query = 'UPDATE workplace_schedule ' \
                    'SET is_checked = 2 ' \
                    'WHERE employer_id="{employer_id}" AND workplace_id = {workplace_id} ' \
                    'AND YEAR(date) = {year} AND Month(date) = {month} AND DAY(date) = {day};'

            try:
                cursor.execute(query.format(employer_id=__employer_id,
                                            workplace_id=workplace_id,
                                            year=__year,
                                            month=__month,
                                            day=__day
                                            ))
                alba_db.commit()

                return {'result': 'Success'}
            except:
                return {'result': 'Fail', "error": "Auth Failed"}, 401

        else:
            return {'result': 'Fail', "error": "Auth Failed"}, 401
