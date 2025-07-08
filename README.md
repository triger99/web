# 📌 Flask 질문 게시판 웹 애플리케이션 (MySQL 연동)
## 🔐 프로젝트 개요
본 프로젝트는 Flask 웹 프레임워크와 MySQL 데이터베이스를 기반으로 구성된 기본적인 질문 게시판 웹 애플리케이션입니다. 사용자는 로그인한 상태에서 게시글(질문)을 생성(CREATE), 조회(READ), 수정(UPDATE), 삭제(DELETE)할 수 있으며, 키워드 기반 검색 기능도 포함되어 있습니다.

CSRF 방지와 보안 인증 강화를 위해 Flask-WTF와 Flask-Login을 적극 활용하였으며, Python의 with문을 통해 자원 누수를 방지하는 구조로 작성하였습니다.

## 🧰 사용 기술 스택
범주	기술
언어	Python 3.x
웹 프레임워크	Flask
프론트엔드	HTML, Jinja2, Bootstrap
데이터베이스	MySQL
폼 처리	Flask-WTF (CSRF Protection)
사용자 인증	Flask-Login
비밀번호 암호화	werkzeug.security (PBKDF2 기반 generate_password_hash)

## 🔑 핵심 기능
## ✅ 회원가입 및 로그인 (/auth/signup/, /auth/login/)
CSRF 보호를 위해 Flask-WTF 사용

werkzeug.security를 사용한 안전한 비밀번호 저장

중복 사용자 확인 및 에러 메시지 출력 (Flash 메시지)

## 📝 게시글(질문) CRUD
### 🔸 생성 /create/
로그인한 사용자만 접근 가능 (@login_required)

제목, 내용 입력을 받아 질문 등록

작성 시점과 사용자 ID 저장

### 🔸 조회 /list/
최신순 정렬

페이지네이션 (기본 10개씩)

총 페이지, 이전/다음 버튼 렌더링

### 🔸 수정 /question/detail/<int:question_id>/
GET: 기존 데이터 불러오기

POST: 입력값 DB 업데이트 (UPDATE question SET ...)

update_date 컬럼 추가 사용

### 🔸 삭제 /question/delete/<int:question_id>/
POST 방식으로만 처리

삭제 전 confirm() JS 경고창 구현

삭제 후 목록으로 리다이렉트

### 🔍 검색 /question/search/
제목 / 내용 / 제목+내용 옵션 제공

검색어를 기준으로 LIKE 문법을 통해 질문 조회

검색결과 없을 시 질문 목록으로 리다이렉트

### 🧠 보안 설계 요소
보안 항목	적용 방법
로그인 보호	@login_required 데코레이터 사용
CSRF 방지	Flask-WTF를 통한 자동 {{ form.csrf_token }} 처리
비밀번호 보호	generate_password_hash() 및 해시 비교
DB 연결 안전 관리	with conn.cursor() 구문으로 리소스 자동 해제
SQL Injection 방지	cursor.execute(sql, params) 구조로 파라미터 바인딩 처리

### 🔧 설치 및 실행 방법
bash
복사
편집
## 가상환경 생성 및 활성화 (선택)

```python
python -m venv venv
source venv/bin/activate  # 또는 venv\Scripts\activate
```

# 필수 패키지 설치
```shell
pip install flask pymysql flask-wtf flask-login
```

# 실행

```script
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```


### 🗃️ 데이터베이스 스키마 예시
```sql
CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(200) NOT NULL,
    email VARCHAR(200)
);

CREATE TABLE question (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    create_date DATETIME NOT NULL,
    update_date DATETIME,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

### 🧪 테스트 계정 예시
항목	값
아이디	testuser
비밀번호	test1234 (해시됨)

📎 참고자료
VSCode와 MySQL 연동: https://velog.io/@milkim0818/VS-code에서-MySQL-연동하기

Python with 문법 이해: https://projooni.tistory.com/entry/Python-with절-문법의-이해

Flask 공식문서: https://flask.palletsprojects.com

Flask-WTF: https://flask-wtf.readthedocs.io

MySQL 연결/해제 구조: conn = get_connection(); conn.close()

### 🧑‍💻 개발자 코멘트
with conn.cursor() 구문을 적극 활용하여 메모리 누수 및 MySQL 연결 미종료 이슈 방지

사용자 인증 및 폼 검증을 통해 최소한의 공격 벡터만을 노출

향후 답변 기능 추가 또는 JWT 기반 API 구현도 확장 가능

### 📌 향후 개선 사항 (TODO)
 질문 상세 페이지에 답변 기능 추가

 사용자 프로필 페이지 구현

 AJAX 기반 비동기 삭제/수정

 게시글 태그 및 필터 기능 도입

 XSS 대비 escape 처리 강화

