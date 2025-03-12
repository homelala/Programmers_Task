class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://programmers:programmers1234!@localhost/programmersdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    SERVER_NAME = "localhost"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://programmers:programmers1234!@localhost/test_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
