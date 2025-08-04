# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import os
from contextlib import contextmanager

app = Flask(__name__)


"""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# 数据库配置
DB_CONFIG = {
    'host': '192.168.146.129',
    'user': 'root',
    'password': '123456',
    'db': 'auth_demo',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 用于闪现消息的秘钥
app.secret_key = os.urandom(24)


@contextmanager
def get_db_connection():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        yield connection
    finally:
        connection.close()


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users WHERE username = %s AND password = %s",
                    (username, password)
                )
                user = cursor.fetchone()

        if user:
            return render_template('success.html')
        else:
            flash('用户名或密码错误', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                        (username, password, email)
                    )
                    conn.commit()
            flash('注册成功，请登录', 'success')
            return redirect(url_for('login'))
        except pymysql.Error as e:
            flash(f'注册失败: {e.args[1]}', 'error')

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
