import pymysql
import pymysql.cursors


from datetime import datetime
from flask import Blueprint, render_template, request, url_for, g , abort
from werkzeug.utils import redirect
from ..forms import QuestionForm
from ..views.auth_views import login_required
from ..db import get_databse_connection


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
    




@bp.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    "질문 생성"
    form = QuestionForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        conn = get_databse_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        sql = """
            INSERT INTO question (subject, content, create_date , user_id)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql, (form.subject.data, form.content.data, datetime.now(), g.user['id']))

        conn.commit()
        cursor.close()
        conn.close()

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

## READE 
@bp.route('/question/detail/<int:question_id>/', methods=['GET'])
def detail(question_id):
    question = get_object_or_404(question_id) 
    return render_template('question/question_detail.html', question=question)


# 수정된 질문을 처리하는 뷰
@bp.route('/question/detail/<int:question_id>/', methods=['GET', 'POST'])
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



## DELETE 
@bp.route('/question/delete/<int:question_id>/', methods=['POST'])
def delete(question_id):
    conn = get_databse_connection()
    with conn.cursor() as cursor:
        cursor.execute('DELETE FROM question WHERE id = %s', (question_id , ))
        conn.commit()
    
    return redirect(url_for('question._list'))


@bp.route('/question/search/', methods=['GET'])
def search():
    search_query = request.args.get('search', '')
    search_type = request.args.get('search_type', 'both')
    
    # 검색어가 있을 경우 DB에서 검색
    if search_query:
        conn = get_databse_connection()
        cursor = conn.cursor()

        if search_type == 'subject':
            sql = "SELECT * FROM question WHERE subject LIKE %s"
            cursor.execute(sql, ('%' + search_query + '%',))
        elif search_type == 'content':
            sql = "SELECT * FROM question WHERE content LIKE %s"
            cursor.execute(sql, ('%' + search_query + '%',))
        else:  # both
            sql = "SELECT * FROM question WHERE subject LIKE %s OR content LIKE %s"
            cursor.execute(sql, ('%' + search_query + '%', '%' + search_query + '%'))

        questions = cursor.fetchall()

        # 검색 결과가 있을 경우
        if questions:
            return render_template('question/question_detail.html', questions = questions)
    
    # 검색 결과가 없으면 질문 목록 페이지로 이동
    return redirect(url_for('question._list'))
