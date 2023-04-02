from math import log
from statistics import variance, mean
from decimal import Decimal
import os
import datetime
import sys
import sqlite3
from PyQt6.QtSql import *
from datetime import datetime
from PyQt6 import uic, QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QIcon
from MainForm import Ui_MainForm
from DeleteDialog import Ui_DeleteDialog
from EditDialog import Ui_EditDialog
from ErrorDialog import Ui_ErrorDialog
from AddDialog1 import Ui_AddDialog1
from AddDialog2 import Ui_AddDialog2
from Calendar import Ui_Calendar
from AnalysisDialog import Ui_AnalysisDialog


db_name = 'databases/db_tested.db'

def connect_db(db_name):
    '''Функция устанавливает соединение с базой данных'''
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_name)
    if not db.open():
        print('Не удалось подключиться к базе')
        return False
    return db

def get_headers(tab_name):
    '''Функция возвращает заголовки по переданному названию таблицы'''
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    sql = 'SELECT name FROM PRAGMA_TABLE_INFO("{}")'.format(tab_name)
    headers = tuple(header[0] for header in cur.execute(sql).fetchall())
    print(cur.execute(sql).fetchall())
    cur.close()
    con.close()
    return headers

def get_all_act_isp():
    '''Функция возвращает кортеж из двух котрежей: коды бумаги и даты погащения'''
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    sql = 'SELECT * FROM {}'.format('Act_isp')
    regnum_data = tuple(line[0] for line in cur.execute(sql).fetchall())
    exec_date_data = tuple(line[1] for line in cur.execute(sql).fetchall())
    cur.close()
    con.close()
    return (regnum_data, exec_date_data)

def get_all_Activ():
    '''Функция возвращает кортеж из котрежей: даты торгов, кода бумаги, цены, доходности'''
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    sql = 'SELECT * FROM {}'.format('Activ')
    torg_date_data = tuple(line[0] for line in cur.execute(sql).fetchall())
    regnum_data = tuple(line[1] for line in cur.execute(sql).fetchall())
    price_data = tuple(line[2] for line in cur.execute(sql).fetchall())
    gain_end = tuple(line[3] for line in cur.execute(sql).fetchall())
    cur.close()
    con.close()
    return (torg_date_data, price_data, regnum_data, gain_end)

def get_rate_Activ():
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    sql = 'SELECT {} FROM {}'.format('ставка', 'Activ')
    rate = [line[0] for line in cur.execute(sql).fetchall()]
    cur.close()
    con.close()
    return rate

def get_count_rows(tab_name):
    '''Функция возвращает количество строк в переданной таблице'''
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    sql = 'SELECT COUNT(*) FROM {}'.format(tab_name)
    count_rows = cur.execute(sql).fetchall()[0][0]
    return count_rows

