from datetime import datetime, timedelta

from marshmallow import Schema, fields, validate, validates, ValidationError, validates_schema


class ReservationSchema(Schema):
    user_id = fields.Int(description="고객 아이디", required=True)
    user_count = fields.Int(description="유저 수", required=True, validate=validate.Range(min=1, max=50000, error="유저 수는 50000 이하만 가능합니다."))
    start_datetime = fields.DateTime(description="시험 시작 일자 및 시간 YYYY-MM-DD HH:00", required=True, format="%Y-%m-%d %H", metadata={"example": (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d %H")})
    end_datetime = fields.DateTime(description="시험 종료 일자 및 시간 YYYY-MM-DD HH:00", required=True, format="%Y-%m-%d %H", metadata={"example": (datetime.utcnow() + timedelta(days=3, hours=1)).strftime("%Y-%m-%d %H")})

    @validates("start_datetime")
    def validate_start_datetime(self, value):
        min_date = datetime.utcnow().date() + timedelta(days=3)  # 오늘 + 3일

        if value.date() < min_date:
            raise ValidationError(f"시험 시작 시간은 {min_date} 이후여야 합니다.")

    @validates_schema
    def validate_end_datetime(self, data, **kwargs):
        start = data.get("start_datetime")
        end = data.get("end_datetime")

        if end < start + timedelta(hours=1):
            raise ValidationError("시험 종료 시간(end_datetime)은 시험 시작 시간(start_datetime)보다 최소 1시간 이후여야 합니다.", field_name="end_datetime")


class ReservationListSchema(Schema):
    id = fields.Int(description="예약 아이디")
    user_id = fields.Int(description="고객 아이디")
    user_count = fields.Int(description="유저 수")
    start_datetime = fields.DateTime(description="시험 시작 시간")
    end_datetime = fields.DateTime(description="시험 종료 시간")
    is_confirmed = fields.Bool(description="확정 여부")


class ReservationUserSchema(Schema):
    user_id = fields.Integer(description="고객 아이디")


class AvailableReservationSchema(Schema):
    datetime = fields.DateTime(description="예약 가능 시간")
    user_count = fields.Integer(description="예약 가능 인원")
    status = fields.String(description="예약 가능 여부")
