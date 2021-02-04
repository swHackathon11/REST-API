from flask import Flask
from flask_restplus import Api
from flask_cors import CORS
from Api.login import Login
import os

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['JSON_AS_ASCII'] = False

CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app, version='1.0', title='알바꼼꼼 REST API', description='알바꼼꼼 백엔드 REST API 입니다!')

ns_login = api.namespace('/', description='로그인')


@app.route('/')
def main():
    return 'Hello, World!'

api.add_namespace(Login, '/login')                  # 로그인

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
