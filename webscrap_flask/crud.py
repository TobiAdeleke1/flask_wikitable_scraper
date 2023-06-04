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
    url_lists = db.execute(
	"SELECT p.id, title, url, created, user_id, username"
	"FROM post_urls p JOIN user u ON p.user_id = u.id"
	"ORDER BY created DESC"
     ).fetchall()

    return render_template('crud/index.html', url_lists=url_lists)

@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        url_link = request.form.get('url')
        error = None

        if not title:
            error = 'A Title Is Required'
        
        if error is not None:
            flash(error)
        else:
            db= get_db()
            db.execute("INSERT INTO post_url values (?, ?, ?)",(title, url_link, g.user['id']))
            db.commit
            redirect(url_for('scrap.index'))
                
    return render_template('crud/create.html')


def get_post(id, check_author=True): # Util function 
    db = get_db()
    post = db.execute('SELECT p.id, p.title, p.url, created, username'
                      'FROM post_url p JOIN  user u on p.user_id = u.id'
                      'WHERE p.id = ?', (id,)).fetchone()
    if post is None:
        abort(404, f'This user with id={id} does not Exist')
       
    if check_author and post['user_id'] != g.user.get('id'):
        abort(403)
    return post 


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        url_post = request.form.get('url_post')
        error = None
        
        if not title:
            error = 'A Title Is Required'

        if error is not None:
            flash(error)
        else:
            db= get_db()
            db.execute('UPDATE post_url p SET VALUES title = ?, url_post=?'
                       'WHERE p.id= ?', (title,url_post,id)
                       )
            db.commit()

            return redirect(url_for('scrap.index'))
        
    render_template('crud/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post_url WHERE id=?",(id,))
    db.commit()
    return redirect(url_for('scrap.index'))
