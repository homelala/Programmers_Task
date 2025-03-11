from datetime import datetime, timedelta

import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.database import db
from app.models.reservation import Reservation
from app.tests.factories.user import UserFactory


class ReservationFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Reservation
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    user_id = factory.SubFactory(UserFactory)
    start_datetime = factory.LazyFunction(lambda: datetime.utcnow())
    end_datetime = factory.LazyAttribute(lambda obj: obj.start_datetime + timedelta(hours=1))  # 1시간 뒤
    is_confirmed = False
