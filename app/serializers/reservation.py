from marshmallow import Schema, fields, validate


class ReservationSchema(Schema):
    user_id = fields.Int(description="고객 아이디", required=True)
    user_count = fields.Int(description="유저 수", required=True, validate=validate.Range(min=1, max=50000, error="유저 수는 50000 이하만 가능합니다."))
    start_datetime = fields.DateTime(description="시험 시작 시간", required=True)
    end_datetime = fields.DateTime(description="시험 종료 시간", required=True)
