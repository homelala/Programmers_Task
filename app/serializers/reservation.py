from marshmallow import Schema, fields

class ReservationSchema(Schema):
    user_id = fields.Int(description="고객 아이디", required=True)
    user_count = fields.Int(description="유저 수", required=True)
    start_datetime = fields.DateTime(description="시험 시작 시간", required=True)
    end_datetime = fields.DateTime(description="시험 종료 시간", required=True)


