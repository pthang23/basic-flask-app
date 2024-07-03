from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt

from db import db
from models import UserModel, BlocklistModel

from schemas import UserSchema

blp = Blueprint('users', __name__, description='Operations on users')


@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, request_data):
        request_data['password'] = pbkdf2_sha256.hash(request_data['password'])

        user = UserModel(**request_data)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(400, message='User name existed!')
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting new user!')

        return user


@blp.route('/user/<string:user_id>')
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @blp.response(200)
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while deleting user!')

        return {'message': 'User deleted!'}, 200


@blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200)
    def post(self, request_data):
        user = UserModel.query.filter(UserModel.username == request_data['username']).first()
        if user is not None and pbkdf2_sha256.verify(request_data['password'], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {'access_token': access_token, 'refresh_token': refresh_token}

        abort(401, message='Invalid credential!')


@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    @blp.response(200)
    def post(self):
        jti = get_jwt()['jti']
        jti_object = BlocklistModel(jti=jti)

        try:
            db.session.add(jti_object)
            db.session.commit()
        except IntegrityError:
            abort(400, message='You have logged out!')
        except SQLAlchemyError:
            abort(500, message='An error occurred while logout!')

        return {'message': 'Successfully logged out!'}


@blp.route('/refresh')
class RefreshAccessToken(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200)
    def post(self):
        user_id = get_jwt()['sub']
        non_fresh_access_token = create_access_token(identity=user_id, fresh=False)
        return {'access_token': non_fresh_access_token}