from PyQt6.QtSql import *
import sys
import sqlite3
from datetime import datetime
from PyQt6 import uic, QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QIcon
from MainForm import Ui_MainForm
from DeleteDialog import Ui_DeleteDialog
from EditDialog import Ui_EditDialog
from ErrorDialog import Ui_ErrorDialog
from AddDialog import Ui_AddDialog
from Calendar import Ui_Calendar

db_name = 'databases/db_ocb_1.db'

def connect_db(db_name):
    '''Функция устанавливает соединение с базой данных'''
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_name)
    if not db.open():
        print('Не удалось подключиться к базе')
        return False
    return db

def get_headers():
    '''Функция возвращает заголовки таблицы'''
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    sql = 'SELECT name FROM PRAGMA_TABLE_INFO("{}")'.format('Activ')
    headers = tuple(header[0] for header in cur.execute(sql).fetchall())
    cur.close()
    con.close()
    return headers

def set_filter():
    ''''Функция фильтрует по заданным параметрам'''

    # Считывание введённых фильтров
    date_start = ui.date_start.text()
    date_end = ui.date_end.text()
    key = ui.key_list.text()
    price_start = ui.price_start.text()
    price_end = ui.price_end.text()
    gain_start = ui.gain_start.text()
    gain_end = ui.gain_end.text()
    date_start = '"{}"'.format(date_start)
    date_end ='"{}"'.format(date_end)
    key = '"{}"'.format(key)

    # Фильтрация
    sql = 'дата_торгов >= {} and дата_торгов <= {} and код_бумаги = {} and цена >= {} '\
          'and цена <= {} and текущая_доходность >= {} and текущая_доходность <= {}'\
        .format(date_start, date_end, key, price_start, price_end, gain_start, gain_end)
    sql = 'дата_торгов >= "1996-07-01" and дата_торгов <= "1996-07-12"'

    Activ.setFilter(sql)
    print(sql)

def Add_Dialog():
    '''Функция позволяет взаимодействовать с окном добавления'''
    
    
    def add_date():
        def add_and_close():
            global added_date
            added_date=ui_2.calendarWidget.selectedDate()
            added_date=str(added_date)
            added_date=added_date[19:30]
            added_date=added_date.replace(',', '-')
            added_date=added_date.split()
            added_date="".join(added_date)
            
            Calendar.close()

        Calendar.show()
        ui_2.CalendarCheck.clicked.connect(add_and_close)
    
    global AddDialog
    global Calendar
    
    AddDialog = QtWidgets.QWidget()
    ui = Ui_AddDialog()
    ui.setupUi(AddDialog)
    AddDialog.show()
    
    Calendar = QtWidgets.QWidget()
    ui_2 = Ui_Calendar()
    ui_2.setupUi(Calendar)
    
    ui.pushCalendar.clicked.connect(add_date)
    

    
        

    def sql_insert_query(lst_data):
        headers = get_headers()
        query = QSqlQuery()
        sql = 'INSERT INTO {} {} VALUES {}'.format('Activ', headers, lst_data)
        query.prepare(sql)
        flag = query.exec()
        print(flag)
        Activ.select()

        AddDialog.close()

    def add_row():

        lst_data = tuple()
        lst_data += (added_date,)
        lst_data += (ui.comboBox_regnum.currentText(),)
        price_cell = ui.line_price.text()
        gain_end_cell = ui.line_gain_end.text()

        # проверка на ввод всех значений
        if price_cell is '' or gain_end_cell is '':
            ui.textBrowser.setText('Введены не все значения')
            return

        # проверка на правильность ввода текущей цены
        try:
            if float(price_cell) <= 0:
                ui.textBrowser.setText('Введено неверное значение цены')
                return
            else:
                lst_data += (float(price_cell),)
        except ValueError:
            ui.textBrowser.setText('Введено неверное значение цены')
            return

        # проверка на правильность ввода доходности
        try:
            if float(gain_end_cell) <= 0:
                ui.textBrowser.setText('Введено неверное значение доходности')
                return
            else:
                lst_data += (float(gain_end_cell),)
        except ValueError:
            ui.textBrowser.setText('Введено неверное значение доходности')
            return

        print(lst_data)
        sql_insert_query(lst_data)

    ui.button_ok.clicked.connect(add_row)
    ui.button_cancel.clicked.connect(AddDialog.close)


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
        '''функция делает sql запрос на обновление таблицы'''

        query = QSqlQuery()
        sql = 'UPDATE {} SET {} = "{}", {} = "{}" WHERE {} = "{}" AND {} = "{}" AND {} = "{}" AND {} = "{}" '. \
            format('Activ', headers[2], float(price_cell),
                   headers[3], float(gain_end_cell),
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
        headers = get_headers()

        # проверка на правильность ввода текущей цены
        try:
            if float(price_cell) <= 0:
                ui.textBrowser.setText('Введено неверное значение цены')
                return
        except ValueError:
            ui.textBrowser.setText('Введено неверное значение цены')
            return

        # проверка на правильность ввода доходности
        try:
            if float(gain_end_cell) <= 0:
                ui.textBrowser.setText('Введено неверное значение доходности')
                return
        except ValueError:
            ui.textBrowser.setText('Введено неверное значение доходности')
            return

        # проверка на наличие изменений
        if  [price_cell, gain_end_cell] == list_values[-2:]:
            ui.textBrowser.setText('Изменения не были внесены')
            return

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

        # отображение значений из таблицы в QLineEdit
        ui.line_torg_date.setText(list_values[0])
        ui.line_regnum.setText(list_values[1])
        ui.line_price.setText(list_values[2])
        ui.line_gain_end.setText(list_values[3])

        ui.button_ok.clicked.connect(edit_row)
        ui.button_cancel.clicked.connect(EditDialog.close)


def Delete_Dialog():
    '''Функция позволяет взаимодейстовать с окном удаления'''

    global DeleteDialog

    DeleteDialog = QtWidgets.QDialog()
    ui = Ui_DeleteDialog()
    ui.setupUi(DeleteDialog)
    DeleteDialog.show()

    ui.No_button.clicked.connect(DeleteDialog.close)
    ui.Yes_button.clicked.connect(remove_row)

def remove_row():
    '''Функция удаляет выбранные строки'''
    selected = ui.tableView_Activ.selectedIndexes()
    index_set = set(index.row() for index in selected)  # множество индексов выбранных строк
    for index in index_set:
        Activ.removeRow(index)
    Activ.select()

    DeleteDialog.close()


def get_row():
    '''Функция возвращает список со значениями текущей строки,
    если строка не выбрана, то возвращает -1'''
    selected = ui.tableView_Activ.currentIndex().row()
    if selected == -1:
        return selected
    else:
        list_values = [ui.tableView_Activ.model().index(selected, i).data() for i in range(4)]
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
    ui = Ui_MainForm()
    ui.setupUi(MainForm)


    ui.tableView_Activ.setModel(get_Activ())
    ui.tableView_act_isp.setModel(get_act_isp())

    ui.delete_button.clicked.connect(Delete_Dialog)
    ui.edit_button.clicked.connect(Edit_Dialog)
    ui.add_button.clicked.connect(Add_Dialog)
    ui.filter_button.clicked.connect(set_filter)
    ui.exit_button.clicked.connect(MainForm.close)
    # выравнивание по ширине текста в столбце
    ui.tableView_Activ.resizeColumnsToContents()
    ui.tableView_act_isp.resizeColumnsToContents()

    #сортировка по столбцам
    ui.tableView_Activ.setSortingEnabled(True)

    MainForm.show()
    sys.exit(app.exec())


