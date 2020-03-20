# -*- coding: utf-8 -*-

import sqlite3

conn = sqlite3.connect("db.db")
cursor = conn.cursor()


# Функция проверки наличия пользователя в базе данных
def check_user(user_id):
    sql = f'''
            SELECT *
            FROM USERS
            WHERE ID={user_id}
        '''
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_users():
    sql = f'''
            SELECT ID, NAME
            FROM USERS
        '''
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


# Функция регистрации нового пользователя (Без имени)
def new_user(user_id):
    try:
        sql = f'''
                INSERT INTO USERS
                Values ({user_id}, Null)
            '''
        cursor.execute(sql)
        conn.commit()
    except sqlite3.DatabaseError as err:
        print("Error: ", err)


# Функция присваивает имя новому пользователю и устанавливает статус 0(Главное меню)
def set_users_name(user_id, user_name):
    try:
        sql = f'''
                UPDATE USERS
                SET NAME = '{user_name}'
                WHERE ID = {user_id}
        '''
        cursor.execute(sql)
        conn.commit()
    except sqlite3.DatabaseError as err:
        print("Error: ", err)


# Функция для получения состояний пользователя
def get_statements(user_id):
    sql = f'''
            select STATEMENTS
            from USERS
            where ID={user_id}
        '''
    cursor.execute(sql)
    result = cursor.fetchall()
    statements = str(result[0][0])
    return statements.split('|')


def get_rooms():
    sql = '''
            select ID, NAME
            from ROOMS
        '''
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_room_name(room_id):
    sql = f'''
            select NAME
            from ROOMS
            where ROOMS.ID = {room_id}
        '''
    cursor.execute(sql)
    result = cursor.fetchall()
    return result[0][0]


# Функция обновляет статусы пользователя в БД
def update_statements(user_id, statements):
    sql = f'''
            UPDATE USERS
            SET statements = {statements}
            WHERE ID = {user_id}
        '''
    cursor.execute(sql)
    conn.commit()


# функция убирает последнюю запись из строки состояний (Используется при нажатии кнопки "Назад"), возвращает новую
# строку
def pop_statement(statements):
    statements.pop(-1)
    return '|'.join(statements)


# Функция получает текущее состояние пользователя
def get_current_state(user_id):
    statements = get_statements(user_id)
    return statements[-1]


# Получить все расписание
def get_schedule(date, room_id):
    start_date = date
    end_date = date + 86400
    sql = f'''
                SELECT 
                    SCHEDULE.START_DATE,
                    SCHEDULE.END_DATE,
                    USERS.NAME as USER,
                    SCHEDULE.USER_ID,
                    SCHEDULE.COMMENT
                FROM SCHEDULE JOIN USERS ON SCHEDULE.USER_ID = USERS.ID
                WHERE
                    SCHEDULE.ROOM_ID = {room_id}
                    AND SCHEDULE.START_DATE > {start_date} 
                    AND SCHEDULE.END_DATE < {end_date}
                ORDER BY
                    SCHEDULE.START_DATE
            '''
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def add_schedule_row(room_id, user_id, time_start, time_end, period):
    sql = f'''
                INSERT INTO SCHEDULE (ROOM_ID, USER_ID, START_DATE, END_DATE, PERIOD)
                VALUES({room_id}, {user_id}, {time_start}, {time_end}, '{period}')
            '''
    cursor.execute(sql)
    conn.commit()


def add_comment(room_id, user_id, time_start, comment):
    sql = f'''
                UPDATE SCHEDULE
                SET COMMENT = '{comment}'
                WHERE 
                    ROOM_ID = {room_id}
                AND
                    USER_ID={user_id}
                AND
                    START_DATE={time_start}

            '''
    cursor.execute(sql)
    conn.commit()


def get_cross_reserves(room_id, time_start, time_end):
    sql = f'''
                SELECT
                    SCHEDULE.START_DATE,
                    SCHEDULE.END_DATE,
                    USERS.NAME as USER,
                    SCHEDULE.USER_ID,
                    SCHEDULE.COMMENT
                FROM 
                    SCHEDULE JOIN USERS ON SCHEDULE.USER_ID = USERS.ID
                WHERE
                    SCHEDULE.ROOM_ID = {room_id}
                AND
                    (SCHEDULE.START_DATE + 1 BETWEEN {time_start} AND {time_end} OR
                    SCHEDULE.END_DATE - 1 BETWEEN {time_start} AND {time_end} OR
                    {time_start} BETWEEN SCHEDULE.START_DATE + 1 AND SCHEDULE.END_DATE - 1 OR
                    {time_end} BETWEEN SCHEDULE.START_DATE + 1 AND SCHEDULE.END_DATE - 1)
                ORDER BY
                    SCHEDULE.START_DATE
            '''
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_users_reserves(user_id, tm):
    sql = f'''
                SELECT 
                    SCHEDULE.START_DATE,
                    SCHEDULE.END_DATE,
                    ROOMS.NAME as ROOM_NAME,
                    ROOMS.ID as ROOM_ID
                FROM SCHEDULE JOIN USERS ON SCHEDULE.USER_ID = USERS.ID JOIN ROOMS ON SCHEDULE.ROOM_ID = ROOMS.ID
                WHERE
                    SCHEDULE.USER_ID = {user_id}
                AND    
                    SCHEDULE.END_DATE > {tm}
                ORDER BY
                    SCHEDULE.START_DATE
            '''
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def delete_reserve(room_id, user_id, start_date):
    sql = f'''
            DELETE
            FROM 
                SCHEDULE
            WHERE 
                START_DATE={start_date}
            AND
                USER_ID={user_id}
            AND
                ROOM_ID={room_id}
        '''
    cursor.execute(sql)
    conn.commit()


def get_reserve(room_id, user_id, start_date):
    sql = f'''
            SELECT
                SCHEDULE.START_DATE,
                SCHEDULE.END_DATE,
                ROOMS.NAME
            FROM 
                SCHEDULE join ROOMS on SCHEDULE.ROOM_ID = ROOMS.ID
            WHERE 
                START_DATE={start_date}
            AND
                USER_ID={user_id}
            AND
                ROOM_ID={room_id}
        '''
    cursor.execute(sql)
    result = cursor.fetchall()
    return result[0]
