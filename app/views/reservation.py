from flask_apispec import use_kwargs, doc, marshal_with
from flask_classful import FlaskView, route

from app.serializers import marshal_empty
from app.serializers.error import ApiErrorSchema
from app.serializers.reservation import ReservationSchema, ReservationListSchema, ReservationUserSchema, \
    AvailableReservationSchema
from app.service.reservation import ReservationService


class ReservationView(FlaskView):
    decorators = (doc(tags=["Reservation"]),)

    @doc(summary="예약 목록 조회")
    @route("/list", methods=["GET"])
    @use_kwargs(ReservationUserSchema, locations=["query"])
    @marshal_with(ReservationListSchema(many=True), code=200)
    def get_reserved_list(self, user_id):
        return ReservationService.get_reservations(user_id), 200

    @doc(summary="예약하기")
    @route("/", methods=["POST"])
    @use_kwargs(ReservationSchema, locations=["json"])
    @marshal_with(ApiErrorSchema, code=422, description="입력 정보가 유효하지 않습니다.")
    @marshal_with(ApiErrorSchema, code=400, description="예약 가능 인원이 부족합니다.")
    @marshal_empty(code=200)
    def reserve(self, user_id, user_count, start_datetime, end_datetime):
        ReservationService.create_reservation(user_id, user_count, start_datetime, end_datetime)
        return "", 200


    @doc(summary="예약 가능 일정 조회")
    @route("/schedule", methods=["GET"])
    @marshal_with(AvailableReservationSchema(many=True), code=200)
    def get_available_schedule(self):
        return ReservationService.get_available_schedule(), 200


    @doc(summary="예약 확정")
    @route("/confirm/<user_id>/<reservation_id>", methods=["PATCH"])
    @marshal_with(ApiErrorSchema, code=403, description="예약 권한이 없습니다.")
    @marshal_empty(code=201)
    def confirm_reservation(self, user_id, reservation_id):
        ReservationService.confirm_reservation(user_id, reservation_id)
        return "", 201