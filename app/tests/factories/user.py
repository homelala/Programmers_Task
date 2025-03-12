import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker

from app.database import db
from app.models.user import User

fake = Faker()


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    name = factory.Faker("name")
    email = factory.Sequence(lambda n: f"user{n}_" + factory.Faker("email").generate({}))