def Analysis_Dialog():

    global AnalysisDialog
    AnalysisDialog = QtWidgets.QDialog()
    ui_analysis = Ui_AnalysisDialog()
    ui_analysis.setupUi(AnalysisDialog)
    AnalysisDialog.show()

    def select_date_from():
        '''Функция позволяет выбрать дату начала интервала'''

        global Calendar
        Calendar = QtWidgets.QWidget()
        ui_cal = Ui_Calendar()
        ui_cal.setupUi(Calendar)
        Calendar.show()

        def add_and_close():
            global sel_date_from
            sel_date_from = ui_cal.calendarWidget.selectedDate()
            sel_date_from = sel_date_from.toString("dd.MM.yyyy")
            ui_analysis.line_date_from.setText(sel_date_from)
            Calendar.close()

        ui_cal.CalendarCheck.clicked.connect(add_and_close)

    def select_date_to():
        '''Функция позволяет выбрать дату конца интервала'''

        global Calendar
        Calendar = QtWidgets.QWidget()
        ui_cal = Ui_Calendar()
        ui_cal.setupUi(Calendar)
        Calendar.show()

        def add_and_close():
                global sel_date_to
                sel_date_to = ui_cal.calendarWidget.selectedDate()
                sel_date_to = sel_date_to.toString("dd.MM.yyyy")
                ui_analysis.line_date_to.setText(sel_date_to)
                Calendar.close()
        ui_cal.CalendarCheck.clicked.connect(add_and_close)

    def clear_table():
        '''Функция очищает таблицу от текущих значений'''
        for i in range(58):
            ui_analysis.tableWidget.item(i, 0).setText('')
            ui_analysis.tableWidget.item(i, 1).setText('')
            ui_analysis.tableWidget.item(i, 2).setText('')
            ui_analysis.tableWidget.item(i, 3).setText('')
            ui_analysis.tableWidget.item(i, 4).setText('')

    def calculates_characteristics():
        '''Функция рассчитывает среднее и дисперсию процентных ставок для каждого кода бумаги выбранного интревала'''

        # проверка даты
        if 'sel_date_from' not in globals() or ui_analysis.line_date_from.text() == '':
            ui_analysis.textBrowser.setText('Не выбрана дата начала предыстории')
            return

        if 'sel_date_to' not in globals() or ui_analysis.line_date_to.text() == '':
            ui_analysis.textBrowser.setText('Не выбрана дата конца предыстории')
            return

        date_from = datetime.strptime(sel_date_from, '%d.%m.%Y')
        date_to = datetime.strptime(sel_date_to, '%d.%m.%Y')

        if date_to < date_from:
            print(date_to, date_from)
            ui_analysis.textBrowser.setText('Начальная дата больше конечной')
            return
        ui_analysis.textBrowser.clear()

        # получение необходимых данных
        count_rows = get_count_rows('Activ')  # количество строк в таблице Activ
        torg_date_Activ = get_all_Activ()[0] # даты торгов из таблицы Activ
        regnum_Activ = get_all_Activ()[2] # коды бумаги из таблицы Activ
        rate = get_rate_Activ() # ставка

        if date_to > datetime.strptime(torg_date_Activ[-1], '%d.%m.%Y'):
            ui_analysis.textBrowser.setText('Выбранная дата превышает максимально допустимую для выбора дату')
            return

        # получение уникальных дат торгов из всей таблицы
        set_torg_date = []
        for i in range(count_rows):
            if torg_date_Activ[i] not in set_torg_date:
                set_torg_date.append(torg_date_Activ[i])

        if date_to < datetime.strptime(set_torg_date[1], '%d.%m.%Y'):
            ui_analysis.textBrowser.setText('Минимально допустимая для выбора дата превышает выбранную дату')
            return

        if sel_date_to not in set_torg_date:
            ui_analysis.textBrowser.setText('Выбранная дата не является датой торгов')
            return

        # t-1 день
        previous_date_to = datetime.strptime(set_torg_date[set_torg_date.index(sel_date_to) - 1], '%d.%m.%Y')
        print(set_torg_date)

        def calc_char_diff_days(date_from, date_to):
            # инициализация дополнительных переменных
            regnum_day = [] # уникальные коды бумаги из выбранного дня
            regnum_interval = [] # коды бумаги из выбранного интервала
            rate_interval = [] # ставки из выбранного интервала
            mean_rate = [] # среднее ставки для каждого кода бумаги из выбранного интервала
            one_regnum_rate = [] # ставки для одного кода бумаги
            variance_rate = [] # дисперсия ставки для каждого кода из выбранного интервала

            for i in range(count_rows):

                if date_from <= datetime.strptime(torg_date_Activ[i], '%d.%m.%Y') <= date_to:

                    rate_interval.append(float(rate[i].replace(',', '.')))
                    regnum_interval.append(regnum_Activ[i])

                if datetime.strptime(torg_date_Activ[i], '%d.%m.%Y') == date_to:
                    if regnum_Activ[i] not in regnum_day:
                        regnum_day.append(regnum_Activ[i])

            for i in range(len(regnum_day)):
                for j in range(len(regnum_interval)):
                    if regnum_day[i] == regnum_interval[j]:
                        one_regnum_rate.append(rate_interval[j])

                if len(one_regnum_rate) == 1:
                    variance_rate.append(0)
                else:
                    variance_rate.append(round(variance(one_regnum_rate), 9))

                mean_rate.append(round(mean(one_regnum_rate), 7))
                one_regnum_rate = []

            return (regnum_day, mean_rate, variance_rate)

        # получение кодов бумаги, средних и дисперсий для дня t
        regnum_day = calc_char_diff_days(date_from, date_to)[0]
        mean_rate = calc_char_diff_days(date_from, date_to)[1]
        variance_rate = calc_char_diff_days(date_from, date_to)[2]

        # получение кодов бумаги, средних и дисперсий для дня t-1
        regnum_previous_day = calc_char_diff_days(date_from, previous_date_to)[0]
        mean_rate_previous = calc_char_diff_days(date_from, previous_date_to)[1]
        variance_rate_previous= calc_char_diff_days(date_from, previous_date_to)[2]

        print(regnum_day, regnum_previous_day)
        print(mean_rate, mean_rate_previous)
        print(variance_rate, variance_rate_previous)
        print(len(regnum_day), len(regnum_previous_day))

        # печать расчитанных значений в таблицу
        for i in range(len(regnum_day)):
            ui_analysis.tableWidget.item(i, 0).setText(regnum_day[i])
            ui_analysis.tableWidget.item(i, 1).setText(str(mean_rate[i]))
            ui_analysis.tableWidget.item(i, 2).setText(str("{:.2e}".format(Decimal(variance_rate[i]))))

            if mean_rate[i] > mean_rate_previous[i]:
                ui_analysis.tableWidget.item(i, 3).setText('растет')
            else:
                ui_analysis.tableWidget.item(i, 3).setText('уменьшается')

            if variance_rate[i] > variance_rate_previous[i]:
                ui_analysis.tableWidget.item(i, 4).setText('растет')
            else:
                ui_analysis.tableWidget.item(i, 4).setText('уменьшается')

    # кнопки взаимодействия с окном
    ui_analysis.date_button_from.clicked.connect(select_date_from)
    ui_analysis.date_button_to.clicked.connect(select_date_to)
    ui_analysis.calc_button.clicked.connect(calculates_characteristics)
    ui_analysis.clear_button.clicked.connect(clear_table)
    ui_analysis.exit_button.clicked.connect(AnalysisDialog.close)



