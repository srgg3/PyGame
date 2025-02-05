import hashlib
import sqlite3

# Инициализация базы данных SQLite
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
conn.commit()


def hash_password(password): # С помощью hashlib можно хешировать строки и файлы, обеспечивая целостность данных и повышая безопасность паролей
    return hashlib.sha256(password.encode()).hexdigest()


def register(username, password): # проверка на логин + пароль
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone() is not None:
        return "Пользователь с таким именем уже существует."
    hashed_password = hash_password(password)
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    return "Регистрация прошла успешно!"


def login(username, password): #проверка на логин
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    if user is None:
        return "Пользователь не найден."
    if user[1] != hash_password(password):
        return "Неверный пароль."
    return "Вход выполнен успешно!"