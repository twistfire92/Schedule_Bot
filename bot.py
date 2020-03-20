# -*- coding: utf-8 -*-

import datetime
import json
import time

import telebot
from telebot import apihelper, types

import backend
import config
import frontend
from frontend import Statements

# Подключение самого бота
bot = telebot.TeleBot(token=config.token, threaded=False)

apihelper.proxy = {'https': config.proxy}

# НАЧАЛО РАБОТЫ
# Предложить ввести имя и ожидание ввода, если пользователь не найден. Иначе - главное меню
@bot.message_handler(commands=['start'])
def welcome_main_menu(message):
    new_user_data = backend.check_user(message.from_user.id)
    if len(new_user_data) == 0:
        bot.send_message(message.chat.id, "Здравствуйте!")
        time.sleep(1)
        bot.send_message(message.chat.id, "Перед вами инструмент бронирования переговорных комнат в компании Angels IT")
        time.sleep(2)
        bot.send_message(message.chat.id,
                         "Представьтесь, пожалуйста!\nВведите свои имя и фамилию.\nТак ваши бронирования будут отображаться в расписании")
        backend.new_user(message.from_user.id)
        bot.register_next_step_handler(message, get_user_name)
    elif new_user_data[0][1] is None:
        bot.send_message(message.chat.id, 'Ввдите свои имя и фамилию')
        bot.register_next_step_handler(message, get_user_name)
    else:
        main_menu(message.chat.id)


def get_user_name(message):
    if message.text in ['/start', '/help', '/feedback']:
        bot.send_message(message.chat.id, 'Введите свои имя и фамилию')
        bot.register_next_step_handler(message, get_user_name)
    elif is_digit(message.text):
        bot.send_message(message.chat.id, 'Это похоже на порядковый номер. Представьтесь так, чтобы Вас могли узнать')
        bot.register_next_step_handler(message, get_user_name)
    else:
        bot.send_message(message.chat.id, f'Добро пожаловать, {message.text}!')
        backend.set_users_name(message.from_user.id, message.text)
        time.sleep(1)
        bot.send_message(message.chat.id, 'Главное меню:', reply_markup=frontend.create_main_menu_markup())


def is_digit(string):
    if string.isdigit():
        return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False


@bot.message_handler(commands=['feedback'])
def feedback(message):
    marckup = types.InlineKeyboardMarkup()
    marckup.add(types.InlineKeyboardButton(text='Чат с автором',
                                           url='t.me/twistfire92',
                                           callback_data=''))
    text = 'Если у вас есть предложения по развитию функционала или если вы заметили какой-либо баг - пишите'
    bot.send_message(message.chat.id, text, reply_markup=marckup)


@bot.message_handler(commands=['help'])
def help(message):
    text = '''
Работа с ботом начинается по команде &b\start&b

Если вы - новый пользователь, вам будет предложено ввести ваше имя, после чего появится главное меню
Убедительная просьба! Вводите свои имя и фамилию, чтобы ваши коллеги могли понять кто вы есть.
Тем не менее, если ваша бронь появится в расписании, любой пользователь сможет написать вам, нажав на ваше имя.

В главном меню есть 3 раздела:
&b"Расписание"&b, &b"Бронирование"&b, &b"Отмена брони"&b

&b&uРасписание:&u&b
Вам будет предложено выбрать дату(сегодня, завтра, другая), после чего откроется расписание всех переговорок на выбранное вами число.

&b&uБронирование:&u&b
Бронирование состоит из пяти этапов:
&b1.&b Выбор &iкомнаты&i, которую хотите забронировать
&b2.&b Выбор &iдаты&i
&b3.&b Выбор &iвремени начала&i брони с шагом в полчаса
&b4.&b Выбор &iвремени окончания&i брони с шагом в полчаса
&b5.&b Добавление &iкомментария&i при необходимости

&iМожет получиться так, что на выбранное вами время и место уже есть бронь (либо бронирования пересекаются с кем-то по времни).
В таком случае бронирование не запишется, но вы сможете связаться с человеком, чтобы договориться, просто нажав на его имя.&i

&b&uОтмена брони:&u&b
В этом разделе вам будет предложено выбрать свою бронь, которую вы хотели бы отменить.
В списке будут только те бронирования, дата окончания которых еще не прошла.

&iВ связи с тем, что телеграм блокируется в России, могут возникать неполадки со связью, поэтому не спешите жать на кнопки по 100 раз, возможно, нужно будет просто подождать.&i
'''
    text = escape_charcters(text)
    bot.send_message(message.chat.id, text, parse_mode='MarkdownV2')


