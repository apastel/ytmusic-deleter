# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QMenuBar,
    QPlainTextEdit, QPushButton, QSizePolicy, QStatusBar,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.removeLibraryButton = QPushButton(self.centralwidget)
        self.removeLibraryButton.setObjectName(u"removeLibraryButton")
        self.removeLibraryButton.setGeometry(QRect(220, 140, 101, 41))
        self.consoleTextArea = QPlainTextEdit(self.centralwidget)
        self.consoleTextArea.setObjectName(u"consoleTextArea")
        self.consoleTextArea.setGeometry(QRect(40, 270, 721, 271))
        self.consoleTextArea.setReadOnly(True)
        self.deleteUploadsButton = QPushButton(self.centralwidget)
        self.deleteUploadsButton.setObjectName(u"deleteUploadsButton")
        self.deleteUploadsButton.setGeometry(QRect(330, 140, 101, 41))
        self.consoleLabel = QLabel(self.centralwidget)
        self.consoleLabel.setObjectName(u"consoleLabel")
        self.consoleLabel.setGeometry(QRect(40, 250, 81, 21))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        self.consoleLabel.setFont(font)
        self.authIndicator = QPushButton(self.centralwidget)
        self.authIndicator.setObjectName(u"authIndicator")
        self.authIndicator.setGeometry(QRect(40, 50, 121, 41))
        self.deletePlaylistsButton = QPushButton(self.centralwidget)
        self.deletePlaylistsButton.setObjectName(u"deletePlaylistsButton")
        self.deletePlaylistsButton.setGeometry(QRect(440, 140, 101, 41))
        self.unlikeAllButton = QPushButton(self.centralwidget)
        self.unlikeAllButton.setObjectName(u"unlikeAllButton")
        self.unlikeAllButton.setGeometry(QRect(550, 140, 101, 41))
        self.deleteAllButton = QPushButton(self.centralwidget)
        self.deleteAllButton.setObjectName(u"deleteAllButton")
        self.deleteAllButton.setGeometry(QRect(40, 140, 121, 41))
        self.sortPlaylistButton = QPushButton(self.centralwidget)
        self.sortPlaylistButton.setObjectName(u"sortPlaylistButton")
        self.sortPlaylistButton.setGeometry(QRect(220, 210, 101, 41))
        self.deleteHistoryButton = QPushButton(self.centralwidget)
        self.deleteHistoryButton.setObjectName(u"deleteHistoryButton")
        self.deleteHistoryButton.setGeometry(QRect(660, 140, 101, 41))
        self.orLabel = QLabel(self.centralwidget)
        self.orLabel.setObjectName(u"orLabel")
        self.orLabel.setGeometry(QRect(180, 150, 21, 21))
        self.orLabel.setFont(font)
        self.accountNameLabel = QLabel(self.centralwidget)
        self.accountNameLabel.setObjectName(u"accountNameLabel")
        self.accountNameLabel.setGeometry(QRect(330, 50, 161, 31))
        self.accountPhotoLabel = QLabel(self.centralwidget)
        self.accountPhotoLabel.setObjectName(u"accountPhotoLabel")
        self.accountPhotoLabel.setGeometry(QRect(190, 10, 108, 108))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.removeLibraryButton.setDefault(False)
        self.deleteUploadsButton.setDefault(False)
        self.deletePlaylistsButton.setDefault(False)
        self.unlikeAllButton.setDefault(False)
        self.deleteAllButton.setDefault(False)
        self.sortPlaylistButton.setDefault(False)
        self.deleteHistoryButton.setDefault(False)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"YTMusic Deleter", None))
        self.removeLibraryButton.setText(QCoreApplication.translate("MainWindow", u"Remove Library", None))
        self.deleteUploadsButton.setText(QCoreApplication.translate("MainWindow", u"Delete Uploads", None))
        self.consoleLabel.setText(QCoreApplication.translate("MainWindow", u"Console Log", None))
        self.authIndicator.setText(QCoreApplication.translate("MainWindow", u"Log In", None))
        self.deletePlaylistsButton.setText(QCoreApplication.translate("MainWindow", u"Delete Playlists", None))
        self.unlikeAllButton.setText(QCoreApplication.translate("MainWindow", u"Unlike All", None))
        self.deleteAllButton.setText(QCoreApplication.translate("MainWindow", u"Delete All", None))
        self.sortPlaylistButton.setText(QCoreApplication.translate("MainWindow", u"Sort Playlist", None))
        self.deleteHistoryButton.setText(QCoreApplication.translate("MainWindow", u"Delete History", None))
        self.orLabel.setText(QCoreApplication.translate("MainWindow", u"OR", None))
        self.accountNameLabel.setText(QCoreApplication.translate("MainWindow", u"Account Name", None))
        self.accountPhotoLabel.setText(QCoreApplication.translate("MainWindow", u"[Insert Photo Here]", None))
    # retranslateUi

