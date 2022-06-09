# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/main/resources/main_window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.removeLibraryButton = QtWidgets.QPushButton(self.centralwidget)
        self.removeLibraryButton.setGeometry(QtCore.QRect(330, 70, 121, 41))
        self.removeLibraryButton.setDefault(False)
        self.removeLibraryButton.setObjectName("removeLibraryButton")
        self.consoleTextArea = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.consoleTextArea.setGeometry(QtCore.QRect(40, 270, 721, 271))
        self.consoleTextArea.setReadOnly(True)
        self.consoleTextArea.setObjectName("consoleTextArea")
        self.deleteUploadsButton = QtWidgets.QPushButton(self.centralwidget)
        self.deleteUploadsButton.setGeometry(QtCore.QRect(330, 130, 121, 41))
        self.deleteUploadsButton.setDefault(False)
        self.deleteUploadsButton.setObjectName("deleteUploadsButton")
        self.consoleLabel = QtWidgets.QLabel(self.centralwidget)
        self.consoleLabel.setGeometry(QtCore.QRect(40, 250, 81, 21))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.consoleLabel.setFont(font)
        self.consoleLabel.setObjectName("consoleLabel")
        self.authIndicator = QtWidgets.QPushButton(self.centralwidget)
        self.authIndicator.setGeometry(QtCore.QRect(40, 30, 101, 41))
        self.authIndicator.setObjectName("authIndicator")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "YTMusic Deleter"))
        self.removeLibraryButton.setText(_translate("MainWindow", "Remove Library"))
        self.deleteUploadsButton.setText(_translate("MainWindow", "Delete Uploads"))
        self.consoleLabel.setText(_translate("MainWindow", "Console Log"))
        self.authIndicator.setText(_translate("MainWindow", "Unauthenticated"))

