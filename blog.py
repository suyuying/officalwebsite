from flask import (
    g, redirect, url_for, flash, request, render_template, Blueprint
)
from werkzeug.exceptions import abort
from offical_website.auth import login_required  # 驗證g.user是否有東西
from offical_website.db import get_db

bp = Blueprint('blog', __name__)
# db用username撈資料做成user(dict)->user['id'] -> session['id']->撈user資料->放入g.user類屬性
# g.user['id']會被當作值填入post表裏的author_id欄位，後續修改 新增 都會用到g.user['id']去對post裡面author_id

# blog首頁show文章
@bp.route("/")
def index():
    db = get_db()
    # JOIN default is inner JOIN (兩邊都有才有列）
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template("blog/index.html", posts=posts)


@bp.route("/create", methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        # '' == None  (False 空值不是None 所以這邊要針對空值做阻擋)
        if not title:
            error = "title is required"
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title,body,author_id)'
                ' VALUES (?,?,?)',
                (title, body, g.user['id'])
            )
            db.commit()
        return redirect(url_for('blog.index'))
    return render_template("blog/create.html")


def get_post(id, check_author=True):

    post = get_db().execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()
    if post is None:
        abort(404, f"Post id {id} doesn't exist")
        # 如果你傳入false就可以看單篇，
    if check_author and post['author_id'] != g.user['id']:
        abort(403)
    return post

# 使用前面的get_post去取得合法的post(檢驗傳入id
@bp.route("/<int:id>/update", methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        if not title:
            error = "title is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title= ?, body= ?'
                ' WHERE id= ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))
    return render_template("blog/update.html", post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
