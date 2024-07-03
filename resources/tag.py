from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import StoreModel, ItemModel, TagModel

from schemas import PlainTagSchema, TagUpdateSchema, TagSchema, ItemTagSchema


blp = Blueprint('tags', __name__, description='Operation on tags')


@blp.route('/store/<string:store_id>/tag')
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags

    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema)
    def post(self, request_data, store_id):
        existed_tag = TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == request_data['name']).first()
        if existed_tag is not None:
            abort(400, message='Tag already exists in store!')

        request_data = {'store_id': int(store_id), **request_data}
        new_tag = TagModel(**request_data)
        try:
            db.session.add(new_tag)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting new tag!')

        return new_tag


@blp.route('/item/<string:item_id>/tag/<string:tag_id>')
class TagItemLink(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        item.tags.append(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting new tag!')

        return tag

    @blp.response(200, ItemTagSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        item.tags.remove(tag)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message='An error occurred while inserting new tag!')

        return {'message': 'Remove tag from item!', 'item': item, 'tag': tag}


@blp.route('/tag/<string:tag_id>')
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @blp.response(200, description='Delete a tag with no linked item.')
    @blp.response(404, description='Tag not found!')
    @blp.response(400, description='Exist at least one item link with tag!')
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if len(tag.items) == 0:
            db.session.delete(tag)
            db.session.commit()

        abort(400, message='Could not delete tag. Make sure no item link with this tag.')