@bot.callback_query_handler(func=lambda call: True)
def choose_next_action(call):
    data = json.loads(call.data)
    state = data['st']

    cases = {
        Statements.S_MAIN_MENU_REPLACE: main_menu_replace,
        Statements.S_MAIN_MENU_ADD: main_menu_add,
        Statements.S_SHOW_SCHEDULE_CHOOSE_DAY: show_schedule_choose_day,
        Statements.S_SHOW_SCHEDULE_CALENDAR: show_schedule_calendar,
        Statements.S_SHOW_SCHEDULE_PRINT: show_schedule_print,
        Statements.S_RESERVE_CHOOSE_DAY: reserve_choose_day,
        Statements.S_RESERVE_CHOOSE_ROOM: reserve_choose_room,
        Statements.S_RESERVE_CALENDAR: reserve_calendar,
        Statements.S_RESERVE_CHOOSE_START_TIME: reserve_choose_start_time,
        Statements.S_RESERVE_CHOOSE_END_TIME: reserve_choose_end_time,
        Statements.S_RESERVE_CHECK: reserve_check,
        Statements.S_RESERVE_ERROR: reserve_error,
        Statements.S_RESERVE_ADD_COMMENT: reserve_add_comment,
        Statements.S_CANCEL_CHOOSE_RESERVE: cancel_choose_reserve,
        Statements.S_CANCEL_RESERVE: cancel_reserve,
        Statements.S_CHANGE_MONTH: change_month,
        Statements.S_DO_NOTHING: do_nothing
    }

    method = cases[state]
    method(call)


@bot.message_handler(func=lambda message: True)
def delete_message(message):
    bot.delete_message(message.chat.id, message.message_id)


def main_menu_replace(call):
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Главное меню:",
                          reply_markup=frontend.create_main_menu_markup())


def main_menu_add(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id)
    main_menu(call.message.chat.id)


def show_schedule_choose_day(call):
    today = datetime.datetime.today()
    time_moment = today.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    markup = frontend.create_choose_day_markup(time_moment, Statements.S_SHOW_SCHEDULE_PRINT)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='На какой день интересует расписание?',
                          reply_markup=markup)


def show_schedule_calendar(call):
    today = datetime.datetime.today()
    time_moment = today.timestamp()
    markup = frontend.create_calendar_markup(time_moment, Statements.S_SHOW_SCHEDULE_PRINT)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Выберите дату:",
                          reply_markup=markup)


def show_schedule_print(call):
    call_data = json.loads(call.data)
    time_start = int(call_data['tm'])
    time_end = time_start + 86400
    date = datetime.datetime.fromtimestamp(time_start)
    text = f'&bРасписание на {date.day:0>2}.{date.month:0>2}.{date.year}:&b\n'
    text = escape_charcters(text)
    rooms = backend.get_rooms()

    for room in rooms:
        reserves = backend.get_cross_reserves(room[0], time_start, time_end)
        if len(reserves) > 0:
            text += f'\n*__{room[1]}__*\n'
            rows = []
            for reserve in reserves:
                start = datetime.datetime.fromtimestamp(reserve[0])
                end = datetime.datetime.fromtimestamp(reserve[1])
                row = f'*_{start.hour:0>2}:{start.minute:0<2}\-{end.hour:0>2}:{end.minute:0<2}_ [{reserve[2]}](tg://user?id={reserve[3]})*'
                if not (reserve[4] is None):
                    comment = escape_charcters(reserve[4])
                    row += f': `{comment}`\n'
                rows.append(row)
            text += '\n'.join(rows) + '\n'

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=text,
                          parse_mode='MarkdownV2',
                          reply_markup=frontend.create_buttons_print_schedule_markup(time_start))


