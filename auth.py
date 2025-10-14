#type:ignore 

import functools 
from flask import Flask,g,Blueprint,redirect,render_template,request,session,url_for,flash
from werkzeug.security import check_password_hash,generate_password_hash
from .db import get_db
import sqlite3



bp = Blueprint('auth', __name__,url_prefix = '/auth',template_folder="templates")

@bp.route('/register',methods = ('GET','POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'necessario um Username'
        if not password:
            error = 'necessario um password'
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user(username, password) VALUES (?,?)",
                    (username,generate_password_hash(password),))
                db.commit()
            except sqlite3.IntegrityError:
                error = f"usuario {username} ja esta registrado "
            else:
                return redirect(url_for("auth.login"))

        if error is not None:
            flash(error)

    return render_template('auth/register.hrml')

@bp.route('/login',methods = ('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

        if not username:
            error = 'necessario um Username'
        elif not  check_password_hash(user['password'],password):
            error = 'password incorreto'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash (error)
    return render_template('auth/login.hrml')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None

    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?',(user_id,)).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view