def get_rate():
    '''
    Функция расчитывает и выводит в консоль список состоящий из процентных ставкок для каждого торгового дня
    Формула для расчета: xk(i) = ln{ Fk(i) / 100)}/( Tk - ti ), где
    Fk - текущая цена ценной бумаги
    Tk - дата погашения ценной бумаги
    ti - порядковый номер торгового дня
    '''

    def sql_update_query():
        sql = 'UPDATE {} SET {} = "{}" WHERE {} = "{}" AND {} = "{}" AND {} = "{}" AND {} = "{}" '. \
            format('Activ', headers[4], str(xk[i]).replace('.', ','),
                   headers[0], torg_date_Activ[i],
                   headers[1], regnum_Activ[i],
                   headers[2], price[i],
                   headers[3], gain_end[i])
        query.prepare(sql)
        flag = query.exec()
        print(flag)

    xk, Tk, t, res = [], [], [], [] # переменные для расчета

    count_rows = get_count_rows('Activ') # количество строк в таблице Activ
    headers = get_headers('Activ') # заголовки таблицы Activ

    regnum_act_isp = get_all_act_isp()[0] #все коды из таблицы act_isp
    exec_date = get_all_act_isp()[1] #все даты погашения из таблицы act_isp

    torg_date_Activ = get_all_Activ()[0] #все даты торгов из таблицы Activ
    price = get_all_Activ()[1]  # кортеж из цен для каждого торгового дня
    regnum_Activ = get_all_Activ()[2] #все коды из таблицы Activ
    gain_end = get_all_Activ()[3]  # все доходности из таблицы Activ

    # создание списка из дат погашения по соответствию кодов двух таблиц
    for reg_Activ in regnum_Activ:
        for index, reg_act_isp in enumerate(regnum_act_isp):
            if reg_Activ == reg_act_isp:
                res.append(exec_date[index])

    # t = [int(date[:2].lstrip('0')) for date in torg_date_Activ] # создание списка из дней торгов
    # Tk = [int(date[:2].lstrip('0')) for date in res] # создание списка из дней погашения
    t = torg_date_Activ
    Tk = res
    Fk = [float(i.replace(',', '.')) for i in price]  # приведение цены к численному типу

    print(Tk[:7], t[:7], Fk[:7])

    # расчет ставки
    for i in range(count_rows):
        if Tk[i] == t[i]:
            xk.append(0)
        else:
            delta = (datetime.strptime(Tk[i], "%d.%m.%Y") - datetime.strptime(t[i], "%d.%m.%Y")).days
            print(delta)
            xk.append(round(log(Fk[i] / 100) / delta, 6))

    query = QSqlQuery()

    # добавление нового столбца со значениями ставки
    if 'ставка' not in headers:
        sql = 'ALTER TABLE {} ADD "ставка" TEXT NOT NULL DEFAULT ""'.format('Activ')
        query.prepare(sql)
        flag = query.exec()
        print(flag)
        Activ.select()

        headers = get_headers('Activ')  # заголовки таблицы Activ, включая ставку
        print(headers)
        for i in range(count_rows):
            sql_update_query()
        Activ.select()

    irrelevant_rate = get_rate_Activ() #ставка, которая находится в данный момент в таблице (может быть неактуальной)
    price = get_all_Activ()[1]  # кортеж из цен для каждого торгового дня

    # обновление значений ставки для добавленных строк
    while '' in irrelevant_rate:
        i = irrelevant_rate.index('')
        irrelevant_rate[i] = xk[i]
        sql_update_query()
    Activ.select()

    # обновление значения ставки для отредактированных строк
    for i in range(count_rows):
            if irrelevant_rate[i] != str(xk[i]).replace('.',','):
                sql_update_query()
                irrelevant_rate[i] = str(xk[i]).replace('.',',')
    Activ.select()

