import pymysql
import config

## sql 데이터 베이스 연동 
def get_databse_connection():
    connection = pymysql.connect(
        host = config.DB_HOST,
        user = config.DB_USER,
        password= config.DB_PASSWORD,
        database= config.DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor # 결과를 Dict형태로 반환 
    )
    return connection




## USER table 생성 
def create_user_table():
    sql = """
        CREATE TABLE IF NOT EXISTS user(
         id INT AUTO_INCREMENT PRIMARY KEY,
         username VARCHAR(200) UNICODE NOT NULL,
         password VARCHAR(200) UNICODE NOT NULL,
         email VARCHAR(20) UNIQUE NOT NULL
        )
    """
    conn = get_databse_connection()
    with conn.cursor() as cursor:
        cursor.execute(sql)
        conn.commit()
        conn.close()

# QUestion table 생성
def create_question_table():
    sql = """
        CREATE TABLE IF NOT EXISTS question(
         id INT AUTO_INCREMENT PRIMARY KEY,
         subject VARCHAR(200) NOT NULL,
         content TEXT NOT NULL,
         create_date DATETIME NOT NULL, 
         user_id INT,
         FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE   
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

