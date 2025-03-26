from flask import Blueprint


bp = Blueprint('file', __name__ , url_prefix='/file')


# file uplodaer
@bp.route('/uploader')
def file_uploader():
    return '<h2> file uplodaer <h2>'