def set_filter():
    ''''Функция фильтрует по заданным параметрам'''

    # Считывание введённых фильтров
    date_start = Ui_Main.date_start.text()
    date_end = Ui_Main.date_end.text()
    key = Ui_Main.key_list.text()
    price_start = Ui_Main.price_start.text()
    price_end = Ui_Main.price_end.text()
    gain_start = Ui_Main.gain_start.text()
    gain_end = Ui_Main.gain_end.text()
    date_start = '"{}"'.format(date_start)
    date_end ='"{}"'.format(date_end)
    key = '"{}"'.format(key)

    # Фильтрация
    sql = 'дата_торгов >= {} and дата_торгов <= {} and код_бумаги = {} and цена >= {} '\
          'and цена <= {} and текущая_доходность >= {} and текущая_доходность <= {}'\
        .format(date_start, date_end, key, price_start, price_end, gain_start, gain_end)

    Activ.setFilter(sql)
    print(sql)


def Add_Dialog():
    '''Функция открывает диалог добавления для выбранной таблицы'''
    tab_name = Ui_Main.tabWidget.tabText(Ui_Main.tabWidget.currentIndex())  # имя текущей таблицы
    if tab_name == 'Activ':
        Add_Dialog_Activ()
    elif tab_name == 'Act_isp':
        Add_Dialog_act_isp()


