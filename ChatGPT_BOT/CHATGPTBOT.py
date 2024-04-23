# библиотеки
import openai
import telebot
import datetime as dt
from telebot import types
import sqlite3 as sq

# константы
bot = telebot.TeleBot("7095557628:AAH16Qc4sO5QCEmmdGaaQ2ToswmADE4VUyc")
openai.api_key = "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"
LIST_OF_COMMANDS = ['/help', '/start', '/chat', '/add_admin', '/delete_admin']


# функция для того, чтобы при запущенной команде могли исполняться другие
def start_commands(message):
    text = message.text
    if text == '/delete_admin':
        delete_admin(message)
    elif text == '/start':
        Start(message)
    elif text == '/help':
        help(message)
    elif text == 'add_admin':
        add_admin(message)
    elif text == '/chat':
        Chat(message)


# выкачиваем id всех пользователей
def db_list_of_id():
    with sq.connect('ChatGPT.db') as con:
        cur = con.cursor()
        list_of_id = cur.execute('''SELECT id FROM users''').fetchall()
        return list_of_id


# выкачиваем значение админа(0/1)
def db_admin(id):
    with sq.connect('ChatGPT.db') as con:
        cur = con.cursor()
        admin = cur.execute(f'''SELECT id_admin FROM users WHERE id = {id}''').fetchall()[0][0]
        return admin


# кнопка для возвращения в гланое меню
def back_to_main_menu():
    markup = types.InlineKeyboardMarkup()
    back_to_main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
    markup.add(back_to_main_menu)
    return markup


# команда для подробного пояснения каждой функции
@bot.message_handler(commands=['help'])
def help(message):
    bot.delete_message(message.chat.id, message.message_id)
    help_markup = types.InlineKeyboardMarkup()
    # если значение админ == 1, то добавояется больше команд
    if db_admin(message.chat.id) == 1:
        back_to_main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
        mailing = types.InlineKeyboardButton(text='/mailing', callback_data='help_mailing')
        add_admin = types.InlineKeyboardButton(text='/add_admin', callback_data='help_add_admin')
        delete_admin = types.InlineKeyboardButton(text='/delete_admin', callback_data='help_delete_admin')
        chat = types.InlineKeyboardButton(text='/chat', callback_data='help_chat')
        count_of_users = types.InlineKeyboardButton(text='/count_of_users', callback_data='help_count_of_users')
        main_menu = types.InlineKeyboardButton('/main_menu', callback_data='help_main_menu')

        help_markup.add(chat, mailing, add_admin, delete_admin, count_of_users, main_menu, back_to_main_menu)
    # если значение админ == 0, то остаются базовые команды
    else:
        back_to_main_menu = types.InlineKeyboardButton(text='Главное меню', callback_data='main_menu')
        chat = types.InlineKeyboardButton(text='/chat', callback_data='help_chat')
        main_menu = types.InlineKeyboardButton('/main_menu', callback_data='help_main_menu')
        help_markup.add(chat, main_menu, back_to_main_menu)
    bot.send_message(message.chat.id, f'<b>Нажмите на кнопку которая вам не понятна.</b>', parse_mode='html',
                     reply_markup=help_markup)


