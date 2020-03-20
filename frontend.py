# -*- coding: utf-8 -*-

import calendar
import datetime
import json
import backend

from telebot import types


# Обозначения:
# tm - time_moment
# r  - room
#

class Statements:
    # Главное меню
    S_MAIN_MENU_REPLACE = '00'
    S_MAIN_MENU_ADD = '01'

    # Просмотр расписания на день
    S_SHOW_SCHEDULE_CHOOSE_DAY = '10'
    S_SHOW_SCHEDULE_CALENDAR = '11'
    S_SHOW_SCHEDULE_PRINT = '12'

    # Бронирование комнаты
    S_RESERVE_CHOOSE_DAY = '20'
    S_RESERVE_CHOOSE_ROOM = '21'
    S_RESERVE_CALENDAR = '22'
    S_RESERVE_CHOOSE_START_TIME = '23'
    S_RESERVE_CHOOSE_END_TIME = '24'
    S_RESERVE_CHECK = '25'
    S_RESERVE_ERROR = '26'
    S_RESERVE_ADD_COMMENT = '27'

    # Отмена бронирования
    S_CANCEL_CHOOSE_RESERVE = '30'
    S_CANCEL_RESERVE = '31'

    # Для кнопок календаря)
    S_CHANGE_MONTH = '777'
    S_DO_NOTHING = '666'


# Создаем json структуру для отправки как сallback_data
def create_callback_data(state,
                         **kwargs):  # Обязательным полем будет аргумент state - показывает куда переходить дальше
    kwargs.update(st=state)
    return json.dumps(kwargs)


# Создание главного меню
def create_main_menu_markup():
    markup = types.InlineKeyboardMarkup()

    markup.row(types.InlineKeyboardButton(text='Посмотреть расписание',
                                          callback_data=create_callback_data(Statements.S_SHOW_SCHEDULE_CHOOSE_DAY)))
    markup.row(types.InlineKeyboardButton(text='Забронировать',
                                          callback_data=create_callback_data(Statements.S_RESERVE_CHOOSE_ROOM)))
    markup.row(types.InlineKeyboardButton(text='Отменить бронирование',
                                          callback_data=create_callback_data(Statements.S_CANCEL_CHOOSE_RESERVE)))
    return markup


# Создаем меню выбора комнаты
def create_choose_room_markup():
    markup = types.InlineKeyboardMarkup()
    rooms = backend.get_rooms()
    for room in rooms:
        callback_data = create_callback_data(Statements.S_RESERVE_CHOOSE_DAY, r=room[0])
        markup.add(types.InlineKeyboardButton(text=room[1],
                                              callback_data=callback_data))
    markup.add(types.InlineKeyboardButton(text='Назад', callback_data=create_callback_data(Statements.S_MAIN_MENU_REPLACE)))
    return markup


def create_choose_day_markup(tm, next_state, room_id=None):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='Сегодня',
                                          callback_data=create_callback_data(next_state, tm=tm, r=room_id)),
               types.InlineKeyboardButton(text='Завтра',
                                          callback_data=create_callback_data(next_state, tm=tm + 86400, r=room_id)))

    row = [types.InlineKeyboardButton(text='Назад', callback_data=create_callback_data(Statements.S_RESERVE_CHOOSE_DAY))]
    if next_state == Statements.S_RESERVE_CHOOSE_START_TIME:
        row = [
            types.InlineKeyboardButton(text='Назад', callback_data=create_callback_data(Statements.S_RESERVE_CHOOSE_ROOM)),
            types.InlineKeyboardButton(text='Выбрать дату',
                                       callback_data=create_callback_data(Statements.S_RESERVE_CALENDAR, r=room_id))]
    else:
        row = [types.InlineKeyboardButton(text='Назад', callback_data=create_callback_data(Statements.S_MAIN_MENU_REPLACE)),
               types.InlineKeyboardButton(text='Выбрать дату',
                                          callback_data=create_callback_data(Statements.S_SHOW_SCHEDULE_CALENDAR))]

    markup.row(*row)
    return markup


