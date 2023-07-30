import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from webscrap_flask.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password: 
            error = 'Password is required.'

        if error is None:
            try: 
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?,?)",
                    (username,generate_password_hash(password))
                )
                db.commit()
          
            except db.IntegrityError:
                error = f"User {username} is already registered"
            else:
                return redirect(url_for("auth.login")) 
            
        flash(error)
 
    return render_template('auth/register.html')
    

@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None 

        db_user = db.execute("SELECT * FROM user WHERE username = ?", (username,)
                             ).fetchone()
 
        if db_user is None:
            error = 'Incorrect Username'
        elif not check_password_hash(db_user['password'], password):
            error = 'Incorrect Password'
        
        if error is None:
            session.clear()
            session['user_id'] = db_user['id'] 
            return redirect(url_for('scrap.index'))
        
        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_current_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        g.user = db.execute("SELECT * FROM user WHERE id = ?", (user_id,) 
                            ).fetchone()
    

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('scrap.index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs): 
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs) 
    return wrapped_view