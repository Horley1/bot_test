import sqlite3
import telebot
from requests import *
from json import *
import json
from fernet import *
import time
from datetime import datetime
bot = telebot.TeleBot('5199364372:AAGnaM9JbpyH2_JjTpCi1zb3EN5nWUtiwmE')
connect = sqlite3.connect('bot.db')

cursor = connect.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS data (
user_id INTEGER UNIQUE NOT NULL,
login STRING,
pass STRING,
token STRING,
last_marks STRING,
day INTEGER,
month INTEGER,
year INTEGER
);""")
connect.commit()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет! Если ты ещё не зарегался пиши: "/reg". Иначе пиши "/parse" для старта парсинга!')
@bot.message_handler(commands=['parse'])
def start_parsing(message):
    connect = sqlite3.connect('bot.db')
    cursor = connect.cursor()
    print(cursor.execute(f"SELECT * FROM data WHERE user_id={message.chat.id}").fetchone())
    if cursor.execute(f"SELECT * FROM data WHERE user_id={message.chat.id}").fetchone():
        bot.send_message(message.chat.id, 'Ты в базе данных! Начинаю парсинг.')
    else:
        bot.send_message(message.chat.id, 'Упс... Тебя нету базе данных. Напиши "/reg", чтобы зарегаться.')




@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Напиши: /start")

@bot.message_handler(commands=['reg'])
def reg(message):
    if not check_bd(message):
        bot.send_message(message.chat.id, "Напиши мне свой логин:")
        bot.register_next_step_handler(message, get_login)
    else:
        bot.send_message(message.chat.id, "Эййй, ты уже в базе!")



def check_bd(message):
    connect = sqlite3.connect('bot.db')
    cursor = connect.cursor()
    if cursor.execute(f"SELECT * FROM data WHERE user_id={message.chat.id}").fetchone():
        return True
    else:
        return False
def get_login(message):
    global login
    login = message.text
    bot.send_message(message.from_user.id, 'ОК. Теперь напиши мне свой пароль. ')
    bot.send_message(message.from_user.id, 'Пароль шифруется внутренней функцией Python, поэтому никто кроме него пароль не узнает!')
    bot.delete_message(message.chat.id, message.message_id)
    bot.register_next_step_handler(message, get_pass)


def get_pass(message):
    global password
    password = message.text
    bot.send_message(message.from_user.id, 'Принял. Сейчас добавим тебя в базу. Погоди секу.')
    bot.delete_message(message.chat.id, message.message_id)
    reg_to_bd(message)

def get_elgur(login, password):
    r = post('https://api.eljur.ru/api/auth', data={
        'login': login,
        'password': password,
        'vendor': '2007',
        'devkey': '9235e26e80ac2c509c48fe62db23642c',  # 19c4bfc2705023fe080ce94ace26aec9
        'out_format': 'json'
    })
    if r.status_code != 200:
        return None
    token = loads(r.text)['response']['result']['token']
    r2 = get('https://api.eljur.ru/api/getmarks', params={
        'auth_token': token,
        'vendor': '2007',
        'out_format': 'json',
        'devkey': '9235e26e80ac2c509c48fe62db23642c',
        'days': '20220110-20220320'
    })
    student_code = list(r2.json()['response']['result']['students'].keys())[0]
    lst_marks = r2.json()['response']['result']['students'][student_code]['lessons']
    return (token, lst_marks)
def get_elgur_by_token(token):
    r2 = get('https://api.eljur.ru/api/getmarks', params={
        'auth_token': token,
        'vendor': '2007',
        'out_format': 'json',
        'devkey': '9235e26e80ac2c509c48fe62db23642c',
        'days': '20220110-20220320'
    })
    student_code = list(r2.json()['response']['result']['students'].keys())[0]
    lst_marks = r2.json()['response']['result']['students'][student_code]['lessons']
    return lst_marks


def encode(data):
    file = open('key.txt', 'rb')
    cipher_key = file.readline()
    cipher = Fernet(cipher_key)
    encrypted_text = cipher.encrypt(data)
    string = bytes.decode(encrypted_text, encoding='utf-8')
    return string


def reg_to_bd(message):
    connect = sqlite3.connect('bot.db')
    cursor = connect.cursor()
    if get_elgur(login, password) == None:
        bot.send_message(message.from_user.id, 'Кхмм... Пароль неверный! Введи нормально.')
        reg(message)
        return
    token, lst_marks = get_elgur(login, password)
    values = [message.chat.id, str("'") + encode(login) + str("'"), str("'") + encode(password) + str("'"), str("'") + token + str("'"), str("'") + json.dumps(lst_marks) + str("'"), datetime.now().date().day, datetime.now().date().month, datetime.now().date().year]
    cursor.execute(f"INSERT INTO data(user_id, login, pass, token, last_marks, day, month, year) VALUES({values[0]}, {values[1]}, {values[2]}, {values[3]}, {values[4]}, {values[5]}, {values[6]}, {values[7]});")
    connect.commit()

bot.polling(none_stop=True, interval=0)