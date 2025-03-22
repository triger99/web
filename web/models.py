from web.db import get_databse_connection


class Question:
    def __init__(self, id, subject, content, create_date, user_id):
        self.id = id
        self.subject = subject
        self.content = content
        self.create_data = create_date
        self.user_id = user_id
    
    @staticmethod
    def get_question_by_id(conn, question_id):
        conn = get_databse_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM question WHERE id = %s", (question_id,))
            result = cursor.fetchone()
            if result:
                return Question(*result)
            return None

    
    @staticmethod
    def get_question_by_subject(conn, subject):
        conn = get_databse_connection()
        with conn.cursor as cursor:
            cursor.execute("SELECT * FROM question WHERE subject =%s", (subject,))
            result = cursor.fetchone()
            if result:
                return Question(*result)
            return None


            