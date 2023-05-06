from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic, QtCore
import sys

class UI_P(QDialog):
    def __init__(self):
        super(UI_P, self).__init__()

        uic.loadUi("D:\\Undip\\Kerja Praktek\\Prototype PyQt5\\Prototype.Download data\\Dialog-box.progress-download.ui", self)

        self.pushButton = self.findChild(QPushButton, "pushButton")

        self.pushButton.clicked.connect(self.click)

        self.show()
        
    def click(self):
        self.close()

class UI(QMainWindow):
    
    def __init__(self):
        super(UI, self).__init__()

        uic.loadUi("D:\\Undip\\Kerja Praktek\\Prototype PyQt5\\Prototype.Download data\\Main-window.download-data.ui", self)

        self.pushButton = self.findChild(QPushButton, "pushButton")
        self.searchButton = self.findChild(QToolButton, "searchButton")
        self.label_yourdir = self.findChild(QLabel, "label_yourdir")
        self.f_date = self.findChild(QFrame, "f_date")
        
        self.dateStart = self.findChild(QDateEdit, "dateStart")
        self.dateEnd = self.findChild(QDateEdit, "dateEnd")

        self.pushButton.clicked.connect(self.openDialog)
        self.searchButton.clicked.connect(self.openDir)

        self.dateStart = QtWidgets.QDateEdit(self.f_date, calendarPopup=True)
        self.dateStart.setDate(QtCore.QDate(2020, 2, 2))
        self.dateStart.setGeometry(QtCore.QRect(60, 30, 161, 41))
        self.dateStart.setObjectName("dateStart")

        self.dateEnd = QtWidgets.QDateEdit(self.f_date, calendarPopup=True)
        self.dateStart.setDate(QtCore.QDate(2020, 2, 2))
        self.dateEnd.setGeometry(QtCore.QRect(310, 30, 161, 41))
        self.dateEnd.setObjectName("dateEnd")

        self.show()

    def openDir(self):
        fname = QFileDialog.getExistingDirectory(self, "Open Folder")
        if fname:
            self.label_yourdir.setText(str(fname))

    def openDialog(self):
        # self.win = QApplication(sys.argv)
        self.ui = UI_P()
        # self.ui.__init__()
        # self.win.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = UI()
    app.exec_()