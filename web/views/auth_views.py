import functools
from ..db import get_databse_connection
from flask import Blueprint, url_for, render_template, flash, request, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from ..forms import UserCreateForm, UserLoginForm


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
                cursor.execute("INSERT INTO user (username, password, email) VALUES (%s ,%s ,%s)", 
                               (form.username.data,password, form.email.data))
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