def Add_Dialog_Activ():
    '''Функция добавляет строку в таблицу Activ'''

    global AddDialog1
    AddDialog1 = QtWidgets.QWidget()
    ui_add_tab1 = Ui_AddDialog1()
    ui_add_tab1.setupUi(AddDialog1)
    AddDialog1.show()

    def add_date():
        '''Функция позволяет выбрать дату из календаря'''

        global Calendar
        Calendar = QtWidgets.QWidget()
        ui_cal = Ui_Calendar()
        ui_cal.setupUi(Calendar)
        Calendar.show()

        def add_and_close():
            global added_date  # выбранная дата из календаря
            added_date = ui_cal.calendarWidget.selectedDate()
            added_date = added_date.toString("dd.MM.yyyy")
            ui_add_tab1.line_date.setText(added_date)
            Calendar.close()

        ui_cal.CalendarCheck.clicked.connect(add_and_close)

    def sql_insert_query(new_values, headers):
        '''Функция вставляет переданный кортеж в таблицу Activ и обновляет ее'''
        query = QSqlQuery()
        sql = 'INSERT INTO {} {} VALUES {}'.format('Activ', headers, new_values)
        query.prepare(sql)
        flag = query.exec()
        print(flag)
        Activ.select()

        AddDialog1.close()

    def add_row_Activ():

        new_values = tuple() #кортеж для всех значений строки

        # проверка на выбор даты
        if 'added_date' not in globals() or ui_add_tab1.line_date.text() == '':
            ui_add_tab1.textBrowser.setText('Не выбрана дата торгов')
            return
        new_values += (added_date,)

        new_values += (ui_add_tab1.comboBox_regnum.currentText(),) # добавление к общему списку выбранного кода
        price_cell = ui_add_tab1.line_price.text() # получение текущего значения цены
        gain_end_cell = ui_add_tab1.line_gain_end.text() # получение текущего значения доходности

        # проверка на ввод всех значений
        if price_cell == '':
            ui_add_tab1.textBrowser.setText('Не указано значение текущей цены')
            return

        # проверка на правильность ввода текущей цены
        try:
            if float(price_cell) < 0:
                ui_add_tab1.textBrowser.setText('Введено отрицательное значение')
                return
            new_values += (price_cell.replace('.', ','),)
        except ValueError:
            ui_add_tab1.textBrowser.setText('Введено значение неверного типа')
            return

        if gain_end_cell == '':
            ui_add_tab1.textBrowser.setText('Не указано значение текущей доходности')
            return

        # проверка на правильность ввода доходности
        try:
            if float(gain_end_cell) <= 0:
                ui_add_tab1.textBrowser.setText('Введено отрицательное значение')
                return
            new_values += (gain_end_cell.replace('.', ','),)
        except ValueError:
            ui_add_tab1.textBrowser.setText('Введено значение неверного типа')
            return

        headers = get_headers('Activ')
        if 'ставка' in headers:
            new_values += ('',)

        print(headers)
        print(new_values)

        sql_insert_query(new_values, headers)

    ui_add_tab1.date_button.clicked.connect(add_date)
    ui_add_tab1.button_ok.clicked.connect(add_row_Activ)
    ui_add_tab1.button_cancel.clicked.connect(AddDialog1.close)


