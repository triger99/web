import pymysql
import pymysql.cursors
import os

from datetime import datetime
from flask import Blueprint, render_template, request, url_for, g , abort, redirect,current_app , send_from_directory , session , flash
from ..forms import QuestionForm
from ..views.auth_views import login_required
from ..db import get_databse_connection
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import Question  

bp = Blueprint('question', __name__, url_prefix='/question')


@bp.route('/list/')
def _list():
    "질문 목록 조회"
    page = request.args.get('page', type=int, default=1)  # 페이지 번호
    per_page = 10

    # 데이터베이스 연결
    conn = get_databse_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # 질문 총 개수 조회
    cursor.execute("SELECT COUNT(*) FROM question")
    total_count = cursor.fetchone()['COUNT(*)']

    # 페이지네이션을 위한 OFFSET 및 LIMIT
    offset = (page - 1) * per_page
    cursor.execute("SELECT * FROM question ORDER BY create_date DESC LIMIT %s OFFSET %s", (per_page, offset))
    question_list = cursor.fetchall()

    # 커넥션 종료
    cursor.close()
    conn.close()

    # 페이지네이션 처리
    total_pages = (total_count + per_page - 1) // per_page  # 총 페이지 수 계산
    has_prev = page > 1
    has_next = page < total_pages
    prev_num = page - 1 if has_prev else None
    next_num = page + 1 if has_next else None
    page_nums = range(1, total_pages + 1)

    # 페이징 정보와 함께 템플릿 전달
    return render_template('question/question_list.html', 
                           question_list=question_list,
                           page=page, 
                           per_page=per_page,
                           total_count=total_count,
                           total_pages=total_pages,
                           has_prev=has_prev,
                           has_next=has_next,
                           prev_num=prev_num,
                           next_num=next_num,
                           page_nums=page_nums)
    



ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(files, question_id):
    "파일 저장"
    if files:
        conn = get_databse_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                sql = """
                    INSERT INTO file (filename, data, question_id)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(sql, (filename, file_data, question_id))
        conn.commit()
        cursor.close()
        conn.close()



def save_question(form):
    conn = get_databse_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    is_secret = request.form.get('is_secret') == 'on'
    password  = request.form.get('password') if is_secret else None
    hashed_password = generate_password_hash(password) if password else None

    sql = """
        INSERT INTO question (subject, content, create_date, user_id, is_secret, password)
        VALUES (%s, %s, %s, %s , %s , %s )
    """
    cursor.execute(sql, (form.subject.data, form.content.data, datetime.now(), g.user['id'], is_secret, hashed_password))
    question_id = cursor.lastrowid

    conn.commit()
    cursor.close()
    conn.close()
    return question_id


@bp.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    "질문 새성 "
    form = QuestionForm()

    if request.method == 'POST' and form.validate_on_submit():
        question_id = save_question(form)
        save_file(request.files.getlist('file'),question_id)
        return redirect(url_for('main.index'))
    return render_template('question/question_form.html', form=form)


def get_object_or_404(id):
    conn = get_databse_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    sql = """
        SELECT * FROM question WHERE id = %s
    """
    cursor.execute(sql, (id,))
    question = cursor.fetchone()

    # 데이터가 없으면 404 오류 반환
    if not question:
        abort(404)

    conn.close()
    return question



@bp.route('/<int:question_id>/check_password', methods=['GET', 'POST'])
def check_password(question_id):
    question = get_object_or_404(question_id)
    password = request.form.get('password')

    # 비밀번호 확인 POST 요청 처리
    if request.method == 'POST':
        if check_password_hash(question['password'], password):  # 비밀번호가 맞으면
            session[f'authorized_{question["id"]}'] = True  # 세션에 인증 정보 저장
            return redirect(url_for('question.detail', question_id=question['id']))  # 상세 페이지로 이동
        else:  # 비밀번호가 틀리면
            flash('비밀번호가 일치하지 않습니다.')
            return redirect(url_for('question.check_password', question_id=question['id']))  # 다시 check_password로 리디렉션

    # GET 요청 시, 비밀글 여부에 따라 다르게 처리
    return render_template('question/question_detail.html', question=question)




@bp.route('/detail/<int:question_id>/', methods=['GET'])
def detail(question_id):
    question = get_object_or_404(question_id)  # 질문을 가져옴
    

    ## 비밀 글 일 경우 session에서 인증 여부 확인 
    if question['is_secret'] and f'authorized_{question_id}' not in session:
        return redirect(url_for('question.check_password', question_id=question_id))

    # 데이터베이스 연결
    conn = get_databse_connection()

    # 커서 정의
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 파일 가져오기
    file_sql = "SELECT * FROM file WHERE question_id = %s"
    cursor.execute(file_sql, (question_id,))
    files = cursor.fetchall()  # 질문에 연결된 파일 리스트 가져오기
    
    cursor.close()  # 커서 닫기
    conn.close()    # 연결 닫기
    
   
    return render_template('question/question_detail.html', question=question, files=files)


# 수정된 질문을 처리하는 뷰
@bp.route('/detail/<int:question_id>/', methods=['GET', 'POST'])
def update(question_id):
    if request.method == 'POST':
        subject = request.form['subject']
        content = request.form['content']

        # 데이터베이스 연결 및 업데이트 실행
        conn = get_databse_connection()
        with conn.cursor() as cursor:
            cursor.execute('UPDATE question SET subject = %s, content = %s, update_date = NOW() WHERE id = %s',
                           (subject, content, question_id))
            conn.commit()

        # 수정 후 상세 페이지로 리다이렉트
        return redirect(url_for('question.detail', question_id=question_id))

    # GET 요청: 수정된 질문을 가져와서 템플릿에 전달
    question = get_object_or_404(question_id)
    return render_template('question/question_detail.html', question=question)

@bp.route('/download/<filename>', methods = ['GET'])
def file_download(filename):
    try:
        ## file server에서 반환
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        abort(404)

## DELETE 
@bp.route('/delete/<int:question_id>/', methods=['POST'])
def delete(question_id):
    conn = get_databse_connection()
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM question WHERE id = %s', (question_id , ))
        conn.commit()
    
    return redirect(url_for('question._list'))


@bp.route('/search/', methods=['GET'])
def search():
    search_query = request.args.get('search', '')
    search_type = request.args.get('search_type', 'both')
    page = request.args.get('page', type=int, default = 1)
    per_page = 10



    # 검색어가 있을 경우 DB에서 검색
    if search_query:
        conn = get_databse_connection()
        cursor = conn.cursor()

        if search_type == 'subject':
            sql = "SELECT COUNT(*) FROM question WHERE subject LIKE %s"
            count_sql = "SELECT * FROM question WHERE subject LIKE %s ORDER BY create_date DESC LIMIT %s OFFSET %s"
            cursor.execute(sql, ('%' + search_query + '%',))
        elif search_type == 'content':
            sql = "SELECT COUNT(*) FROM question WHERE content LIKE %s"
            count_sql =  "SELECT * FROM question WHERE content LIKE %s ORDER BY create_date DESC LIMIT %s OFFSET %s"
            sql = "SELECT * FROM question WHERE content LIKE %s"
            cursor.execute(sql, ('%' + search_query + '%',))
        else:  # both
            sql = "SELECT COUNT(*) FROM question WHERE subject LIKE %s OR content LIKE %s"
            count_sql = "SELECT * FROM question WHERE subject LIKE %s OR content LIKE %s ORDER BY create_date DESC LIMIT %s OFFSET %s"
            cursor.execute(sql, ('%' + search_query + '%', '%' + search_query + '%'))

        total_count = cursor.fetchone()['COUNT(*)']
        total_pages = (total_count + per_page - 1) // per_page 
        offset = (page - 1 ) * per_page

        if search_type == 'both':
            cursor.execute(count_sql , ('%' + search_query + '%', '%' + search_query, per_page, offset ))
        else:
            cursor.execute(count_sql, ('%' + search_query + '%', per_page, offset))

        question_list = cursor.fetchall()

        return render_template('question/question_list.html', 
                           question_list=question_list,
                           page=page, 
                           per_page=per_page,
                           total_count=total_count,
                           total_pages=total_pages,
                           has_prev=page > 1,
                           has_next=page < total_pages,
                           prev_num=page - 1 if page > 1 else None,
                           next_num=page + 1 if page < total_pages else None,
                           page_nums=range(1, total_pages + 1),
                           search_query=search_query,
                           search_type=search_type)