# Создание кнопок каелендаря
def create_calendar_markup(tm, next_state, room_id=None):
    date = datetime.datetime.fromtimestamp(tm)
    date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year = date.year
    month = date.month
    next_month = date.replace(day=15) + datetime.timedelta(days=20)
    next_month = next_month.replace(day=1)
    prev_month = date.replace(day=15) - datetime.timedelta(days=20)
    prev_month = prev_month.replace(day=1)
    next_month_unix = next_month.timestamp()
    prev_month_unix = prev_month.timestamp()

    month_list = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    markup = types.InlineKeyboardMarkup()
    month_button = types.InlineKeyboardButton(text=f'{month_list[month - 1]} {year}',
                                              callback_data=create_callback_data(Statements.S_DO_NOTHING))
    markup.row(month_button)

    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    week_row = []
    for weekday in weekdays:
        week_row.append(
            types.InlineKeyboardButton(text=weekday, callback_data=create_callback_data(Statements.S_DO_NOTHING)))
    markup.row(*week_row)

    month_calendar = calendar.monthcalendar(date.year, date.month)
    for week in month_calendar:
        week_row = []
        for day in week:
            if day > 0:
                button_date = date.replace(day=day)
                button_text = f'{day}'
                callback_data = create_callback_data(next_state, tm=button_date.timestamp(), r=room_id)
            else:
                button_text = ' '
                callback_data = create_callback_data(Statements.S_DO_NOTHING)
            week_row.append(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
        markup.row(*week_row)
    if next_state == Statements.S_RESERVE_CHOOSE_START_TIME:
        prev_state = Statements.S_RESERVE_CHOOSE_DAY
    else:
        prev_state = Statements.S_SHOW_SCHEDULE_CHOOSE_DAY
    navigate_row = [types.InlineKeyboardButton(text='<--',
                                               callback_data=create_callback_data(Statements.S_CHANGE_MONTH,
                                                                                  tm=prev_month_unix,
                                                                                  ns=next_state,
                                                                                  r=room_id)),
                    types.InlineKeyboardButton(text='Назад',
                                               callback_data=create_callback_data(prev_state,
                                                                                  r=room_id)),
                    types.InlineKeyboardButton(text='-->',
                                               callback_data=create_callback_data(Statements.S_CHANGE_MONTH,
                                                                                  tm=next_month_unix,
                                                                                  ns=next_state,
                                                                                  r=room_id))]
    markup.row(*navigate_row)
    return markup


def create_hour_choose_menu(next_state, tm, room_id):
    markup = types.InlineKeyboardMarkup(row_width=4)
    time_moment = datetime.datetime.fromtimestamp(tm)
    hourslist = []
    if next_state == Statements.S_RESERVE_CHECK:
        prev_state = Statements.S_RESERVE_CHOOSE_START_TIME
        start = time_moment.hour + 1
        if time_moment.minute == 0:
            callback_data = create_callback_data(next_state, uts=int(tm), ute=tm + 1800, r=room_id)
            hourslist.append(types.InlineKeyboardButton(text=f'{time_moment.hour}:30', callback_data=callback_data))

        for i in range(start, 21):
            tm_end = int(time_moment.replace(hour=0, minute=0).timestamp() + 3600 * i)

            callback_data = create_callback_data(next_state,
                                                 uts=tm,
                                                 ute=tm_end,
                                                 r=room_id)
            hourslist.append(types.InlineKeyboardButton(text=f'{i}:00', callback_data=callback_data))

            callback_data = create_callback_data(next_state,
                                                 uts=tm,
                                                 ute=tm_end + 1800,
                                                 r=room_id)
            hourslist.append(types.InlineKeyboardButton(text=f'{i}:30', callback_data=callback_data))
        tm = int(time_moment.replace(hour=0, minute=0).timestamp())
    else:
        prev_state = Statements.S_RESERVE_CHOOSE_DAY
        for i in range(8, 20):
            callback_data = create_callback_data(next_state, tm=tm + 3600 * i, r=room_id)
            hourslist.append(types.InlineKeyboardButton(text=f'{i}:00', callback_data=callback_data))

            callback_data = create_callback_data(next_state, tm=tm + 3600 * i + 1800, r=room_id)
            hourslist.append(types.InlineKeyboardButton(text=f'{i}:30', callback_data=callback_data))

    markup.add(*hourslist)
    callback_data = create_callback_data(prev_state, tm=tm, r=room_id)
    markup.row(types.InlineKeyboardButton(text='Назад', callback_data=callback_data))
    return markup


def create_cancel_markup(user_id):
    time_moment = int(datetime.datetime.timestamp(datetime.datetime.today()))
    reserves = backend.get_users_reserves(user_id, time_moment)
    markup = types.InlineKeyboardMarkup()
    if len(reserves) == 0:
        text = 'Вы не забронировали ни одной комнаты, нечего отменять!'
    else:
        text = 'Выберите бронирование, которое вы хотите отменить:'

    for reserve in reserves:
        start = datetime.datetime.fromtimestamp(reserve[0])
        end = datetime.datetime.fromtimestamp(reserve[1])
        room_name = reserve[2]
        room_id = reserve[3]
        button_text = f'{room_name} {start.day:0>2}.{start.month:0>2}.{start.year}  {start.hour:0>2}:{start.minute:0<2}-{end.hour:0>2}:{end.minute:0<2}'
        callback_data = create_callback_data(Statements.S_CANCEL_RESERVE, tm=reserve[0], u=user_id, r=room_id)
        markup.add(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))

    markup.add(
        types.InlineKeyboardButton(text='Главное меню', callback_data=create_callback_data(Statements.S_MAIN_MENU_REPLACE)))
    return {'text': text, 'markup': markup}


def create_button_main_menu_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Главное меню',
                                          callback_data=create_callback_data(Statements.S_MAIN_MENU_ADD)))
    return markup


def create_button_main_menu_comment_markup(room_id, tm_start):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(text='Добавить комментарий',
                                          callback_data=create_callback_data(Statements.S_RESERVE_ADD_COMMENT,
                                                                             r=room_id,
                                                                             tms=tm_start)))
    markup.row(types.InlineKeyboardButton(text='Главное меню',
                                          callback_data=create_callback_data(Statements.S_MAIN_MENU_ADD)))
    return markup


def create_buttons_print_schedule_markup(tm_start):
    next_day = datetime.datetime.fromtimestamp(tm_start + 86400)
    prev_day = datetime.datetime.fromtimestamp(tm_start - 86400)
    markup = types.InlineKeyboardMarkup()
    row = [types.InlineKeyboardButton(text=f'<< {prev_day.day:0>2}.{prev_day.month:0>2}.{prev_day.year}',
                                      callback_data=create_callback_data(Statements.S_SHOW_SCHEDULE_PRINT,
                                                                         tm=tm_start - 86400)),
           types.InlineKeyboardButton(text=f'{next_day.day:0>2}.{next_day.month:0>2}.{next_day.year} >>',
                                      callback_data=create_callback_data(Statements.S_SHOW_SCHEDULE_PRINT,
                                                                         tm=tm_start + 86400))]

    markup.row(*row)
    markup.row(types.InlineKeyboardButton(text='Главное меню',
                                          callback_data=create_callback_data(Statements.S_MAIN_MENU_ADD)))
    return markup
