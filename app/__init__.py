from flask import Flask
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.debug = True
    # Configuration (SQLAlchemy 설정 포함)
    app.config.from_object(Config)

    from app.database import init_db
    # DB 초기화
    init_db(app)

    from .views import register_api
    # blueprint 등록
    register_api(app)

    @app.route('/')
    def home():
        return "Hello, Flask!"

    return app
