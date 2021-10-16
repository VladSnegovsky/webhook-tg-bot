import os
import telebot
from telebot import types
from flask import Flask, request


import database


API_TOKEN = '2089966817:AAGKsEfyqufqum--MmO-i6VBfLyF-SEH8SI'
APP_URL = f'https://test-task1234.herokuapp.com/{API_TOKEN}'

bot = telebot.TeleBot(API_TOKEN)
server = Flask(__name__)
db = database.DataBase()


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    db.add_user(message.from_user.id)
    msg = bot.send_message(message.chat.id, "Ім'я?")
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        if len(name) < 2 or len(name) > 20:
            bot.send_message(chat_id, "Ім'я має бути довжиною від 2х до 20 символів!")
            send_welcome(message)
        else:
            db.set_name(message.from_user.id, name)

            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Назад')

            msg = bot.send_message(chat_id, 'Вік?', reply_markup=markup)
            bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'Помилка!')


def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = message.text
        if age == 'Назад':
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            send_welcome(message)
        elif not age.isdigit():
            msg = bot.send_message(chat_id, 'Вік повинен бути записаний числом!')
            bot.register_next_step_handler(msg, process_age_step)
        elif int(age) < 2 or int(age) > 102:
            msg = bot.send_message(chat_id, 'Вік повинен бути від 2х до 102х років!')
            bot.register_next_step_handler(msg, process_age_step)
        else:
            db.set_age(message.from_user.id, int(age))

            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Жінка', 'Чоловік', 'Ще не визначився:)', 'Назад')

            msg = bot.send_message(chat_id, 'Стать?', reply_markup=markup)
            bot.register_next_step_handler(msg, process_sex_step)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'Помилка!')


def process_sex_step(message):
    try:
        sex = message.text
        if sex == 'Назад':
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Назад')
            msg = bot.send_message(message.chat.id, 'Вік?', reply_markup=markup)
            bot.register_next_step_handler(msg, process_age_step)
        elif sex in ['Жінка', 'Чоловік', 'Ще не визначився:)']:
            db.set_sex(message.from_user.id, sex)
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            send_menu(message)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Жінка', 'Чоловік', 'Ще не визначився:)')
            msg = bot.send_message(message.chat.id, 'Немає такого варіанту!', reply_markup=markup)
            bot.register_next_step_handler(msg, process_sex_step)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'Помилка!')


def send_menu(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Налаштування', 'Інформація про мене')
    msg = bot.send_message(message.chat.id, 'Головне меню', reply_markup=markup)
    bot.register_next_step_handler(msg, process_menu_step)


def process_menu_step(message):
    try:
        action = message.text

        if action == 'Налаштування':
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add("Змінити ім'я", 'Змінити вік', 'Змінити стать', 'Назад')
            msg = bot.send_message(message.chat.id, 'Налаштування', reply_markup=markup)
            bot.register_next_step_handler(msg, process_settings)
        elif action == 'Інформація про мене':
            information = db.get_information(message.from_user.id)
            bot.send_message(message.chat.id, f"Ім'я: {information[0][1]}\n"
                                               f"Вік: {information[0][2]}\n"
                                               f"Стать: {information[0][3]}")
            send_menu(message)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Налаштування', 'Інформація про мене')
            msg = bot.send_message(message.chat.id, 'Немає такого пункту меню!', reply_markup=markup)
            bot.register_next_step_handler(msg, process_menu_step)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'Помилка!')


def process_settings(message):
    try:
        action = message.text

        if action == 'Назад':
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            send_menu(message)
        elif action == "Змінити ім'я":
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Назад')
            msg = bot.send_message(message.chat.id, "Введіть нове ім'я", reply_markup=markup)
            bot.register_next_step_handler(msg, process_change_name)
        elif action == 'Змінити вік':
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Назад')
            msg = bot.send_message(message.chat.id, "Введіть новий вік", reply_markup=markup)
            bot.register_next_step_handler(msg, process_change_age)
        elif action == 'Змінити стать':
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Жінка', 'Чоловік', 'Ще не визначився:)', 'Назад')
            msg = bot.send_message(message.chat.id, "Оберіть нову стать", reply_markup=markup)
            bot.register_next_step_handler(msg, process_change_sex)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add("Змінити ім'я", 'Змінити вік', 'Змінити стать')
            msg = bot.send_message(message.chat.id, 'Немає такого пункту меню!', reply_markup=markup)
            bot.register_next_step_handler(msg, process_settings)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'Помилка!')


def process_change_name(message):
    try:
        name = message.text
        if name == 'Назад':
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add("Змінити ім'я", 'Змінити вік', 'Змінити стать', 'Назад')
            msg = bot.send_message(message.chat.id, 'Налаштування', reply_markup=markup)
            bot.register_next_step_handler(msg, process_settings)
        elif len(name) < 2 or len(name) > 20:
            msg = bot.send_message(message.chat.id, "Ім'я має бути довжиною від 2х до 20 символів!")
            bot.register_next_step_handler(msg, process_change_name)
        else:
            db.set_name(message.from_user.id, name)
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            send_menu(message)
    except Exception as e:
        print(e)
        bot.reply_to(message, 'Помилка!')


def process_change_age(message):
    try:
        age = message.text
        if age == 'Назад':
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add("Змінити ім'я", 'Змінити вік', 'Змінити стать', 'Назад')
            msg = bot.send_message(message.chat.id, 'Налаштування', reply_markup=markup)
            bot.register_next_step_handler(msg, process_settings)
        elif not age.isdigit():
            msg = bot.send_message(message.chat.id, 'Вік повинен бути записаний числом!')
            bot.register_next_step_handler(msg, process_change_age)
        elif int(age) < 2 or int(age) > 102:
            msg = bot.send_message(message.chat.id, 'Вік повинен бути від 2х до 102х років!')
            bot.register_next_step_handler(msg, process_change_age)
        else:
            db.set_age(message.from_user.id, int(age))
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            send_menu(message)
    except Exception as e:
            print(e)
            bot.reply_to(message, 'Помилка!')


def process_change_sex(message):
    try:
        sex = message.text
        if sex == 'Назад':
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add("Змінити ім'я", 'Змінити вік', 'Змінити стать', 'Назад')
            msg = bot.send_message(message.chat.id, 'Налаштування', reply_markup=markup)
            bot.register_next_step_handler(msg, process_settings)
        elif sex in [u'Жінка', u'Чоловік', u'Ще не визначився:)']:
            db.set_sex(message.from_user.id, sex)
            bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            send_menu(message)
        else:
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add('Жінка', 'Чоловік', 'Ще не визначився:)', 'Назад')
            msg = bot.send_message(message.chat.id, 'Немає такого варіанту!', reply_markup=markup)
            bot.register_next_step_handler(msg, process_change_sex)
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
