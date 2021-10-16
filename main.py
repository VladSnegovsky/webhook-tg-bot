import os
import telebot
from telebot import types
from flask import Flask, request


import database


API_TOKEN = '2026677724:AAFY67mpk3KdxIV0LfvMgB25Zec3BH6tgUc'
APP_URL = f'https://webhook-tg-bot1234.herokuapp.com/{API_TOKEN}'

bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)
db = database.DataBase()


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    db.add_user(message.from_user.id)
    msg = bot.send_message(message.chat.id, """Ім'я?""")
    bot.register_next_step_handler(msg, process_name_step)


def delete_buttons(call):
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    except Exception as e:
        print("Can't update message")


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        if len(name) < 2 or len(name) > 20:
            bot.send_message(chat_id, "Ім'я має бути довжиною від 2х до 20 символів!")
            send_welcome(message)
        else:
            db.set_name(message.from_user.id, name)

            back = types.InlineKeyboardButton(text='Назад', callback_data='Назад до імені')
            keyboard = types.InlineKeyboardMarkup().add(back)

            msg = bot.send_message(chat_id, 'Вік?', reply_markup=keyboard)
            bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        bot.reply_to(message, 'Помилка!')


def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = message.text
        if not age.isdigit():
            msg = bot.send_message(chat_id, 'Вік повинен бути записаний числом!')
            bot.register_next_step_handler(msg, process_age_step)
        elif int(age) < 2 or int(age) > 102:
            msg = bot.send_message(chat_id, 'Вік повинен бути від 2х до 102х років!')
            bot.register_next_step_handler(msg, process_age_step)
        else:
            db.set_age(message.from_user.id, int(age))

            male = types.InlineKeyboardButton(text='Чоловік', callback_data='Чоловік')
            female = types.InlineKeyboardButton(text='Жінка', callback_data='Жінка')
            third = types.InlineKeyboardButton(text='Ще не визначився:)', callback_data='Ще не визначився:)')
            back = types.InlineKeyboardButton(text='Назад', callback_data='Назад до віку')
            keyboard = types.InlineKeyboardMarkup().add(male, female).add(third).add(back)

            bot.send_message(chat_id, 'Стать?', reply_markup=keyboard)
    except Exception as e:
        bot.reply_to(message, 'Помилка!')


