import telebot
from telebot import types
bot = telebot.TeleBot('6574248387:AAGILlI3c29I8CqEQYT_xX-cVOTQaj15UM0')

import random
import pandas as pd
import sqlite3

connection = sqlite3.connect('database.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS timetable
              (Date, Time, Master)''')
#cursor.execute('DELETE FROM timetable;')
cursor.execute('''CREATE TABLE IF NOT EXISTS info
              (Service, Info, Time, Price)''')
#cursor.execute('DELETE FROM info;')
connection.commit()
connection.close()

def add_timetable(date, time, master):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO timetable (Date, Time, Master) 
        SELECT ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM timetable 
            WHERE Date = ? AND Time = ? AND Master = ?
        )
    """, (date, time, master, date, time, master))
    connection.commit()
    connection.close()

add_timetable('01.01.2024', '10:00', 'Anna')


def remove_old_timetable_entries(): # это когда нужно очистить базу данных info потому что добавили обновленные данные и старые уже неактуальны
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    # Получаем все записи из базы данных
    cursor.execute('SELECT * FROM info')
    existing_entries = cursor.fetchall()

    # Удаляем записи, которых нет в коде
    for entry in existing_entries:
        cursor.execute('DELETE FROM info WHERE Service = ? AND Info = ? AND Time = ? AND Price = ?', entry)

    connection.commit()
    connection.close()

# Вызываем функцию для удаления старых записей
remove_old_timetable_entries()

def add_info(service, info, time, price):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO info (Service, Info, Time, Price) 
        SELECT ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM info 
            WHERE Service = ? AND Info = ? AND Time = ? AND Price = ?
        )
    """, (service, info, time, price, service, info, time, price))
    connection.commit()
    connection.close()

add_info('\U0001F337 Маникюр с однотонным покрытием гель-лак', 'Входит снятие старого покрытия, опил формы, комби маникюр, выравнивание, покрытие под кутикулу', 'Продолжительность процедуры - 2 часа', 'Стоимость - 2500 рублей')
add_info('\U0001F337 Наращивание', 'Входит снятие старого покрытия, комби маникюр, создание архитектуры гелем, покрытие под кутикулу', 'Продолжительность процедуры - 2,5 часа', 'Стоимость - 3500 рублей')
add_info('\U0001F337 Маникюр без покрытия', 'Входит снятие старого покрытия, опил формы, комби маникюр', 'Продолжительность процедуры - 1 час', 'Стоимость - 1000 рублей')
add_info('\U0001F337 Снятие без маникюра', 'Входитнятие старого покрытия, опил формы', 'Продолжительность процедуры - 15 минут', 'Стоимость - 500 рублей')
add_info('\U0001F337 SPA-уход', 'Входит очищение кожи с использованием скраба, интенсивное питание кожи маской-филлером, увлажнение кремом с пептидным комплексом', '30 минут', 'Стоимость - 700 рублей')

@bot.message_handler(commands=["start"])
def start(m, res=False):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Расписание")
    item2 = types.KeyboardButton("Услуги")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(m.chat.id, f'Здравствуйте, {m.from_user.first_name}!\nДобро пожаловать в студию smp nails\U0001FA77 \nС помощью этого бота вы сможете: \n \U0001F337 Ознакомиться с услугами салона  \n \U0001F337 Самостоятельно записаться на процедуру \n \U0001F337 Ознакомиться с прайсом \n \U0001F337 Подтвердить или отменить запись')
    bot.send_message(m.chat.id, "Выберите, пожалуйста, что вас интересует\U0001F447", reply_markup=markup)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if message.text.strip() == 'Расписание':
        cursor.execute('SELECT * FROM timetable')
        rows = cursor.fetchall()
        rows_str = [' '.join(map(str, row)) for row in rows]
        message_str = '\n'.join(rows_str)
    elif message.text.strip() == 'Услуги':
        cursor.execute('SELECT * FROM info')
        rows = cursor.fetchall()
        rows_str = ['\n'.join(map(str, row)) for row in rows]
        message_str = '\n'.join(rows_str)
    else:
        message_str = 'нажмите кнопку'
    conn.close()
    bot.send_message(message.chat.id, message_str)

bot.polling(none_stop=True, interval=0)