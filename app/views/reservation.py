from flask_apispec import use_kwargs, doc
from flask_classful import FlaskView, route
from app.database import db
from app.models.reservation import Reservation
from app.serializers import marshal_empty
from app.serializers.reservation import ReservationSchema

class ReservationView(FlaskView):
    decorators = (doc(tags=["Reservation"]), )
    @doc(summary="예약 목록 조회")
    @route("/", methods=["GET"])
    @marshal_empty(code=200)
    def get(self):
        return "", 200

    @doc(summary="예약하기")
    @route("/", methods=["POST"])
    @use_kwargs(ReservationSchema, locations=["json"])
    @marshal_empty(code=200)
    def reserve(self, user_id, user_count, start_datetime, end_datetime):
        reservation = Reservation(user_id=user_id, user_count=user_count, start_datetime=start_datetime, end_datetime=end_datetime)
        db.session.add(reservation)
        db.session.commit()
        return "", 200
