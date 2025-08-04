# app.py
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import os
from contextlib import contextmanager
from datetime import datetime

app = Flask(__name__)

<<<<<<< HEAD
=======

>>>>>>> main
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


# 配置日志系统
def setup_logger():
    # 创建logs目录如果不存在
    if not os.path.exists('logs'):
        os.mkdir('logs')

    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )

    # 创建RotatingFileHandler，每个日志文件最大1MB，保留3个备份
    file_handler = RotatingFileHandler(
        'logs/auth_system.log',
        maxBytes=1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 添加到应用日志器
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)


# 初始化日志系统
setup_logger()


@contextmanager
def get_db_connection():
    connection = pymysql.connect(**DB_CONFIG)
    try:
        yield connection
    finally:
        connection.close()


def log_operation(user_id, action, status, req):
    """记录用户操作日志到文件"""
    log_message = (
        f"ACTION: {action.upper()}, "
        f"STATUS: {status.upper()}, "
        f"USER_ID: {user_id or 'Unknown'}, "
        f"IP: {req.remote_addr}, "
        f"USER_AGENT: {req.headers.get('User-Agent', 'Unknown')}, "
        f"TIMESTAMP: {datetime.now().isoformat()}"
    )
    app.logger.info(log_message)


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
            log_operation(user['id'], 'login', 'success', request)
            return render_template('success.html', username=user['username'])
        else:
            # 记录失败的登录尝试
            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id FROM users WHERE username = %s",
                        (username,)
                    )
                    user = cursor.fetchone()
            user_id = user['id'] if user else None
            log_operation(user_id, 'login', 'failed', request)
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
                    user_id = cursor.lastrowid
                    conn.commit()
            log_operation(user_id, 'register', 'success', request)
            flash('注册成功，请登录', 'success')
            return redirect(url_for('login'))
        except pymysql.Error as e:
            log_operation(None, 'register', 'failed', request)
            flash(f'注册失败: {e.args[1]}', 'error')

    return render_template('register.html')


@app.route('/logout')
def logout():
    log_operation(None, 'logout', 'success', request)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)

