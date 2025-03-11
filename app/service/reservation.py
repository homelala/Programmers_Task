from sqlalchemy import func, and_

from app.database import db
from app.error import ApiError
from app.models.reservation import Reservation
from app.models.user import User


class ReservationService:
    @classmethod
    def _check_create_reservatioin(cls, start_time, end_time):
        reservation_user_count = Reservation.query.with_entities(func.sum(Reservation.user_count)).filter(and_(Reservation.start_datetime <= end_time, Reservation.end_datetime >= start_time, Reservation.is_confirmed == True)).scalar() or 0
        return reservation_user_count

    @classmethod
    def create_reservation(cls, user_id, user_count, start_datetime, end_datetime):
        if cls._check_create_reservatioin(start_datetime, end_datetime) + user_count > 50000:
            raise ApiError("예약 가능 인원이 부족합니다.", status_code=400)

        reservation = Reservation(user_id=user_id, user_count=user_count, start_datetime=start_datetime, end_datetime=end_datetime)
        db.session.add(reservation)
        db.session.commit()

    @classmethod
    def get_reservations(cls, user_id):
        user = User.query.filter(User.id == user_id).first()

        if user.is_admin:
            return Reservation.query.all()

        return Reservation.query.filter(Reservation.user_id == user_id).all()
