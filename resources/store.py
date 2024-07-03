import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel, ItemModel

from schemas import StoreSchema

blp = Blueprint('stores', __name__, description='Operations on stores')


@blp.route('/store')
class StoreList(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, request_data):
        new_store = StoreModel(**request_data)

        try:
            db.session.add(new_store)
            db.session.commit()
        except IntegrityError:
            abort(400, message='Store name existed!')
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting new item!')

        return new_store


@blp.route('/store/<string:store_id>')
class Store(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    @jwt_required()
    @blp.response(200)
    def delete(self, store_id):
        jwt = get_jwt()
        if not jwt.get('admin') is True:
            abort(401, message='Permission denied!')

        store = StoreModel.query.get_or_404(store_id)
        try:
            db.session.delete(store)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while deleting an item!')

        return {'message': 'Store deleted!'}