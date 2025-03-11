from flask_apispec import use_kwargs, doc, marshal_with
from flask_classful import FlaskView, route

from app.serializers import marshal_empty
from app.serializers.error import ApiErrorSchema
from app.serializers.reservation import ReservationSchema
from app.service.reservation import ReservationService


class ReservationView(FlaskView):
    decorators = (doc(tags=["Reservation"]),)

    @doc(summary="예약 목록 조회")
    @route("/", methods=["GET"])
    @marshal_empty(code=200)
    def get(self):
        return "", 200

    @doc(summary="예약하기")
    @route("/", methods=["POST"])
    @use_kwargs(ReservationSchema, locations=["json"])
    @marshal_with(ApiErrorSchema, code=422, description="예약 가능 인원이 부족합니다.")
    @marshal_with(ApiErrorSchema, code=400, description="예약 가능 인원이 부족합니다.")
    @marshal_empty(code=200)
    def reserve(self, user_id, user_count, start_datetime, end_datetime):
        ReservationService.create_reservation(user_id, user_count, start_datetime, end_datetime)
        return "", 200
