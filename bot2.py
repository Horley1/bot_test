import sqlite3
import telebot
from requests import *
from json import *
import json
import time
from datetime import datetime
from fernet import *

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

def parsing_process(message_id):
    cursor = connect.cursor()
    txt = cursor.execute(f"SELECT * FROM data WHERE user_id={message_id}").fetchone()
    new_txt = get_elgur_by_token(txt[3], message_id)
    txt = json.loads(txt[4])
    if  new_txt != txt:
        for i in range(16):
            if txt[i] != new_txt[i]:
                #print(txt[i]['name'])
                ln1 = len(txt[i]['marks'])
                ln2 = len(new_txt[i]['marks'])
                #print(ln2, ln1)
                for j in range(ln2):
                    #print(new_txt[i]['marks'][j])
                    if j > len(txt[i]['marks']) - 1 or new_txt[i]['marks'][j] != txt[i]['marks'][j]:
                        bot.send_message(message_id, f"У тебя новая оценка по {new_txt[i]['name']}\nОценка: <tg-spoiler>{new_txt[i]['marks'][j]['value']}</tg-spoiler> ✅\nТип: {new_txt[i]['marks'][j]['lesson_comment']}\nДата: {new_txt[i]['marks'][j]['date']}", parse_mode="HTML")
        add_to_bd(message_id, new_txt)

def check_date(message_id):
    day = cursor.execute(f"SELECT * FROM data WHERE user_id={message_id}").fetchone()[5]
    month = cursor.execute(f"SELECT * FROM data WHERE user_id={message_id}").fetchone()[6]
    year = cursor.execute(f"SELECT * FROM data WHERE user_id={message_id}").fetchone()[7]
    #print(day, month, year)
    prev = datetime(year, month, day).date()
    now = datetime.now().date()
    return (now - prev).days
def decode(data):
    file = open('key.txt', 'rb')
    cipher_key = file.readline()
    cipher = Fernet(cipher_key)
    decrypted_text = cipher.decrypt(str.encode(data, encoding='utf-8'))
    return str(decrypted_text)[2:-1]

def change_token(message_id):
    login = cursor.execute(f"SELECT * FROM data WHERE user_id={message_id}").fetchone()[1]
    password = cursor.execute(f"SELECT * FROM data WHERE user_id={message_id}").fetchone()[2]
    r = post('https://api.eljur.ru/api/auth', data={
        'login': decode(login),
        'password': decode(password),
        'vendor': '2007',
        'devkey': '9235e26e80ac2c509c48fe62db23642c',  # 19c4bfc2705023fe080ce94ace26aec9
        'out_format': 'json'
    })
    token = loads(r.text)['response']['result']['token']
    value = str("'") + token + str("'")
    cursor.execute(f"UPDATE data SET token = {value} WHERE user_id = {message_id}")
    return token



def get_elgur_by_token(token, message_id):
    #print('+')
    #print(check_date(message_id))
    if check_date(message_id) > 0:
        token = change_token(message_id)
        #print('+')

    r2 = get('https://api.eljur.ru/api/getmarks', params={
        'auth_token': token,
        'vendor': '2007',
        'out_format': 'json',
        'devkey': '9235e26e80ac2c509c48fe62db23642c',
        'days': '20220110-20220320'
    })
    #print(r2.status_code)
    student_code = list(r2.json()['response']['result']['students'].keys())[0]
    lst_marks = r2.json()['response']['result']['students'][student_code]['lessons']
    return lst_marks

def add_to_bd(message_id, new_list):
    values = [message_id ,str("'") + json.dumps(new_list) + str("'")]
    cursor.execute(f"UPDATE data SET last_marks = {values[1]} WHERE user_id = {values[0]}")
    connect.commit()

#test = cursor.execute("SELECT user_id FROM data").fetchall()
while True:
    #for elem in test:
    #    try:
    #        parsing_process(elem[0])
    #    except:
    #        pass
    time.sleep(15)
    bot.send_message(327830972, "success")
