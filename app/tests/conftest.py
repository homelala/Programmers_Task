import psycopg2
import pytest
from app import create_app
from app.config import TestConfig
from app.database import db


import psycopg2
import pytest


@pytest.fixture(scope="session")
def test_database():
    conn = psycopg2.connect(dbname="postgres", user="programmers", password="programmers1234!", host="localhost", port="5432")
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = 'test_db' AND pid <> pg_backend_pid();
        """
    )
    cursor.execute("DROP DATABASE IF EXISTS test_db;")

    cursor.execute("CREATE DATABASE test_db;")

    cursor.close()
    conn.close()

    yield "test_db"  # 테스트 실행 동안 유지

    conn = psycopg2.connect(dbname="postgres", user="programmers", password="programmers1234!", host="localhost", port="5432")
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = 'test_db' AND pid <> pg_backend_pid();
        """
    )
    cursor.execute("DROP DATABASE IF EXISTS test_db;")

    cursor.close()
    conn.close()


@pytest.fixture(scope="session")
def test_app(test_database):
    """테스트용 Flask """
    app = create_app()
    app.config.from_object(TestConfig)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://programmers:programmers1234!@localhost:5432/{test_database}"

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function", autouse=True)
def app_context(test_app):
    ctx = test_app.app_context()
    ctx.push()
    yield
    ctx.pop()


@pytest.fixture
def client(test_app):
    """Flask 테스트 클라이언트"""
    return test_app.test_client()


@pytest.fixture
def headers():
    """테스트 요청에 사용될 헤더"""
    return {"Content-Type": "application/json"}
