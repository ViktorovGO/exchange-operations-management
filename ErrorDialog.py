# Form implementation generated from reading ui file 'ErrorDialog.ui'
#
# Created by: PyQt6 UI code generator 6.3.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_ErrorDialog(object):
    def setupUi(self, ErrorDialog):
        ErrorDialog.setObjectName("ErrorDialog")
        ErrorDialog.resize(331, 128)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("dollar.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        ErrorDialog.setWindowIcon(icon)
        self.button_okk = QtWidgets.QDialogButtonBox(ErrorDialog)
        self.button_okk.setGeometry(QtCore.QRect(131, 80, 71, 23))
        self.button_okk.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.button_okk.setObjectName("button_okk")
        self.label = QtWidgets.QLabel(ErrorDialog)
        self.label.setGeometry(QtCore.QRect(80, 20, 172, 51))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")

        self.retranslateUi(ErrorDialog)
        QtCore.QMetaObject.connectSlotsByName(ErrorDialog)

    def retranslateUi(self, ErrorDialog):
        _translate = QtCore.QCoreApplication.translate
        ErrorDialog.setWindowTitle(_translate("ErrorDialog", "Ошибка!"))
        self.label.setText(_translate("ErrorDialog", "Ошибка! Запись не выбрана."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ErrorDialog = QtWidgets.QDialog()
    ui = Ui_ErrorDialog()
    ui.setupUi(ErrorDialog)
    ErrorDialog.show()
    sys.exit(app.exec())