import json
from flask_restplus import Namespace, fields, Resource

Register = Namespace('login', description='로그인')

model_register = Register.model('Register Data', {
    'user_id': fields.String(description='ID', required=True),
    'user_password': fields.String(description='Password', required=True),
    'user_name': fields.String(description='User Name', required=True),
    'user_type': fields.String(description='User Type', required=True),
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
