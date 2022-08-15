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
        self.removeLibraryButton.setGeometry(QtCore.QRect(40, 130, 121, 41))
        self.removeLibraryButton.setDefault(False)
        self.removeLibraryButton.setObjectName("removeLibraryButton")
        self.consoleTextArea = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.consoleTextArea.setGeometry(QtCore.QRect(40, 270, 721, 271))
        self.consoleTextArea.setReadOnly(True)
        self.consoleTextArea.setObjectName("consoleTextArea")
        self.deleteUploadsButton = QtWidgets.QPushButton(self.centralwidget)
        self.deleteUploadsButton.setGeometry(QtCore.QRect(170, 130, 121, 41))
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
        self.deletePlaylistsButton = QtWidgets.QPushButton(self.centralwidget)
        self.deletePlaylistsButton.setGeometry(QtCore.QRect(300, 130, 121, 41))
        self.deletePlaylistsButton.setDefault(False)
        self.deletePlaylistsButton.setObjectName("deletePlaylistsButton")
        self.unlikeAllButton = QtWidgets.QPushButton(self.centralwidget)
        self.unlikeAllButton.setGeometry(QtCore.QRect(430, 130, 121, 41))
        self.unlikeAllButton.setDefault(False)
        self.unlikeAllButton.setObjectName("unlikeAllButton")
        self.deleteAllButton = QtWidgets.QPushButton(self.centralwidget)
        self.deleteAllButton.setGeometry(QtCore.QRect(570, 130, 121, 41))
        self.deleteAllButton.setDefault(False)
        self.deleteAllButton.setObjectName("deleteAllButton")
        self.sortPlaylistButton = QtWidgets.QPushButton(self.centralwidget)
        self.sortPlaylistButton.setGeometry(QtCore.QRect(40, 190, 121, 41))
        self.sortPlaylistButton.setDefault(False)
        self.sortPlaylistButton.setObjectName("sortPlaylistButton")
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
        self.deletePlaylistsButton.setText(_translate("MainWindow", "Delete Playlists"))
        self.unlikeAllButton.setText(_translate("MainWindow", "Unlike All Songs"))
        self.deleteAllButton.setText(_translate("MainWindow", "Delete All"))
        self.sortPlaylistButton.setText(_translate("MainWindow", "Sort Playlist"))

