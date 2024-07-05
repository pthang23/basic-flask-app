import os
from dotenv import load_dotenv

from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from db import db
from models import BlocklistModel
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.item import blp as ItemBlueprint
from resources.user import blp as UserBlueprint


def create_app(db_url=None):
    app = Flask(__name__)

    load_dotenv()

    app.config['PROPAGATE_EXCEPTION'] = True
    app.config['API_TITLE'] = 'Stores REST API'
    app.config['API_VERSION'] = 'v1'
    app.config['OPENAPI_VERSION'] = '3.0.3'
    app.config['OPENAPI_URL_PREFIX'] = '/'
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv('DATABASE_URL', 'sqlite:///data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    migrate = Migrate(app, db)

    app.config['JWT_SECRET_KEY'] = 'qwertyuiopasdfghjklzxcdfvgbnm'
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_token_in_blocklist(jwt_header, jwt_payload):
        match_jti = BlocklistModel.query.filter(BlocklistModel.jti == jwt_payload['jti']).first()
        return match_jti is not None

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {'error': 'token_revoked'}, 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'token_expired'}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'invalid_token'}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'authorized_required'}, 401

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        return {'admin': True} if identity == 2 else {'admin': False}

    @jwt.needs_fresh_token_loader
    def not_fresh_token_callback(jwt_header, jwt_payload):
        return {'error': 'not_fresh_token'}, 401

    api = Api(app)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(UserBlueprint)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')