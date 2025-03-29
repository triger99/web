import pymysql
from config import DB_CONFIG

## sql 데이터 베이스 연동 
def get_databse_connection():

    connection =  pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        port=DB_CONFIG['port'],
        charset=DB_CONFIG['charset'],
        cursorclass=pymysql.cursors.DictCursor  # 딕셔너리 형태로 결과 반환
    )
    return connection


## USER table 생성 
def create_user_table():
    sql = """
        CREATE TABLE IF NOT EXISTS user(
         id INT AUTO_INCREMENT PRIMARY KEY,
         username VARCHAR(200) UNICODE NOT NULL,
         password VARCHAR(200) UNICODE NOT NULL,
         email VARCHAR(20) NOT NULL,
         school_name VARCHAR(255) NOT NULL,
         profile_image VARCHAR(255)

        )
    """
    conn = get_databse_connection()
    with conn.cursor() as cursor:
        cursor.execute(sql)
        conn.commit()
        conn.close()

def create_question_table():
    sql = """
        CREATE TABLE IF NOT EXISTS question(
         id INT AUTO_INCREMENT PRIMARY KEY,
         subject VARCHAR(200) NOT NULL,
         content TEXT NOT NULL,
         create_date DATETIME NOT NULL, 
         user_id INT,
        is_secret BOOLEAN NOT NULL DEFAULT 0,
         password VARCHAR(255) NULL,
         FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
        )
    """
    conn = get_databse_connection()
    with conn.cursor() as cursor:
        cursor.execute(sql)
        conn.commit()
        conn.close()

def create_file_table():
    sql = """
        CREATE TABLE IF NOT EXISTS file(
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255), 
            data LONGBLOB,
            question_id INT,
            FOREIGN KEY (question_id) REFERENCES question(id) ON DELETE CASCADE 
        )
    """
    conn = get_databse_connection()
    with conn.cursor() as cursor:
        cursor.execute(sql)
        conn.commit()
        conn.close()

def create_tables():
    create_user_table()
    create_question_table()
    create_file_table()