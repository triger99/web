
from flask import Flask
from web.db import create_tables
import config
from flask_wtf import CSRFProtect

def create_app():
    app = Flask(__name__)
    app.run(debug=True)
    app.config.from_object(config)


    create_tables()
    # 블루프린트
    from .views import main_views, question_views, auth_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(question_views.bp)
    app.register_blueprint(auth_views.bp)

    # 필터
    from .filter import format_datetime
    app.jinja_env.filters['datetime'] = format_datetime

    return app
