# type: ignore
from flask import (blueprints,flash,g,redirect,render_template,request,session,url_for)
from werkzeug.exceptions import abort
from .auth import login_required
from .db import get_db

bp = blueprints.Blueprint('blog',__name__,)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute('''
    SELECT
        P.id, title, body, created, author_id, username 
    FROM 
        post P JOIN user U ON P.author_id = U.id
    ORDER BY 
        created DESC''').fetchall()
    return render_template('blog/index.html',posts=posts)
    

@bp.route('/create',methods = ('GET','POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'precisar adicionar um titulo.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                'VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')  


def get_post(id, check_author=True):
    post = get_db().execute(
        
        'SELECT P.id, title, body, created, author_id, username ' 

        'FROM post P JOIN user u ON P.author_id = u.id ' 
        'WHERE P.id = ?',
        (id,)).fetchone()

    if post is None:
        abort(404, f"Post com id {id} não existe.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)
        
    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title necessario.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                
                'UPDATE post SET title = ?, body = ?'
                'WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))