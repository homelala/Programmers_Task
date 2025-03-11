import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from app.database import db
from app.models.user import User

fake = Faker()

class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session  # SQLAlchemy 세션 연결
        sqlalchemy_session_persistence = "flush"  # 자동 커밋 설정

    name = factory.Faker("name")
    email = factory.Sequence(lambda n: f"user{n}_" + factory.Faker("email").generate({}))

