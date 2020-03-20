token = ''
proxy1 = ''
proxy2 = ''


class States:
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
