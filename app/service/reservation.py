from datetime import datetime, timedelta

from sqlalchemy import func

from app.database import db
from app.error import ApiError
from app.models.reservation import Reservation
from app.models.user import User


class ReservationService:
    @classmethod
    def _check_create_reservation(cls, start_datetime, end_datetime):
        reservation_user_count = Reservation.live_objects(Reservation.start_datetime < end_datetime, Reservation.end_datetime > start_datetime, Reservation.is_confirmed == True).with_entities(func.sum(Reservation.user_count)).scalar() or 0
        return reservation_user_count

    @classmethod
    def create_reservation(cls, user_id, user_count, start_datetime, end_datetime):
        if cls._check_create_reservation(start_datetime, end_datetime) + user_count > 50000:
            raise ApiError("예약 가능 인원이 부족합니다.", status_code=400)

        reservation = Reservation(user_id=user_id, user_count=user_count, start_datetime=start_datetime, end_datetime=end_datetime)
        db.session.add(reservation)
        db.session.commit()

    @classmethod
    def get_reservations(cls, user_id):
        user = User.query.filter(User.id == user_id).first()

        if user.is_admin:
            return Reservation.live_objects().all()

        return Reservation.live_objects(Reservation.user_id == user_id).all()

    @classmethod
    def get_available_schedule(cls):
        date_list = cls._get_date_dict()
        reservations = Reservation.live_objects(Reservation.start_datetime >= datetime.utcnow(), Reservation.is_confirmed == True).all()

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

    @classmethod
    def confirm_reservation(cls, user_id, reservation_id):
        user = User.query.get_or_404(user_id)
        reservation = Reservation.live_objects(Reservation.id == reservation_id).first_or_404()

        if user.is_admin or reservation.user_id == user.id:
            reservation.is_confirmed = True
            db.session.commit()
        elif reservation.user_id != user.id:
            raise ApiError("예약 권한이 없습니다.", status_code=403)

    @classmethod
    def delete_reservation(cls, user_id, reservation_id):
        user = User.query.get_or_404(user_id)
        reservation = Reservation.live_objects(Reservation.id == reservation_id).first()
        if reservation.is_confirmed:
            raise ApiError("예약 확정된 예약은 삭제할 수 없습니다.", status_code=401)

        if user.is_admin or reservation.user_id == user.id:
            reservation.deleted()
            db.session.commit()
        elif reservation.user_id != user.id:
            raise ApiError("예약 권한이 없습니다.", status_code=403)

    @classmethod
    def update_reservation(cls, reservation_id, user_id, user_count, start_datetime, end_datetime):
        user = User.query.get_or_404(user_id)
        reservation = Reservation.live_objects(Reservation.id == reservation_id).first_or_404()
        if reservation.is_confirmed:
            raise ApiError("예약 확정된 예약은 수정할 수 없습니다.", status_code=401)

        if user.is_admin or reservation.user_id == user_id:
            if cls._check_create_reservation(start_datetime, end_datetime) + user_count > 50000:
                raise ApiError("예약 가능 인원이 부족합니다.", status_code=400)

            reservation.user_count = user_count
            reservation.start_datetime = start_datetime
            reservation.end_datetime = end_datetime
            db.session.commit()
        else:
            raise ApiError("예약 권한이 없습니다.", status_code=403)