def Add_Dialog_act_isp():
    '''Функция добавляет строку в таблицу Act_isp'''

    global AddDialog2
    AddDialog2 = QtWidgets.QWidget()
    ui_add_tab2 = Ui_AddDialog2()
    ui_add_tab2.setupUi(AddDialog2)
    AddDialog2.show()

    def add_date():
        '''Функция позволяет выбрать дату из календаря'''

        global Calendar
        Calendar = QtWidgets.QWidget()
        ui_cal = Ui_Calendar()
        ui_cal.setupUi(Calendar)
        Calendar.show()

        def add_and_close():
            global added_date  # выбранная дата из календаря
            added_date = ui_cal.calendarWidget.selectedDate()
            added_date = added_date.toString("dd.MM.yyyy")
            ui_add_tab2.line_date.setText(added_date)
            Calendar.close()

        ui_cal.CalendarCheck.clicked.connect(add_and_close)

    def sql_insert_query(new_values):
        '''Функция вставляет переданный кортеж в таблицу Act_isp и обновляет ее'''
        headers = get_headers('Act_isp')
        query = QSqlQuery()
        sql = 'INSERT INTO {} {} VALUES {}'.format('Act_isp', headers, new_values)
        query.prepare(sql)
        flag = query.exec()
        print(flag)
        act_isp.select()

        AddDialog2.close()

    def add_row_act_isp():

        new_values = tuple()
        regnum_Activ = get_all_Activ()[2]
        regnum_cell = ui_add_tab2.line_regnum.text()
        regnum_act_isp = get_all_act_isp()[0]
        exec_date_act_isp = get_all_act_isp()[1]


        # проверка кода бумаги
        if regnum_cell == '':
            ui_add_tab2.textBrowser.setText('Не указан код бумаги')
            return
        if regnum_cell.isdigit() != True:
            ui_add_tab2.textBrowser.setText('Введенный код неверного типа')
            return
        if len(regnum_cell) != 5:
            ui_add_tab2.textBrowser.setText('Недостаточно сиволов кода')
            return
        if 'SU' + regnum_cell + 'RMFS' in get_all_act_isp()[0]:
            ui_add_tab2.textBrowser.setText('Введенный код уже существует')
            return
        new_values += ('SU' + regnum_cell + 'RMFS',)

        # проверка на выбор даты
        if 'added_date' not in globals() or ui_add_tab2.line_date.text() == '':
            ui_add_tab2.textBrowser.setText('Не выбрана дата торгов')
            return
        if added_date in get_all_act_isp()[1]:
            ui_add_tab2.textBrowser.setText('Введеная дата уже существует')
            return

        print(new_values)
        sql_insert_query(new_values)

    ui_add_tab2.date_button.clicked.connect(add_date)
    ui_add_tab2.button_ok.clicked.connect(add_row_act_isp)
    ui_add_tab2.button_cancel.clicked.connect(AddDialog2.close)


def Edit_Dialog():
    '''Функция позволяет взаимодействовать с окном редактирования'''

    def ErrorDialog():
        '''Функция открывает окно с оповещением о том, что запись не выбрана'''
        global ErrorDialog
        ErrorDialog = QtWidgets.QDialog()
        ui = Ui_ErrorDialog()
        ui.setupUi(ErrorDialog)
        ErrorDialog.show()

        # закрытие диалогового окна при нажатии на кнопку
        ui.button_okk.clicked.connect(ErrorDialog.close)

    def sql_update_query(headers, price_cell, gain_end_cell):
        '''Функция делает sql запрос на обновление таблицы'''

        query = QSqlQuery()
        sql = 'UPDATE {} SET {} = "{}", {} = "{}" WHERE {} = "{}" AND {} = "{}" AND {} = "{}" AND {} = "{}" '. \
            format('Activ', headers[2], price_cell.replace('.',','),
                   headers[3], gain_end_cell.replace('.',','),
                   headers[0], list_values[0],
                   headers[1], list_values[1],
                   headers[2], list_values[2],
                   headers[3], list_values[3])

        query.prepare(sql)
        flag = query.exec()
        print(flag)
        Activ.select()

        # закрытие окна редактирования
        EditDialog.close()

    def edit_row():

        # создание переменных с соответсвующими текущими значениями, записанными в QLineEdit
        price_cell = ui.line_price.text()
        gain_end_cell = ui.line_gain_end.text()
        headers = get_headers('Activ')

        # проверка на правильность ввода текущей цены
        try:
            if float(price_cell.replace(',','.')) <= 0:
                ui.textBrowser.setText('Введено неверное значение цены')
                return
        except ValueError:
            ui.textBrowser.setText('Введено неверное значение цены')
            return

        # проверка на правильность ввода доходности
        try:
            if float(gain_end_cell.replace(',', '.')) <= 0:
                ui.textBrowser.setText('Введено неверное значение доходности')
                return
        except ValueError:
            ui.textBrowser.setText('Введено неверное значение доходности')
            return

        # проверка на наличие изменений
        if  [price_cell, gain_end_cell] == list_values[-2:]:
            ui.textBrowser.setText('Изменения не были внесены')
            return

        print(headers, price_cell, gain_end_cell)
        sql_update_query(headers, price_cell, gain_end_cell)

    list_values = get_row()
    if list_values == -1:
        ErrorDialog()

    else:

        global EditDialog
        EditDialog = QtWidgets.QDialog()
        ui = Ui_EditDialog()
        ui.setupUi(EditDialog)
        EditDialog.show()

        # преобразование значений вещественного типа в строчный тип
        list_values = [str(i) if type(i) != str else i for i in list_values]
        print(list_values)

        # отображение значений из таблицы в QLineEdit
        ui.line_torg_date.setText(list_values[0])
        ui.line_regnum.setText(list_values[1])
        ui.line_price.setText(list_values[2])
        ui.line_gain_end.setText(list_values[3])

        ui.button_ok.clicked.connect(edit_row)
        ui.button_cancel.clicked.connect(EditDialog.close)