# функция обработчик callback_data
@bot.callback_query_handler(func=lambda callback: callback.data)
def callback_check(callback):
    if callback.data == 'subdone':
        check_sub_done(callback)

    elif callback.data == 'help_chat':
        bot.send_message(callback.from_user.id,
                         'После того, как нажмете на эту кнопку, напишите боту сообщение, которое вы бы хотели отправить ChatGPT-4.')

    elif callback.data == 'help_mailing':
        bot.send_message(callback.from_user.id,
                         'После того, как нажмете на эту кнопку, напишите сообщение, котрое будет разослано всем польхователям этого бота.')

    elif callback.data == 'help_add_admin':
        bot.send_message(callback.from_user.id,
                         'После того, как нажмете на эту кнопку, напишите id пользователя данного бота, который станет админом.')

    elif callback.data == 'help_delete_admin':
        bot.send_message(callback.from_user.id,
                         'После того, как нажмете на эту кнопку, напищите id пользователя данного бота, который будет удален из админов.')

    elif callback.data == 'help_count_of_users':
        bot.send_message(callback.from_user.id,
                         'После того, как нажмете на эту кнопку, бот выведет количество пользователей этого бота.')

    elif callback.data == 'help_main_menu':
        bot.send_message(callback.from_user.id, 'После того, как нажмете на эту кнопку, бот вернет вас в меню команд.')
    # если админ, то функций больше
    elif callback.data == 'main_menu':
        if db_admin(callback.from_user.id) == 0:
            bot.send_message(callback.from_user.id, '''Главное меню:
/chat - Задать вопрос "ChatGPT-4"
/start - Перезапуск бота
/help - Вопрос к функциям''')
        else:
            bot.send_message(callback.from_user.id, '''Главное меню:
у вас есть доступ к расширенным функциям!
/start - Перезапуск бота 
/chat - Задать вопрос нейросети
/count_of_users - Число пользователей
/mailing - Рассылка
/add_admin - Добавить админа
/delete_admin - Удалить админа
/help - Помощь''')


# функция, которая присылает количество всех пользователей(только для админов)
@bot.message_handler(commands=['count_of_users'])
def count_of_users(message):
    if db_admin(message.chat.id) == 1:
        count = 0
        for i in db_list_of_id():
            count += 1
        bot.send_message(message.chat.id, str(count))
    else:
        bot.send_message(message.chat.id, f'<b>У вас нет доступа к этой команде!</b>', parse_mode='html')


# запуск бота
@bot.message_handler(commands=['start'])
def Start(message):
    try:
        # проверяем, что это личный чат
        if message.chat.type == 'private':
            with sq.connect('ChatGPT.db') as con:
                cur = con.cursor()
                # проверка, есть ли пользователь в БД
                check = cur.execute(f'''SELECT EXISTS(SELECT * FROM users WHERE id = {message.chat.id})''').fetchall()[
                    0]
                # если нет, то добавляем
                if check[0] == 0:
                    cur.execute(
                        f'''INSERT INTO users (id, id_count, id_time, id_admin) VALUES({message.chat.id}, {0},
                            "{dt.datetime.now().strftime('%Y, %m, %d, %H, %M, %S')}", {0})''')
                con.commit()
            # удаляем сообщение start(для красоты)
            bot.delete_message(message.chat.id, message.message_id)
            # проверка на админа(если админ, то функций больше)
            admin = db_admin(message.chat.id)
            if admin == 1:
                bot.send_message(message.chat.id,
                                 f'''
Здравствуйте'', <b> {message.from_user.first_name} </b> 
у вас есть доступ к расширенным функциям!
/start - Перезапуск бота 
/chat - Задать вопрос нейросети
/count_of_users - Число пользователей
/mailing - Рассылка
/add_admin - Добавить админа
/delete_admin - Удалить админа
/help - Помощь''', parse_mode='html')

            else:
                bot.send_message(message.chat.id, f'''
Привет, <b>{message.from_user.username}</b>! Этот бот предназначен для ответов на любые ваши вопросы! 
/start - Перезапуск бота
/chat - Задать вопрос нейросети
/help - помощь 
''', parse_mode='html')
        else:
            bot.send_message(message.chat.id, 'Я работую только в личных сообщениях.')
    except:
        bot.send_message(message.chat.id, 'Попробуйте сново.')


# функция для добавления админа
@bot.message_handler(commands=['add_admin'])
def add_admin(message):
    bot.register_next_step_handler(
        bot.send_message(message.chat.id, 'Напишите id того, кого вы хотите добавить в админы.',
                         reply_markup=back_to_main_menu()), add_admin_final)


def add_admin_final(message):
    text = message.text
    with sq.connect('ChatGPT.db') as con:
        cur = con.cursor()
        check = cur.execute(f'''SELECT EXISTS(SELECT * FROM users WHERE id = {text})''').fetchall()[0]
        if check[0] == 1:
            cur.execute(f'UPDATE users SET id_admin = 1 WHERE id = {text}')
        else:
            cur.execute(
                f'''INSERT INTO users (id, id_count, id_time, id_admin) VALUES({text}, {0}, "", {1})''')
        con.commit()
        bot.send_message(message.chat.id, '<b>Успешно!</b>', parse_mode='html', reply_markup=back_to_main_menu())


