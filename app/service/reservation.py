from datetime import datetime, timedelta

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

    @classmethod
    def get_available_schedule(cls):
        date_list = cls._get_date_dict()
        reservations = Reservation.query.filter(Reservation.start_datetime >= datetime.utcnow(), Reservation.is_confirmed==True).all()

        for res in reservations:
            start_time = res.start_datetime.replace(minute=0, second=0, microsecond=0)  # 시간 단위로 맞춤
            end_time = res.end_datetime.replace(minute=0, second=0, microsecond=0)

            while start_time < end_time:
                key = start_time.strftime("%Y:%m:%d %H:%M")
                for entry in date_list:
                    if entry["datetime"].strftime("%Y:%m:%d %H:%M") == key:
                        entry["user_count"] -= res.user_count

                        if entry["user_count"] <= 0:
                            entry["status"] = "마감"
                            entry["user_count"] = 0

                start_time += timedelta(hours=1)

        return date_list

    @staticmethod
    def _get_date_dict():
        # 현재 시간 기준으로 3일간의 시간대 생성
        start_datetime = (datetime.utcnow() + timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
        date_list = [{"datetime": (start_datetime + timedelta(hours=i)).replace(second=0, microsecond=0), "user_count": 50000, "status": "가능"} for i in range(3 * 24)]
        return date_list