def reserve_choose_room(call):
    markup = frontend.create_choose_room_markup()
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='*Какую комнату* вы хотите забронировать\?',
                          parse_mode='MarkdownV2',
                          reply_markup=markup)


def reserve_choose_day(call):
    call_data = json.loads(call.data)
    room_id = call_data['r']
    today = datetime.datetime.today()
    time_moment = today.replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    markup = frontend.create_choose_day_markup(time_moment, Statements.S_RESERVE_CHOOSE_START_TIME, room_id)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='*Когда* вы хотели бы забронировать комнату\?',
                          parse_mode='MarkdownV2',
                          reply_markup=markup)


def reserve_calendar(call):
    call_data = json.loads(call.data)
    room_id = call_data['r']
    room_name = backend.get_room_name(room_id)
    text = f'Вы бронируете:\n{room_name}'
    today = datetime.datetime.today()
    time_moment = today.timestamp()
    markup = frontend.create_calendar_markup(time_moment, Statements.S_RESERVE_CHOOSE_START_TIME, room_id)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Выберите дату:",
                          reply_markup=markup)


def reserve_choose_start_time(call):
    call_data = json.loads(call.data)
    room_id = call_data['r']
    room_name = backend.get_room_name(room_id)
    time_moment = call_data['tm']
    date = datetime.datetime.fromtimestamp(time_moment)
    date = date.replace(hour=0, minute=0)
    text = f'*Вы бронируете:*\n\n*__{room_name}__*\n*Дата:* _{date.day:0>2}\.{date.month:0>2}\.{date.year}_'
    text += '\n\n*С какого времени вы хотите забронировать комнату?*'
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=text,
                          parse_mode='MarkdownV2',
                          reply_markup=frontend.create_hour_choose_menu(Statements.S_RESERVE_CHOOSE_END_TIME,
                                                                        time_moment, room_id))


def reserve_choose_end_time(call):
    call_data = json.loads(call.data)
    room_id = call_data['r']
    room_name = backend.get_room_name(room_id)
    time_moment = call_data['tm']
    date = datetime.datetime.fromtimestamp(time_moment)
    text = f'*Вы бронируете:*\n*__{room_name}__*\n*Дата:* _{date.day:0>2}\.{date.month:0>2}\.{date.year}_\n*Время:* _{date.hour:0>2}:{date.minute:0<2}\-_'
    text += '\n\n*До какого времени вы хотите забронировать комнату?*'
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=text,
                          parse_mode='MarkdownV2',
                          reply_markup=frontend.create_hour_choose_menu(Statements.S_RESERVE_CHECK,
                                                                        time_moment, room_id))


def reserve_check(call):
    user_id = call.from_user.id
    call_data = json.loads(call.data)
    tm_start = int(call_data['uts'])
    tm_end = int(call_data['ute'])
    room_id = int(call_data['r'])
    start = datetime.datetime.fromtimestamp(tm_start)
    end = datetime.datetime.fromtimestamp(tm_end)
    cross_reserves = backend.get_cross_reserves(room_id, tm_start, tm_end)
    room_name = backend.get_room_name(room_id)
    period = f'{start.day:0>2}.{start.month:0>2}.{start.year} {start.hour:0>2}:{start.minute:0<2}-{end.hour:0>2}:{end.minute:0<2}'

    if len(cross_reserves) == 0:
        backend.add_schedule_row(room_id, user_id, tm_start, tm_end, period)
        text = f'*Бронирование подтверждено\!*\n\n*__{room_name}__*\n_{start.day:0>2}\.{start.month:0>2}\.{start.year} {start.hour:0>2}:{start.minute:0<2}\-{end.hour:0>2}:{end.minute:0<2}_'
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text,
                              parse_mode='MarkdownV2',
                              reply_markup=frontend.create_button_main_menu_comment_markup(room_id, tm_start))

    else:
        text = f'*__{room_name}__*\n_{start.day:0>2}\.{start.month:0>2}\.{start.year} {start.hour:0>2}:{start.minute:0<2}\-{end.hour:0>2}:{end.minute:0<2}_'
        text += '\n\n*Есть пересечения с расписанием других сотрудников:*\n\n'
        rows = []
        for reserve in cross_reserves:
            start = datetime.datetime.fromtimestamp(reserve[0])
            end = datetime.datetime.fromtimestamp(reserve[1])
            rows.append(
                f"_{start.hour:0>2}:{start.minute:0<2}\-{end.hour:0>2}:{end.minute:0<2}_ *[{reserve[2]}](tg://user?id={reserve[3]})*")

        text += '\n'.join(rows)
        text += '\n\n*Отказ в бронировании\!*'
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text,
                              parse_mode='MarkdownV2',
                              reply_markup=frontend.create_button_main_menu_markup())


