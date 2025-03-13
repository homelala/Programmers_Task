# 🔥Programmers_Task🔥
# 📃 API 문서
1. local 실행 후 localhost:port/swagger/ 접속하면 확인 가능
2. [API 명세서](https://pinto-pike-1e8.notion.site/f8ac722b8c5e41879fdf7e9b0ca776d8?v=c9b2ca0ff7624918a080d54feb436258&pvs=74) swagger 외 Notion Page

# ⚙️ 개발환경 설정

## 로컬 환경설정

### 📌 1. 실행 configuration 설정

아래와 같이 configuration을 설정한다. (port 번호는 자유롭게 설정해도 된다, dir path 수정 필요!)

![Image](https://github.com/user-attachments/assets/40c01d53-0b67-4691-9724-7d43ef1fade4)

## 📌 2. Poetry 설치

1. 우선 poetry를 설치한다

```bash
curl -sSL https://install.python-poetry.org | python3 -

# 설치 제대로 됬는지 버전 확인
poetry --version
```

2. 의존성 설치

```bash
poetry install

poetry show
```

3. cmd + ,를 눌러 Interpreter에서 아래 사진과 같이 의존성이 설치되면 성공

![Image](https://github.com/user-attachments/assets/0c74ad50-4d6b-415a-b070-39b2a41ed756)


# 📌 3. Database 설정
1. 우선 psql을 설치

```bash
brew install postgresql

# 아래의 2개의 명령어중 1개를 입력해서 확인한다.
postgres -V 
postgres --version
```

2. psql 실행

```bash
# postgresql 실행 명령어
brew services start postgresql 

# postgresql 종료 명령어
brew services stop postgresql
```

3. psql 접속
아래 명령어를 입력하면 접속에 성공한다.
```bash
psql postgres
``` 

4. Role 생성 (role과 pw 지켜야함)

```bash
CREATE ROLE programmers WITH LOGIN PASSWORD 'programmers1234!';
```

5. DB 생성 (이름 및 owner 이름 지켜야함)

```bash
CREATE DATABASE programmersdb OWNER programmers;
```

6. 해당 role 및 DB 접속
```bash
psql -U programmers -d programmersdb

# 접속 후 아래 명령어를 치면 현재 테이블의 종류 확인 가능
\l
```


# 📌 4. 기타 추가 설정
**test 및 로컬에서 api를 실행하려고 할 때에는 1번에서 나왔던 brew services start postgresql를 실행시켜야 동작한다**