def send_menu(message):
    settings = types.InlineKeyboardButton(text='Налаштування', callback_data='Налаштування')
    information = types.InlineKeyboardButton(text='Інформація про мене', callback_data='Інформація')
    keyboard = types.InlineKeyboardMarkup().add(settings, information)
    bot.send_message(message.chat.id, 'Головне меню', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(call):
    delete_buttons(call)
    if call.data in ['Чоловік', 'Жінка', 'Ще не визначився:)']:
        db.set_sex(call.from_user.id, call.data)
        send_menu(call.message)
    elif call.data == 'Назад до імені':
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        send_welcome(call.message)
    elif call.data == "Назад до віку":
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        back = types.InlineKeyboardButton(text='Назад', callback_data='Назад до імені')
        keyboard = types.InlineKeyboardMarkup().add(back)

        msg = bot.send_message(call.message.chat.id, 'Вік?', reply_markup=keyboard)
        bot.register_next_step_handler(msg, process_age_step)
    elif call.data == "Інформація":
        information = db.get_information(call.from_user.id)
        bot.send_message(call.message.chat.id, f"Ім'я: {information[0][1]}\n"
                                               f"Вік: {information[0][2]}\n"
                                               f"Стать: {information[0][3]}")
        send_menu(call.message)
    elif call.data == "Налаштування":
        ch_name = types.InlineKeyboardButton(text="Змінити ім'я", callback_data="Змінити ім'я")
        ch_age = types.InlineKeyboardButton(text='Змінити вік', callback_data='Змінити вік')
        ch_sex = types.InlineKeyboardButton(text='Змінити стать', callback_data='Змінити стать')
        back = types.InlineKeyboardButton(text='Назад', callback_data='Назад до меню')
        keyboard = types.InlineKeyboardMarkup().add(ch_name, ch_age).add(ch_sex).add(back)

        bot.send_message(call.message.chat.id, 'Налаштування', reply_markup=keyboard)
    elif call.data == "Змінити ім'я":
        back = types.InlineKeyboardButton(text='Назад', callback_data='Назад до налаштувань1')
        keyboard = types.InlineKeyboardMarkup().add(back)
        msg = bot.send_message(call.message.chat.id, "Напишіть нове ім'я", reply_markup=keyboard)
        bot.register_next_step_handler(msg, change_name)
    elif call.data == "Змінити вік":
        back = types.InlineKeyboardButton(text='Назад', callback_data='Назад до налаштувань1')
        keyboard = types.InlineKeyboardMarkup().add(back)
        msg = bot.send_message(call.message.chat.id, "Напишіть новий вік", reply_markup=keyboard)
        bot.register_next_step_handler(msg, change_age)
    elif call.data == "Змінити стать":
        male = types.InlineKeyboardButton(text='Чоловік', callback_data='Чоловік')
        female = types.InlineKeyboardButton(text='Жінка', callback_data='Жінка')
        third = types.InlineKeyboardButton(text='Ще не визначився:)', callback_data='Ще не визначився:)')
        back = types.InlineKeyboardButton(text='Назад', callback_data='Назад до налаштувань')
        keyboard = types.InlineKeyboardMarkup().add(male, female).add(third).add(back)
        bot.send_message(call.message.chat.id, "Оберіть нову стать", reply_markup=keyboard)
    elif call.data == "Назад до меню":
        send_menu(call.message)
    elif call.data == "Назад до налаштувань1":
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        ch_name = types.InlineKeyboardButton(text="Змінити ім'я", callback_data="Змінити ім'я")
        ch_age = types.InlineKeyboardButton(text='Змінити вік', callback_data='Змінити вік')
        ch_sex = types.InlineKeyboardButton(text='Змінити стать', callback_data='Змінити стать')
        back = types.InlineKeyboardButton(text='Назад', callback_data='Назад до меню')
        keyboard = types.InlineKeyboardMarkup().add(ch_name, ch_age).add(ch_sex).add(back)
        bot.send_message(call.message.chat.id, 'Налаштування', reply_markup=keyboard)
    elif call.data == "Назад до налаштувань":
        ch_name = types.InlineKeyboardButton(text="Змінити ім'я", callback_data="Змінити ім'я")
        ch_age = types.InlineKeyboardButton(text='Змінити вік', callback_data='Змінити вік')
        ch_sex = types.InlineKeyboardButton(text='Змінити стать', callback_data='Змінити стать')
        back = types.InlineKeyboardButton(text='Назад', callback_data='Назад до меню')
        keyboard = types.InlineKeyboardMarkup().add(ch_name, ch_age).add(ch_sex).add(back)
        bot.send_message(call.message.chat.id, 'Налаштування', reply_markup=keyboard)


def change_name(message):
    try:
        chat_id = message.chat.id
        name = message.text
        if len(name) < 2 or len(name) > 20:
            back = types.InlineKeyboardButton(text='Назад', callback_data='Назад до налаштувань1')
            keyboard = types.InlineKeyboardMarkup().add(back)
            msg = bot.send_message(chat_id, "Ім'я має бути довжиною від 2х до 20 символів!", reply_markup=keyboard)
            bot.register_next_step_handler(msg, change_name)
        else:
            db.set_name(message.from_user.id, name)
            send_menu(message)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'Помилка!')


def change_age(message):
    try:
        chat_id = message.chat.id
        age = message.text
        if not age.isdigit():
            back = types.InlineKeyboardButton(text='Назад', callback_data='Назад до налаштувань1')
            keyboard = types.InlineKeyboardMarkup().add(back)
            msg = bot.send_message(chat_id, 'Вік повинен бути записаний числом!', reply_markup=keyboard)
            bot.register_next_step_handler(msg, change_age)
        elif int(age) < 2 or int(age) > 102:
            back = types.InlineKeyboardButton(text='Назад', callback_data='Назад до налаштувань1')
            keyboard = types.InlineKeyboardMarkup().add(back)
            msg = bot.send_message(chat_id, 'Вік повинен бути від 2х до 102х років!', reply_markup=keyboard)
            bot.register_next_step_handler(msg, change_age)
        else:
            db.set_age(message.from_user.id, int(age))
            send_menu(message)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'Помилка!')


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()


@server.route('/' + API_TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200


@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return '!', 200


if __name__ == '__main__':
    server.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))


db.close()
