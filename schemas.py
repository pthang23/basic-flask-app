from marshmallow import Schema, fields


class PlainStoreSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)


class PlainTagSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)


class PlainItemSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class TagUpdateSchema(Schema):
    name = fields.Str()
    store_id = fields.Integer()


class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    store_id = fields.Integer()


class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    # store_id = fields.Integer()
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)


class ItemSchema(PlainItemSchema):
    store_id = fields.Integer(required=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class ItemTagSchema(Schema):
     message = fields.Str()
     items = fields.Nested(ItemSchema)
     tags = fields.Nested(TagSchema)


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

