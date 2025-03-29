from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, EmailField , SubmitField,FileField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class QuestionForm(FlaskForm):
    subject = StringField('제목', validators=[DataRequired('제목은 필수입력 항목입니다.')])
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수입력 항목입니다.')])



class UserCreateForm(FlaskForm):
    username = StringField('사용자 이름', validators=[DataRequired(), Length(min=3, max=25)])
    password1 = PasswordField('비밀번호', validators=[DataRequired(), Length(min=8),
                                                 EqualTo('password2', message='비밀번호가 일치하지 않습니다.')])
    password2 = PasswordField('비밀번호 확인', validators=[DataRequired()])
    email = EmailField('이메일', validators=[DataRequired(), Email()])
    school_name = StringField('학교 이름', validators=[DataRequired()])


class UserLoginForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('비밀번호', validators=[DataRequired()])

class UserUpdateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=30)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    school_name = StringField('School Name', validators=[Length(max=100)])
    profile_image = FileField('Profile Image')
    submit = SubmitField('Update')
