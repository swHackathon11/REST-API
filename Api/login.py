import json
from flask_restplus import Namespace, fields, Resource

Login = Namespace('login', description='로그인')

model_login = Login.model('login data', {
    'user_id': fields.String(description='ID', required=True),
    'user_password': fields.String(description='Password', required=True)
})


@Login.route('')
class PostLogin(Resource):
    @Login.expect(model_login)
    @Login.response(200, 'OK')
    @Login.response(400, 'Bad Request')
    @Login.response(401, 'Unauthorized')
    @Login.response(500, 'Internal Server Error')
    def post(self):
        return 'Login'
