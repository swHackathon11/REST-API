import json
from flask_restplus import Namespace, fields, Resource

Register = Namespace('register', description='회원가입')

model_register = Register.model('Register Model', {
    'user_id': fields.String(description='ID', required=True),
    'user_password': fields.String(description='Password', required=True),
    'user_name': fields.String(description='User Name', required=True),
    'user_type': fields.String(description='User Type', required=True),
})

model_check_id = Register.model('Check Id Model', {
    'user_id': fields.String(description='ID', required=True),
})


@Register.route('')
class PostRegister(Resource):
    @Register.expect(model_register)
    @Register.response(200, 'OK')
    @Register.response(400, 'Bad Request')
    @Register.response(401, 'Unauthorized')
    @Register.response(500, 'Internal Server Error')
    def post(self):
        return 'Register'


@Register.route('/check')
class PostRegister(Resource):
    @Register.expect(model_check_id)
    @Register.response(200, 'OK')
    @Register.response(400, 'Bad Request')
    @Register.response(401, 'Unauthorized')
    @Register.response(500, 'Internal Server Error')
    def post(self):
        return 'Register'
