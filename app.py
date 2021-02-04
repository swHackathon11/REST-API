from flask import Flask
from flask_restplus import Api
from flask_cors import CORS
from Api.login import Login
from Api.register import Register
import os

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JSON_AS_ASCII'] = False

CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app, version='1.0', title='알바꼼꼼 REST API', description='알바꼼꼼 백엔드 REST API 입니다!')


@app.route('/')
def main():
    return 'Hello, World!'


# 로그인
api.add_namespace(Login, '/login')
# 회원가입
api.add_namespace(Register, '/register')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
