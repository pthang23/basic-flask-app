import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required

from db import db
from models import StoreModel, ItemModel

from schemas import ItemSchema, ItemUpdateSchema

blp = Blueprint('items', __name__, description='Operations on items')


@blp.route('/item')
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, request_data):

        new_item = ItemModel(**request_data)

        try:
            db.session.add(new_item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting new item!')

        return new_item


@blp.route('/item/<string:item_id>')
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    @blp.response(200)
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        try:
            db.session.delete(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while deleting an item!')

        return {'message': 'Item deleted!'}

    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, request_data, item_id):
        item = ItemModel.query.get(item_id)
        if item:
            item.name = request_data['name']
            item.price = request_data['price']
        else:
            item = ItemModel(id=item_id, **request_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting new item!')

        return item