# функция для удаления админа
@bot.message_handler(commands=['delete_admin'])
def delete_admin(message):
    bot.register_next_step_handler(
        bot.send_message(message.chat.id, 'Напишите id того, кого вы хотите удалить из админов.',
                         reply_markup=back_to_main_menu()), delete_admin_final)


def delete_admin_final(message):
    text = message.text
    with sq.connect('ChatGPT.db') as con:
        cur = con.cursor()
        check = cur.execute(f'''SELECT EXISTS(SELECT * FROM users WHERE id = {text})''').fetchall()[0]
        if check[0] == 1:
            cur.execute(f'UPDATE users SET id_admin = 0 WHERE id = {text}')
            bot.send_message(message.chat.id, '<b>Успешно!</b>', parse_mode='html', reply_markup=back_to_main_menu())
            con.commit()
        else:
            bot.send_message(message.chat.id, 'Пользователя с таким id  нет в базе данных.',
                             reply_markup=back_to_main_menu())


# рассылкка всем пользователям(можно использовать для рекламы)
@bot.message_handler(commands=['mailing'])
def mailing(message):
    admin = db_admin(message.chat.id)

    if admin == 1:
        bot.register_next_step_handler(bot.send_message(message.chat.id, 'Напишите текст который вы хотите разослать.',
                                                        reply_markup=back_to_main_menu()),
                                       mailing_finally)
    else:
        bot.send_message(message.chat.id, f'<b>У вас нет доступа к этой команде!</b>', parse_mode='html',
                         reply_markup=back_to_main_menu())


# просьба подписаться, если уже подписанны, то доступ к ChatGPT
@bot.message_handler(commands=['chat'])
def Chat(message):
    switch = types.InlineKeyboardMarkup()
    channel_switch = types.InlineKeyboardButton(text='The_AlIve_live🤩', url="https://t.me/thealivelive")
    sub_done_check = types.InlineKeyboardButton(text='Готово!', callback_data='subdone')
    switch.add(channel_switch, sub_done_check)
    if bot.get_chat_member(chat_id='-1002013250812', user_id=message.chat.id).status == 'left':
        bot.send_message(message.chat.id, 'Пожалуйста, подпишитесь чтоб задать вопросы!', reply_markup=switch)
    else:
        bot.register_next_step_handler(bot.send_message(message.chat.id, '''
Привет! Я - искусственный интелект "ChatGPT-4"!
Задавай мне абсолютно любой вопрос, а я попробую на него ответить!''', reply_markup=back_to_main_menu()), ChatGPT)


