from web.db import get_databse_connection


class Question:
    def __init__(self, id, subject, content, create_date, user_id, password=None, is_secret=False, user_name=None, update_date=None):
        self.id = id
        self.subject = subject
        self.content = content
        self.create_date = create_date
        self.user_id = user_id
        self.password = password
        self.is_secret = is_secret
        self.user_name = user_name
        self.update_date = update_date
    
    @staticmethod
    def get_question_by_id(question_id):
        conn = get_databse_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM question WHERE id = %s", (question_id,))
            result = cursor.fetchone()
            if result:
                return Question(*result)
            return None

    
    @staticmethod
    def get_question_by_subject(subject):
        conn = get_databse_connection()
        with conn.cursor() as cursor:  # 'conn.cursor' -> 'conn.cursor()'로 수정
            cursor.execute("SELECT * FROM question WHERE subject = %s", (subject,))
            result = cursor.fetchone()
            if result:
                return Question(*result)
            return None
        

class User:
    def __init__(self, id, username, password, email, school_name, profile_image=None):
        self.id = id
        self.username = username
        self.password = password
        self.email = email
        self.school_name = school_name
        self.profile_image = profile_image  # profile_image 추가
    
    @staticmethod
    def get_user_by_id(user_id):
        conn = get_databse_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                return User(*result)  # User 객체 생성 (profile_image도 함께 전달됨)
            return None

    @staticmethod
    def update_user(user_id, name, email, school, profile_image=None):
        conn = get_databse_connection()
        cursor = conn.cursor()

        sql = """
            UPDATE user SET username = %s, email = %s, school_name = %s, profile_image = %s WHERE id = %s
        """
        print(f"업데이트 실행: user_id={user_id}, username={name}, email={email}, school_name={school}, profile_image={profile_image}")  # 디버깅 로그 추가
        cursor.execute(sql, (name, email, school, profile_image, user_id))
        conn.commit()

        cursor.close()
        conn.close()
