--主要就兩個table,有註冊的使用者 user 跟 註冊使用者所創建的post
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
--index 是id cloumn 有 username and password
--語法: cloumnname 屬性 條件 特別語法
CREATE TABLE user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
--主要他怎麼reference user id 要看看
CREATE TABLE post(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
);
