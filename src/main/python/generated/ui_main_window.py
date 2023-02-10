# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.4.0
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
        self.removeLibraryButton.setGeometry(QRect(40, 130, 121, 41))
        self.consoleTextArea = QPlainTextEdit(self.centralwidget)
        self.consoleTextArea.setObjectName(u"consoleTextArea")
        self.consoleTextArea.setGeometry(QRect(40, 270, 721, 271))
        self.consoleTextArea.setReadOnly(True)
        self.deleteUploadsButton = QPushButton(self.centralwidget)
        self.deleteUploadsButton.setObjectName(u"deleteUploadsButton")
        self.deleteUploadsButton.setGeometry(QRect(170, 130, 121, 41))
        self.consoleLabel = QLabel(self.centralwidget)
        self.consoleLabel.setObjectName(u"consoleLabel")
        self.consoleLabel.setGeometry(QRect(40, 250, 81, 21))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(10)
        self.consoleLabel.setFont(font)
        self.authIndicator = QPushButton(self.centralwidget)
        self.authIndicator.setObjectName(u"authIndicator")
        self.authIndicator.setGeometry(QRect(40, 30, 101, 41))
        self.deletePlaylistsButton = QPushButton(self.centralwidget)
        self.deletePlaylistsButton.setObjectName(u"deletePlaylistsButton")
        self.deletePlaylistsButton.setGeometry(QRect(300, 130, 121, 41))
        self.unlikeAllButton = QPushButton(self.centralwidget)
        self.unlikeAllButton.setObjectName(u"unlikeAllButton")
        self.unlikeAllButton.setGeometry(QRect(430, 130, 121, 41))
        self.deleteAllButton = QPushButton(self.centralwidget)
        self.deleteAllButton.setObjectName(u"deleteAllButton")
        self.deleteAllButton.setGeometry(QRect(570, 130, 121, 41))
        self.sortPlaylistButton = QPushButton(self.centralwidget)
        self.sortPlaylistButton.setObjectName(u"sortPlaylistButton")
        self.sortPlaylistButton.setGeometry(QRect(40, 190, 121, 41))
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


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"YTMusic Deleter", None))
        self.removeLibraryButton.setText(QCoreApplication.translate("MainWindow", u"Remove Library", None))
        self.deleteUploadsButton.setText(QCoreApplication.translate("MainWindow", u"Delete Uploads", None))
        self.consoleLabel.setText(QCoreApplication.translate("MainWindow", u"Console Log", None))
        self.authIndicator.setText(QCoreApplication.translate("MainWindow", u"Unauthenticated", None))
        self.deletePlaylistsButton.setText(QCoreApplication.translate("MainWindow", u"Delete Playlists", None))
        self.unlikeAllButton.setText(QCoreApplication.translate("MainWindow", u"Unlike All Songs", None))
        self.deleteAllButton.setText(QCoreApplication.translate("MainWindow", u"Delete All", None))
        self.sortPlaylistButton.setText(QCoreApplication.translate("MainWindow", u"Sort Playlist", None))
    # retranslateUi

