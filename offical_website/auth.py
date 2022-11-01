import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from offical_website.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')  # name is passed as the second arg


@bp.route('/register', methods=['GET', 'POST'])  # GET打進來回註冊頁面，post近來寫db
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        # flask缺點再不能預設檢查
        if not username:
            error = "username is required"
        if not password:
            error = "password is required"
        # 如果檢查都沒有錯誤 把資訊放入table
        if error is None:
            try:
                db.execute(  # insert的格式跟以前python用%s寫東西很像
                    "INSERT INTO user (username,password) VALUES (?,?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already reigstered"
            else:  # 沒有出錯的話
                return redirect(url_for("auth.login"))
        flash(error)  # flash() stores messages that can be retrieved when rendering the templatess.
    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        # 查詢
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username=?', (username,)
        ).fetchone()  # 回row 裡面用dict包,cloumn name是key

        if user is None:
            error = "Incorrect username"
        elif not check_password_hash(user['password'], password):
            error = "Incorrect password"
        if error is None:
            session.clear()  # 清掉重複登入 seesion是會跨request的 持續一定時間 Default session lifetime is 31 days
            session['user_id'] = user['id']  # 用table給的id登記value session會把id加密回傳
            return redirect(url_for('index'))
        flash(error)
    return render_template('auth/login.html')


@bp.before_app_request #這邊用成berfore_request會導致整個認證功能爆掉 g.user都會是none!!
# 任何url都要區分使用者是否是以登入狀態 如果是登入會在request之前確認，並產生g.user的值
def load_logged_in_user():
    user_id = session.get('user_id')  # session是跨request
    if user_id is None:
        g.user = None  # g理論上就不會有劉資料，這邊用這個格式作為namespace，其實就是往app物件g 填入物件屬性的方法
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE ID= ?', (user_id,)
        ).fetchone()  # __init__有設定squlite3.Row讓查到東西以dict格式return回來


@bp.route('/logout')
def logout():
    session.clear()  # 清掉跨request的session紀錄
    return redirect(url_for('index'))


# 實際上會把每個view包裝起來，並確認使用者是g.user是有資料的，有就可以直接拿到該view 沒有回login，前面的function有先檢查一次g.user
# 所以這個高級函示會在包 一次view
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)  # 如果有登入，就執行一班view

    return wrapped_view
