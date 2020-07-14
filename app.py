from datetime import timedelta
from threading import Lock

from flask import Flask, jsonify, render_template
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_socketio import SocketIO

from config import db, BLACKLIST_TOKEN
from resource.token import TokenRefresh
from resource.users import UserLogin, UserLogout, UserRegister

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = "jhjhjhl3bhb3jjbjjhjhjhjhjjhgsfeifeifiefieifeifeifieifeifei"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=6000)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(seconds=6000)

api = Api(app)
jwt = JWTManager(app)
socketio = SocketIO(app)
#############################################################

@app.before_first_request
def create_tables():
    db.create_all()


@jwt.token_in_blacklist_loader
def token_in_blacklist_callback(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST_TOKEN


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'The token has expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error: str):
    return jsonify({
        'description': 'Invalid JWT. Header:Authorization:Bearer {token}'
    }), 422


@jwt.unauthorized_loader
def unauthorized_callback(error: str):
    return jsonify({
        'description': 'JWT not found. Header:Authorization:Bearer {token}'
    }), 401


@jwt.needs_fresh_token_loader
def needs_fresh_token_callback():
    return jsonify({
        'description': 'Fresh token required.'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'description': 'The token has been revoked. 😈',
        'error': 'token_revoked'
    }), 401


@jwt.user_claims_loader
def user_claims_callback(identity):
    if identity == 1:
        return {'is_admin': True}
    return {'is_admin': False}


api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(UserRegister, '/register')
api.add_resource(TokenRefresh, '/token_refresh')


######################SocketIO#######################################

@app.route('/')
def sessions():
    return render_template('session.html')


@socketio.on('ping')
def test_message1(message):
    app.logger.error('#########ping#########')


@socketio.on('pong')
def test_message2(message):
    app.logger.error('#########ping#########')


@socketio.on('connect')
def test_message3():
    app.logger.error('#########connect#########')


######################Run#######################################

# db.init_app(app)
# socketio.init_app(app)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')
