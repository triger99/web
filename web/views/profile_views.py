from flask import Blueprint , url_for , redirect, render_template , session, request
from ..views.auth_views import login_required
from ..db import get_databse_connection
from ..models import User
from ..forms import UserUpdateForm
bp = Blueprint('profile', __name__, url_prefix='/profile')



@bp.route('/my_profile', methods=['GET', 'POST'])
@login_required
def my_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))  # 세션이 없으면 로그인 페이지로 이동

    user = User.get_user_by_id(user_id)  #  사용자 정보 가져오기
    form = UserUpdateForm(obj=user)

    if form.validate_on_submit():
        print("폼이 제출됨")  # 디버깅용 출력
        User.update_user(user_id, form.username.data, form.email.data, form.school_name.data)
        return redirect(url_for('profile.my_profile'))
    
    print("폼 오류:", form.errors)  # 폼 검증 실패 시 오류 출력
    return render_template('profile/my_profile.html', form=form, user=user)  #  user 추가




@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    user = User.get_user_by_id(user_id)
    form = UserUpdateForm(obj=user)

    if form.validate_on_submit():
        User.update_user(user_id, form.username.data, form.email.data, form.school_name.data)
        return redirect(url_for('profile.my_profile'))
    
    return render_template('profile/edit_profile.html', form=form, user=user)



@bp.route('/search_user', methods=['GET'])
def search_user():
    username = request.args.get('username')
    if username:
        conn = get_databse_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM user WHERE username LIKE %s", ('%' + username + '%',))
            result = cursor.fetchall()
            users = [User(*row) for row in result]
            return render_template('profile/search_user.html', users=users) 
    return redirect(url_for('question.list'))