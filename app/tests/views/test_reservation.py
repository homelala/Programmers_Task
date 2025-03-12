import json
from datetime import datetime, timedelta

import pytest
from flask import url_for

from app.tests.factories.reservation import ReservationFactory
from app.tests.factories.user import UserFactory
from app.models.reservation import Reservation


class Describe_ReservationView:
    class Context_get_reserved_list:
        @pytest.fixture
        def reservations(self, user):
            return ReservationFactory.create_batch(3, user_id=user.id, user_count=10000)

        @pytest.fixture
        def user(self):
            return UserFactory.create()

        @pytest.fixture
        def subject(self, reservations, client, headers, user):
            url = url_for("ReservationView:get_reserved_list")
            return client.get(url, headers=headers, query_string={"user_id": user.id})

        def test_예약목록조회(self, subject, user, reservations):
            assert subject.status_code == 200
            assert len(subject.json) == len(reservations)

        class Context_어드민계졍인_경우:
            @pytest.fixture
            def admin_user(self):
                return UserFactory.create(is_admin=True)

            @pytest.fixture
            def subject(self, reservations, client, headers, admin_user):
                url = url_for("ReservationView:get_reserved_list")
                return client.get(url, headers=headers, query_string={"user_id": admin_user.id})

            def test_예약목록조회(self, subject, reservations):
                assert subject.status_code == 200
                assert len(subject.json) == len(reservations)

    class Context_reserve:
        @pytest.fixture
        def user(self):
            return UserFactory.create()

        @pytest.fixture
        def form(self, user):
            return {
                "user_id": user.id,
                "user_count": 30000,
                "start_datetime": (datetime.utcnow() + timedelta(days=3)).isoformat(),
                "end_datetime": (datetime.utcnow() + timedelta(days=3, hours=3)).isoformat(),
            }

        @pytest.fixture
        def subject(self, test_app, client, headers, form):
            url = url_for("ReservationView:reserve")
            return client.post(url, data=json.dumps(form), headers=headers)

        def test_예약하기(self, subject, form):
            assert subject.status_code == 200

            reservations = Reservation.query.all()
            assert len(reservations) == 1
            assert reservations[0].user_id == form["user_id"]
            assert reservations[0].user_count == form["user_count"]
            assert reservations[0].start_datetime == datetime.fromisoformat(form["start_datetime"])
            assert reservations[0].end_datetime == datetime.fromisoformat(form["end_datetime"])

        class Context_시험전날에_예약하는_경우:
            @pytest.fixture
            def form(self):
                return {
                    "user_id": 1,
                    "user_count": 30000,
                    "start_datetime": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                    "end_datetime": (datetime.utcnow() + timedelta(hours=3)).isoformat(),
                }

            def test_return_422(self, subject):
                assert subject.status_code == 422

        class Context_예약가능인원_초과로_예약할_경우:
            @pytest.fixture
            def form(self):
                return {
                    "user_id": 1,
                    "user_count": 50001,
                    "start_datetime": (datetime.utcnow() + timedelta(days=3)).isoformat(),
                    "end_datetime": (datetime.utcnow() + timedelta(days=3, hours=3)).isoformat(),
                }

            def test_return_422(self, subject):
                assert subject.status_code == 422

        class Context_이미예약된_인원으로인해_초과된경우:
            @pytest.fixture
            def already_reserved(self, user):
                return ReservationFactory.create(
                    user_id=user.id,
                    user_count=30000,
                    start_datetime=(datetime.utcnow() + timedelta(days=3)).isoformat(),
                    end_datetime=(datetime.utcnow() + timedelta(days=3, hours=3)).isoformat(),
                    is_confirmed=True,
                )

            def test_return_400(self, already_reserved, subject):
                assert subject.status_code == 400

    class Context_get_available_schedule:
        @pytest.fixture
        def subject(self, client, headers):
            url = url_for("ReservationView:get_available_schedule")
            return client.get(url, headers=headers)

        def test_return_data(self, subject):
            assert subject.status_code == 200

            data = subject.json
            assert len(data) == 3 * 24

            for entry in data:
                assert datetime.strptime(entry["datetime"], "%Y-%m-%dT%H:%M:%S") >= (datetime.utcnow() + timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
                assert entry["user_count"] == 50000
                assert entry["status"] == "가능"

        class Context_5만명이상_신청된_예약이_있을_경우:
            @pytest.fixture
            def reserved(self):
                return ReservationFactory.create(user_id= UserFactory.create().id, user_count=50000, start_datetime=(datetime.utcnow() + timedelta(days=3)).replace(hour=1, minute=00, second=0, microsecond=0), end_datetime=(datetime.utcnow() + timedelta(days=3)).replace(hour=3, minute=00, second=0, microsecond=0), is_confirmed=True)

            def test_return_data(self, reserved, subject):
                assert subject.status_code == 200

                data = subject.json
                assert len(data) == 3 * 24

                for entry in data:
                    if reserved.start_datetime <= datetime.strptime(entry["datetime"], "%Y-%m-%dT%H:%M:%S") < reserved.end_datetime:
                        assert entry["user_count"] == 0
                        assert entry["status"] == "마감"
                    else:
                        assert datetime.strptime(entry["datetime"], "%Y-%m-%dT%H:%M:%S") >= (datetime.utcnow() + timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
                        assert entry["user_count"] == 50000
                        assert entry["status"] == "가능"