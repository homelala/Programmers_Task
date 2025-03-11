import json
from datetime import datetime

import pytest
from flask import url_for

from app.tests.factories.reservation import ReservationFactory
from app.tests.factories.user import UserFactory
from app.models.reservation import Reservation


class Describe_ReservationView:
    class Context_reserve:
        @pytest.fixture
        def user(self):
            return UserFactory.create()

        @pytest.fixture
        def form(self, user):
            return {
                "user_id": user.id,
                "user_count": 30000,
                "start_datetime": "2021-01-01 00:00",
                "end_datetime": "2021-01-01 01:00",
            }

        @pytest.fixture
        def subject(self, test_app, client, headers, form):
            url = url_for("ReservationView:reserve")
            return client.post(url, data=json.dumps(form), headers=headers)

        def test_예약하기(self, subject):
            assert subject.status_code == 200

            reservations = Reservation.query.all()
            assert len(reservations) == 1
            assert reservations[0].user_id == 1
            assert reservations[0].user_count == 30000
            assert reservations[0].start_datetime == datetime.strptime("2021-01-01 00:00", "%Y-%m-%d %H:%M")
            assert reservations[0].end_datetime == datetime.strptime("2021-01-01 01:00", "%Y-%m-%d %H:%M")

        class Context_예약가능인원_초과로_예약할_경우:
            @pytest.fixture
            def form(self):
                return {"user_id": 1, "user_count": 50001, "start_datetime": "2021-01-01 00:00", "end_datetime": "2021-01-01 01:00"}

            def test_예약가능인원_초과(self, subject):
                assert subject.status_code == 422

        class Context_이미예약된_인원으로인해_초과된경우:
            @pytest.fixture
            def already_reserved(self, user, form):
                return ReservationFactory.create(
                    user_id=user.id,
                    user_count=30000,
                    start_datetime=datetime.strptime(form["start_datetime"], "%Y-%m-%d %H:%M"),
                    end_datetime=datetime.strptime(form["end_datetime"], "%Y-%m-%d %H:%M"),
                    is_confirmed=True,
                )

            def test_이미예약된_인원으로인해_초과(self, already_reserved, subject):
                assert subject.status_code == 400