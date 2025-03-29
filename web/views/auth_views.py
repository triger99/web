import functools
import secrets
import string
from ..db import get_databse_connection
from flask import Blueprint, url_for, render_template, flash, request, session, g , current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from ..forms import UserCreateForm, UserLoginForm
from flask_mail import Mail, Message


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/signup/', methods=('GET', 'POST'))
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        conn = get_databse_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE username=%s", (form.username.data,))
            user = cursor.fetchone()

            if not user: 
                password = generate_password_hash(form.password1.data)
                cursor.execute("INSERT INTO user (username, password, email,school_name) VALUES (%s ,%s ,%s,%s)", 
                               ( form.username.data,password, form.email.data, form.school_name.data))
                conn.commit()
                return redirect(url_for('main.index'))
            else:
                flash('이미 존재하는 사용자입니다.')
    return render_template('auth/signup.html', form=form)


@bp.route('/login/', methods=('GET', 'POST'))
def login():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        conn = get_databse_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE username=%s", (form.username.data,))
            user = cursor.fetchone()

            if not user:
                error = "존재하지 않는 사용자"
            elif not check_password_hash(user['password'], form.password.data):
                error = "비밀번호가 올바르지 않습니다."
            else:
                session.clear()
                session['user_id'] = user['id']
                _next = request.args.get('next', '')
                conn.close()
                return redirect(_next) if _next else redirect(url_for('main.index'))
        
        conn.close()
        flash(error)
    return render_template('auth/login.html', form=form)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        conn = get_databse_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE id=%s ", (user_id,))
            g.user = cursor.fetchone()
        conn.close()


@bp.route('/logout/')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            _next = request.url if request.method == 'GET' else ''
            return redirect(url_for('auth.login', next=_next))
        return view(*args, **kwargs)
    return wrapped_view


@bp.route('/find_id', methods=['POST', 'GET'])
def find_id():
    if request.method == 'POST':
        email = request.form.get('email')

        conn = get_databse_connection()
        cursor = conn.cursor()
        sql = "SELECT id FROM user WHERE email = %s"
        cursor.execute(sql, (email,))
        user = cursor.fetchone()
        conn.close()

        if user:
            flash(f"가입된 아이디는: {user['id']} 입니다.", "success")
        else:
            flash("가입된 아이디가 없습니다.", "danger")

        return redirect(url_for("auth.find_id"))

    return render_template("auth/find_id.html")

mail = Mail()


@bp.route("/find_password", methods=["POST", "GET"])
def find_password():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("id")

        conn = get_databse_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM user WHERE email = %s AND id = %s", (email, id))
        user = cursor.fetchone()
        conn.close()

        if user:
            #  새로운 임시 비밀번호 생성
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))

            #  비밀번호를 해시화하여 저장
            hashed_password = generate_password_hash(temp_password)
            conn = get_databse_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE user SET password = %s WHERE email = %s AND username = %s",
                           (hashed_password, email, username))
            conn.commit()
            conn.close()

            #  Flask-Mail을 통해 임시 비밀번호 전송
            msg = Message("비밀번호 재설정 안내",
                          sender=current_app.config["MAIL_DEFAULT_SENDER"],
                          recipients=[email])
            msg.body = f"임시 비밀번호: {temp_password}\n로그인 후 반드시 비밀번호를 변경하세요."
            mail.send(msg)

            flash("임시 비밀번호가 이메일로 전송되었습니다. 로그인 후 변경하세요.", "success")
        else:
            flash("입력한 정보와 일치하는 계정이 없습니다.", "danger")

        return redirect(url_for("auth.find_password"))

    return render_template("auth/find_password.html")
