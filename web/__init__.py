
from flask import Flask
from web.db import create_tables
from flask_wtf import CSRFProtect
import config, os
# 블루프린트
from .views import main_views, question_views, auth_views , profile_views

def create_app():
    app = Flask(__name__)
    app.run(debug=True)
    app.config.from_object(config)


    create_tables()
    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(profile_views.bp)    
    

    # 필터
    from .filter import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime

    ## file 관련 설정
    ## upload folder 설정 
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')#현재 경로에서 uploads foleder 생성
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
        
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


    from flask_mail import Mail
    ## maiil 관련 설정
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587 ## tls port 
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = "your_email@gmail.com"
    app.config["MAIL_PASSWORD"] = "your_email_password"
    app.config["MAIL_DEFAULT_SENDER"] = "your_email@gmail.com"  

    mail = Mail(app)  
    return app