# ChatGPT
def ChatGPT(message):
    try:
        with sq.connect('ChatGPT.db') as con:
            cur = con.cursor()
        text = message.text
        # если админ, то ограничений по использованию нет
        if db_admin(message.chat.id) == 1:
            # проверка того, что не было случайно отправленной команды, иначе запускается функция команды
            for i in LIST_OF_COMMANDS:
                if text == '/count_of_users':
                    return count_of_users(message)
                elif text == '/help':
                    return help(message)
                elif text == i:
                    return start_commands(message)
            # генерация ответа на сообщение message.text(от ChatGPT)
            response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=message.text,
                temperature=0,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.5,
                presence_penalty=0.0,
            )
            bot.register_next_step_handler(
                bot.send_message(message.chat.id, text=response['choices'][0]['text'],
                                 reply_markup=back_to_main_menu()),
                ChatGPT)
        else:
            # проверка на то, что пользователь до сих пор подписан
            switch = types.InlineKeyboardMarkup()
            channel_switch = types.InlineKeyboardButton(text='The_AlIve_live🤩',
                                                        url="https://t.me/thealivelive")
            sub_done_check = types.InlineKeyboardButton(text='Готово!', callback_data='subdone')
            switch.add(channel_switch, sub_done_check)
            if bot.get_chat_member(chat_id='-1002013250812', user_id=message.chat.id).status == 'left':
                bot.send_message(message.chat.id, 'Пожалуйста, подпишитесь чтоб задать вопросы!', reply_markup=switch)
            else:
                # проверка того, что не было случайно отправленной команды, иначе запускается функция команды
                for i in LIST_OF_COMMANDS:
                    if text == '/count_of_users':
                        return count_of_users(message)
                    elif text == '/help':
                        return help(message)
                    elif text == i:
                        return start_commands(message)
                # выкачиваем время, когда пользователь истратил 5-ое сообщение
                time = cur.execute(f'''SELECT id_time FROM users WHERE id = {message.chat.id}''').fetchall()[0][
                    0]
                # проверяем прошел ли день с того момента, как пользователь истратил 5-ое сообщение
                if dt.datetime(*list(map(lambda x: int(x), time.split(', ')))).strftime(
                        '%Y, %m, %d, %H, %M, %S') > dt.datetime.now().strftime('%Y, %m, %d, %H, %M, %S'):
                    # если нет
                    bot.send_message(message.chat.id, f'<b>К сожалению 24 часа еще не прошло.</b>',
                                     parse_mode='html', reply_markup=back_to_main_menu())
                else:
                    # если да
                    with sq.connect('ChatGPT.db') as con:
                        cur = con.cursor()
                        data = cur.execute(f'''SELECT id, id_count FROM users''').fetchall()
                        # смотрим сколько на сегодня осталось вопросов, если остались, то генерим ответ
                        for i in data:
                            if i[0] == message.chat.id:
                                if i[1] <= 4:
                                    cur.execute(
                                        f'''UPDATE users SET id_count = id_count + 1 WHERE id = {message.chat.id}''')
                                    response = openai.Completion.create(
                                        model="gpt-3.5-turbo-instruct",
                                        prompt=message.text,
                                        temperature=0,
                                        max_tokens=1000,
                                        top_p=1.0,
                                        frequency_penalty=0.5,
                                        presence_penalty=0.0,
                                    )

                                    bot.register_next_step_handler(
                                        bot.send_message(message.chat.id, text=response['choices'][0]['text'],
                                                         reply_markup=back_to_main_menu()),
                                        ChatGPT)
                                else:
                                    # если не осталось, сохраняем время "сейчас" + день в БД и обнуляем счетчик вопросов
                                    bot.send_message(message.chat.id,
                                                     'Вы исчерпали весь лимит на сегодня. Новые вопросы вы сможете задать через 24 часа!',
                                                     reply_markup=back_to_main_menu())
                                    cur.execute(
                                        f'''UPDATE users SET id_count = 0 WHERE id = {message.chat.id}''')
                                    cur.execute(
                                        f'''UPDATE users SET id_time = {(dt.datetime.now() + dt.timedelta(days=1)).strftime(
                                            '%Y, %m, %d, %H, %M, %S')} WHERE id = {message.chat.id}''')

    except:
        pass


def mailing_finally(message):
    text = message.text
    if text != '/chat' and text != '/start' and text != '/mailing' and text != 'Задать вопрос ChatGPT-4.' and text != 'Главное меню.':
        for i in db_list_of_id():
            bot.send_message(chat_id=i[0], text=text, parse_mode='html')
    else:
        bot.send_message(message.chat.id, '<b>Выберите одну функцию!</b>', parse_mode='html',
                         reply_markup=back_to_main_menu())


# проверка подписки на канал
def check_sub_done(callback):
    switch = types.InlineKeyboardMarkup()
    channel_switch = types.InlineKeyboardButton(text="The_AlIve_live🤩", url="https://t.me/thealivelive")
    sub_done_check = types.InlineKeyboardButton(text='Готово!', callback_data='subdone')
    switch.add(channel_switch, sub_done_check)
    if bot.get_chat_member(chat_id='-1002013250812', user_id=callback.from_user.id).status == 'left':
        bot.send_message(callback.message.chat.id, 'Пожалуйста, подпишитесь чтобы задать вопросы!', reply_markup=switch)
    else:
        bot.register_next_step_handler(bot.send_message(chat_id=callback.from_user.id, text='''
Спасибо, что подписались, можем продолжать!\n\nⒾ Задай мне абсолютно любой вопрос, а я попробую ответить на него''',
                                                        reply_markup=back_to_main_menu()), ChatGPT)


bot.polling(non_stop=True)