def Delete_Dialog():
    '''Функция позволяет взаимодейстовать с окном удаления'''

    def remove_row():
        '''Функция удаляет выбранные строки'''
        selected = Ui_Main.tableView_Activ.selectedIndexes()
        index_set = set(index.row() for index in selected)  # множество индексов выбранных строк
        for index in index_set:
            Activ.removeRow(index)
        Activ.select()

        DeleteDialog.close()

    global DeleteDialog
    DeleteDialog = QtWidgets.QDialog()
    ui = Ui_DeleteDialog()
    ui.setupUi(DeleteDialog)
    DeleteDialog.show()

    ui.No_button.clicked.connect(DeleteDialog.close)
    ui.Yes_button.clicked.connect(remove_row)

def get_row():
    '''Функция возвращает список со значениями текущей строки,
    если строка не выбрана, то возвращает -1'''
    selected = Ui_Main.tableView_Activ.currentIndex().row()
    if selected == -1:
        return selected
    else:
        list_values = [Ui_Main.tableView_Activ.model().index(selected, i).data() for i in range(4)]
        return list_values

def get_Activ():
    '''Функция создает обьъект таблицу Activ'''
    global Activ
    Activ = QSqlTableModel()  # создаем объект
    Activ.setTable('Activ')  # привязываем к объекту таблицу
    Activ.select()  # выбираем все строки из таблицы
    return Activ

def get_act_isp():
    '''Функция создает объект таблицу act_isp'''
    global act_isp
    act_isp = QSqlTableModel()
    act_isp.setTable('act_isp')
    act_isp.select()
    return act_isp

if __name__ == "__main__":

    #Проверка подключения к базе данных
    if not connect_db(db_name):
        sys.exit(-1)
    else:
        print('Подключение прошло успешно')

    app = QtWidgets.QApplication(sys.argv)

    MainForm = QtWidgets.QMainWindow()
    Ui_Main = Ui_MainForm()
    Ui_Main.setupUi(MainForm)

    Ui_Main.tableView_Activ.setModel(get_Activ())
    Ui_Main.tableView_act_isp.setModel(get_act_isp())

    Ui_Main.delete_button.clicked.connect(Delete_Dialog)
    Ui_Main.edit_button.clicked.connect(Edit_Dialog)
    Ui_Main.add_button.clicked.connect(Add_Dialog)
    Ui_Main.filter_button.clicked.connect(set_filter)
    Ui_Main.exit_button.clicked.connect(MainForm.close)
    Ui_Main.rate_button.clicked.connect(get_rate)
    Ui_Main.analysis_button.clicked.connect(Analysis_Dialog)


    # выравнивание по ширине текста в столбце
    Ui_Main.tableView_Activ.resizeColumnsToContents()
    Ui_Main.tableView_act_isp.resizeColumnsToContents()

    #сортировка по столбцам
    Ui_Main.tableView_Activ.setSortingEnabled(True)
    Ui_Main.tableView_act_isp.setSortingEnabled(True)

    MainForm.show()
    sys.exit(app.exec())


