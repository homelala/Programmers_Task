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
            def reservation(self):
                return ReservationFactory.create(user_id= UserFactory.create().id, user_count=50000, start_datetime=(datetime.utcnow() + timedelta(days=3)).replace(hour=1, minute=00, second=0, microsecond=0), end_datetime=(datetime.utcnow() + timedelta(days=3)).replace(hour=3, minute=00, second=0, microsecond=0), is_confirmed=True)

            def test_return_data(self, reservation, subject):
                assert subject.status_code == 200

                data = subject.json
                assert len(data) == 3 * 24

                for entry in data:
                    if reservation.start_datetime <= datetime.strptime(entry["datetime"], "%Y-%m-%dT%H:%M:%S") < reservation.end_datetime:
                        assert entry["user_count"] == 0
                        assert entry["status"] == "마감"
                    else:
                        assert datetime.strptime(entry["datetime"], "%Y-%m-%dT%H:%M:%S") >= (datetime.utcnow() + timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
                        assert entry["user_count"] == 50000
                        assert entry["status"] == "가능"

    class Context_confirm_reservation:
        @pytest.fixture
        def reservation(self):
            return ReservationFactory.create(user_id=UserFactory.create().id, user_count=30000, is_confirmed=False)

        @pytest.fixture
        def subject(self, reservation, client, headers):
            url = url_for("ReservationView:confirm_reservation", user_id=reservation.user_id, reservation_id=reservation.id)
            return client.patch(url, headers=headers)

        def test_예약확정(self, subject, reservation):
            assert subject.status_code == 201
            assert reservation.is_confirmed is True

        class Context_admin계정이_수정하려고할_경우:
            @pytest.fixture
            def admin_user(self):
                return UserFactory.create(is_admin=True)

            @pytest.fixture
            def subject(self, client, headers, reservation, admin_user):
                url = url_for("ReservationView:confirm_reservation", user_id=admin_user.id, reservation_id=reservation.id)
                return client.patch(url, headers=headers)

            def test_예약확정(self, subject, reservation):
                assert subject.status_code == 201
                assert reservation.is_confirmed is True

        class Context_타계정이_수정하려고_할경우:
            @pytest.fixture
            def other_user(self):
                return UserFactory.create()

            @pytest.fixture
            def subject(self, client, headers, reservation, other_user):
                url = url_for("ReservationView:confirm_reservation", user_id=other_user.id, reservation_id=reservation.id)
                return client.patch(url, headers=headers)

            def test_return_403(self, subject):
                assert subject.status_code == 403

    class Context_delete:
        @pytest.fixture
        def reservation(self):
            return ReservationFactory.create(user_id=UserFactory.create().id, user_count=30000)

        @pytest.fixture
        def subject(self, reservation, client, headers):
            url = url_for("ReservationView:delete", user_id=reservation.user_id, reservation_id=reservation.id)
            return client.delete(url, headers=headers)

        def test_예약삭제(self, subject, reservation):
            assert subject.status_code == 200
            assert reservation.deleted_at is not None

        class Context_이미확정된_예약일_경우:
            @pytest.fixture
            def reservation(self):
                return ReservationFactory.create(user_id=UserFactory.create().id, user_count=30000, is_confirmed=True)

            def test_return_400(self, reservation, subject):
                assert subject.status_code == 401

        class Context_admin계정이_삭제하려고할_경우:
            @pytest.fixture
            def admin_user(self):
                return UserFactory.create(is_admin=True)

            @pytest.fixture
            def subject(self, client, headers, reservation, admin_user):
                url = url_for("ReservationView:delete", user_id=admin_user.id, reservation_id=reservation.id)
                return client.delete(url, headers=headers)

            def test_예약삭제(self, subject, reservation):
                assert subject.status_code == 200
                assert reservation.deleted_at is not None

        class Context_타계정이_삭제하려고할_경우:
            @pytest.fixture
            def other_user(self):
                return UserFactory.create()

            @pytest.fixture
            def subject(self, client, headers, reservation, other_user):
                url = url_for("ReservationView:delete", user_id=other_user.id, reservation_id=reservation.id)
                return client.delete(url, headers=headers)

            def test_return_403(self, subject):
                assert subject.status_code == 403

    class Context_put:
        @pytest.fixture
        def reservation(self):
            return ReservationFactory.create(user_id=UserFactory.create().id, user_count=30000)

        @pytest.fixture
        def form(self, reservation):
            return {
                "user_id": reservation.user_id,
                "user_count": 40000,
                "start_datetime": (datetime.utcnow() + timedelta(days=3)).isoformat(),
                "end_datetime": (datetime.utcnow() + timedelta(days=3, hours=3)).isoformat(),
            }

        @pytest.fixture
        def subject(self, test_app, client, headers, form, reservation):
            url = url_for("ReservationView:put", reservation_id=reservation.id)
            return client.put(url, data=json.dumps(form), headers=headers)

        def test_예약수정(self, subject, form, reservation):
            assert subject.status_code == 201

            reservation = Reservation.query.get(reservation.id)
            assert reservation.user_count == form["user_count"]
            assert reservation.start_datetime == datetime.fromisoformat(form["start_datetime"])
            assert reservation.end_datetime == datetime.fromisoformat(form["end_datetime"])

        class Context_이미확정된_예약일_경우:
            @pytest.fixture
            def reservation(self):
                return ReservationFactory.create(user_id=UserFactory.create().id, user_count=30000, is_confirmed=True)

            def test_return_400(self, reservation, subject):
                assert subject.status_code == 401

        class Context_타계정이_수정할_경우:
            @pytest.fixture
            def other_user(self):
                return UserFactory.create()

            @pytest.fixture
            def form(self, form, other_user):
                form.update({"user_id": other_user.id})
                return form

            @pytest.fixture
            def subject(self, client, headers, reservation, other_user, form):
                url = url_for("ReservationView:put", reservation_id=reservation.id)
                return client.put(url, data=json.dumps(form), headers=headers)

            def test_return_403(self, subject):
                assert subject.status_code == 403

        class Context_어드민계정이_수정하는_경우:
            @pytest.fixture
            def admin_user(self):
                return UserFactory.create(is_admin=True)

            @pytest.fixture
            def form(self, form, admin_user):
                form.update({"user_id": admin_user.id})
                return form

            @pytest.fixture
            def subject(self, client, headers, reservation, admin_user, form):
                url = url_for("ReservationView:put", reservation_id=reservation.id)
                return client.put(url, data=json.dumps(form), headers=headers)

            def test_예약수정(self, subject, form, reservation):
                assert subject.status_code == 201

                reservation = Reservation.query.get(reservation.id)
                assert reservation.user_count == form["user_count"]
                assert reservation.start_datetime == datetime.fromisoformat(form["start_datetime"])
                assert reservation.end_datetime == datetime.fromisoformat(form["end_datetime"])

        class Context_인원이찬_시간으로_수정하는_경우:
            @pytest.fixture
            def already_reservation(self, form):
                return ReservationFactory.create(user_id=UserFactory.create().id, user_count=40000, start_datetime=form["start_datetime"], end_datetime = form["end_datetime"], is_confirmed=True)

            def test_return_400(self, already_reservation, subject):
                assert subject.status_code == 400