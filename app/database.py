import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base



db = SQLAlchemy()

def init_db(app):
    from app.models.user import User
    from app.models.reservation import Reservation
    # DB 초기화
    with app.app_context():
        db.init_app(app)
        db.drop_all() # 테이블 초기화
        db.create_all() # 테이블 자동 생성
        execute_sql_file('app/executeSQL.sql')  # SQL 파일 실행


def execute_sql_file(file_path):
    # 파일 경로가 프로젝트 루트에 있을 경우
    file_path = os.path.join(os.getcwd(), file_path)

    # SQL 파일을 읽고 실행
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            sql = file.read()

        # SQL 문 실행
        db.session.execute(text(sql))
        db.session.commit()
        print(f"SQL 파일 {file_path} 실행 완료.")
    else:
        print(f"SQL 파일 {file_path}을 찾을 수 없습니다.")
