from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from webscrap_flask.user_auth import login_required
from webscrap_flask.db import get_db

bp = Blueprint('scrap', __name__, url_prefix='/')

@bp.route('/')
def index():
    db = get_db()
    url_list = db.execute(
	"SELECT p.id, title, url, created, user_id, username"
	"FROM post_urls p JOIN user u ON p.user_id = u.id"
	"ORDER BY created DESC"
     ).fetchall()

    return render_template('crud/index.html', url_lists=url_list)

