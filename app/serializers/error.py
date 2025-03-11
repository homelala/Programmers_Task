from marshmallow import fields, Schema


class ApiErrorSchema(Schema):
    status_code = fields.Integer(data_key="code", required=True)
    message = fields.String()