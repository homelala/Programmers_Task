from datetime import datetime

from app.database import db


class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_count = db.Column(db.Integer, nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

    def deleted(self):
        self.deleted_at = datetime.utcnow()

    @classmethod
    def live_objects(cls, *filters):
        query = cls.query.filter(cls.deleted_at.is_(None))  # 기본 필터
        if filters:
            query = query.filter(*filters)  # 추가 필터 적용
        return query
