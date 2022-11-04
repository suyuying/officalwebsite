import sqlite3
import sys

import click  # 拿來做command line
from flask import current_app, g


# 連db -> 關db -> 建表schema->做init_db->做click command(initdb) ->註冊click command 到app &&  告訴app return response後要關db

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],  # db資訊重app context拿就好
            detect_types=sqlite3.PARSE_DECLTYPES  # Pass this flag value to the detect_types parameter of connect()
        )
        g.db.row_factory = sqlite3.Row  # squlite3的class attribute 定義Row 讓row return回來得表會以dict格式呈現
    return g.db  # 如果g有db直接return


def close_db(e=None):
    # pop沒東西也不會報錯，所以不用try
    db = g.pop('db', None)  # 把pop調的值return出來 這邊return一個squlite3物件
    if db is not None:
        db.close()

#準備用schema.sql做db，每次執行都會把db清掉重建
def init_db():
    #建立連線 -> 執行schema.sql
    db=get_db()
    #使用current_app proxy現在使用的appcontext
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    click.echo("Are you sure u want to init_db")
    action=input("input yes/no  ")
    if action == "yes" or action == "YES":
        init_db()
        # 跳出提示
        click.echo("initialize the database ")
    else:
        sys.exit("Don't want to initialize database")

#click 跟 close_db兩個執行的時間都在沒有app context情況下，要直接跟app註冊
def register_func_app(app):
    app.teardown_appcontext(close_db) #response回覆後，要關掉appcontext同時也要關掉db連線
    app.cli.add_command(init_db_command) #註冊comman


