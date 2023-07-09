from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory, current_app
)
from werkzeug.exceptions import abort

from webscrap_flask.user_auth import login_required
from webscrap_flask.db import get_db
from webscrap_flask.utils.web.scrape_website import main_run

bp = Blueprint('scrap', __name__)


@bp.route('/')
def index():
    db = get_db()
    url_lists = db.execute(
	'''SELECT p.id, title, url, created_at, user_id, username
	  FROM 
      post_urls p 
      JOIN user u ON p.user_id = u.id
	  ORDER BY created_at DESC;
    '''
     ).fetchall()

    return render_template('crud/index.html', url_lists=url_lists)

@bp.route('/create', methods=('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        url_post = request.form.get('url_post')
        error = None
        
        if not title:
            error = 'A Title Is Required'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute('''INSERT INTO post_urls (title, url, user_id) 
                           values (?, ?, ?);
                        ''',(title, url_post, g.user['id']))
            db.commit()
            
            # going into feature
            filename, storage_url = main_run(url_post,  current_app.config['UPLOAD_FOLDER'])
            if '.xlsx' not in storage_url: # if the file was create
                flash(storage_url)
                return redirect(url_for('scrap.index'))
            else:
                
                db.execute(''' INSERT INTO document_urls (document_name, document_url, user_id)
                            VALUES (?,?,?);
                            ''',(filename,storage_url, g.user['id']))
                db.commit()
                return redirect(url_for('scrap.file_lists'))
    return render_template('crud/create.html')

@bp.route('/file_lists')
def file_lists():
    db = get_db()
    file_lists = db.execute(
	'''SELECT 
         d.id, 
         d.document_url,
         d.document_name,
         d.created_at,
         d.user_id,
         u.username
	   FROM 
       document_urls d
       INNER JOIN user u ON d.user_id = u.id
	  ORDER BY d.created_at DESC;
    '''
     ).fetchall()
    
    # file_lists = db.execute(
	# '''SELECT 
    #      d.id, 
    #      p.title, 
    #      p.url,
    #      d.document_url,
    #      d.created_at,
    #      d.user_id,
    #      u.username
	#    FROM 
    #    document_urls d
    #    INNER JOIN post_urls p on d.user_id = p.user_id
    #    INNER JOIN user u ON d.user_id = u.id
	#   ORDER BY d.created_at DESC;
    # '''
    #  ).fetchall()
    
    # for it in file_lists:
    #     print (dict(it))
    
    return render_template('crud/download.html', file_lists=file_lists)


@bp.route('/<int:id>/download')
@login_required
def download_file(id):
    document_item = get_download_path(id)
    return send_from_directory(current_app.config["UPLOAD_FOLDER"],document_item['document_name'])
    
def get_post(id, check_author=True): # Util function 
    db = get_db()
    post = db.execute('''SELECT 
                        p.id, 
                        p.title, 
                        p.url, 
                        created_at,
                        user_id, 
                        username
                        FROM post_urls p 
                      JOIN  user u on p.user_id = u.id
                      WHERE p.id = ?''', (id,)).fetchone()
    if post is None:
        abort(404, f'This user with id={id} does not Exist')
    if check_author and post['user_id'] != g.user['id']:
        abort(403)
    return post 

def get_download_path(id):
    db = get_db()
    document_name = db.execute('''SELECT document_name FROM document_urls
                                   WHERE id=? ''',(id,)).fetchone()
    if document_name is None:
        abort(404, f'This document request with id={id} does not Exist')
    return document_name


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
            db.execute('''UPDATE post_urls SET title = ?, url=?
                       WHERE id= ?''', (title,url_post,id)
                       )
            db.commit()

            return redirect(url_for('scrap.index'))
        
    return render_template('crud/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post_urls WHERE id=?",(id,))
    db.commit()
    return redirect(url_for('scrap.index'))

@bp.route('/document/<int:id>/delete', methods=('POST',))
@login_required
def doc_delete(id):
    get_download_path(id)
    db = get_db()
    db.execute("DELETE FROM document_urls WHERE id=?",(id,))
    db.commit()
    return redirect(url_for('scrap.file_lists'))