def reserve_error(call):
    pass


def reserve_add_comment(call):
    call_data = json.loads(call.data)
    room_id = call_data['r']
    tm_start = call_data['tms']
    msg = bot.send_message(chat_id=call.message.chat.id,
                           text='*Введите комментарий к бронированию:*\n\n_\'отмена\' \- чтобы не оставлять комментарий_',
                           parse_mode='MarkdownV2')
    bot.register_next_step_handler(msg, get_comment, room_id, tm_start, call.from_user.id)


def cancel_choose_reserve(call):
    user_id = call.from_user.id
    message_data = frontend.create_cancel_markup(user_id)
    markup = message_data['markup']
    text = message_data['text']
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=text,
                          reply_markup=markup)


def cancel_reserve(call):
    data = json.loads(call.data)
    start_date = data['tm']
    user_id = data['u']
    room_id = data['r']
    reserve = backend.get_reserve(room_id, user_id, start_date)

    start = datetime.datetime.fromtimestamp(reserve[0])
    end = datetime.datetime.fromtimestamp(reserve[1])
    room_name = reserve[2]

    backend.delete_reserve(room_id, user_id, start_date)

    text = f'*Отменено бронирование\!*\n\n*__{room_name}__*\n_{start.day:0>2}\.{start.month:0>2}\.{start.year} {start.hour:0>2}:{start.minute:0<2}\-{end.hour:0>2}:{end.minute:0<2}_'
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=text,
                          parse_mode='MarkdownV2',
                          reply_markup=frontend.create_button_main_menu_markup())


def change_month(call):
    call_data = json.loads(call.data)
    date = int(call_data['tm'])
    room_id = call_data['r']
    next_state = call_data['ns']
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="*Выберите дату:*",
                          parse_mode='MarkdownV2',
                          reply_markup=frontend.create_calendar_markup(date, next_state, room_id))


def do_nothing(call):
    pass


def get_comment(message, room_id, tm_start, user_id):
    if message.text in ['/start', '/help', '/feedback']:
        bot.send_message(message.chat.id, 'Введите комментарий:')
        bot.register_next_step_handler(message, get_comment, room_id, tm_start, user_id)
    elif message.text.lower().replace(' ', '') == 'отмена':
        main_menu(message.chat.id)
    else:
        comment = message.text
        backend.add_comment(room_id, user_id, tm_start, comment)
        bot.send_message(message.chat.id,
                         '*Комментарий добавлен\!*',
                         parse_mode='MarkdownV2',
                         reply_markup=frontend.create_button_main_menu_markup())
    pass


def main_menu(chat_id):
    bot.send_message(chat_id=chat_id,
                     text='*Главное меню:*',
                     parse_mode='MarkdownV2',
                     reply_markup=frontend.create_main_menu_markup())

# Фунция экранирует все необходимые символы и заменяет придуманные теги (&) на соответсвующие формату MarkdownV2
def escape_charcters(text):
    char_set = ['\\', '.', ',', '!', '-', '(', ')', '=', '+', '#', '[', ']', '~', '`', '|', '*', '_']
    for ch in char_set:
        text = text.replace(ch, '\\' + ch)

    text = text.replace('&b', '*')  # bold
    text = text.replace('&u', '__') # underline
    text = text.replace('&i', '_')  # italic
    text = text.replace('&s', '~')  # strikethrough
    text = text.replace('&f', '`')  # fixed-width
    return text

if __name__ == '__main__':
    '''
    Пришлось запустить все в бесконечном цикле с попыткой,
    ибо соединение осуществляется через прокси,
    а они иногда отваливаются.
    '''
    while True:
        try:
            bot.polling()
        except Exception as E:
            print(E.args)
            time.sleep(.5)
