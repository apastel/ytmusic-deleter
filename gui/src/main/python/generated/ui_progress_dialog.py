# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'progress_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QProgressBar,
    QPushButton, QSizePolicy, QWidget)

class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog):
        if not ProgressDialog.objectName():
            ProgressDialog.setObjectName(u"ProgressDialog")
        ProgressDialog.setWindowModality(Qt.ApplicationModal)
        ProgressDialog.resize(473, 220)
        self.progressBar = QProgressBar(ProgressDialog)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(100, 100, 291, 23))
        self.progressBar.setValue(0)
        self.abortButton = QPushButton(ProgressDialog)
        self.abortButton.setObjectName(u"abortButton")
        self.abortButton.setGeometry(QRect(200, 170, 75, 23))
        self.itemLine = QLabel(ProgressDialog)
        self.itemLine.setObjectName(u"itemLine")
        self.itemLine.setGeometry(QRect(50, 60, 371, 20))
        self.itemLine.setAlignment(Qt.AlignCenter)

        self.retranslateUi(ProgressDialog)

        QMetaObject.connectSlotsByName(ProgressDialog)
    # setupUi

    def retranslateUi(self, ProgressDialog):
        ProgressDialog.setWindowTitle(QCoreApplication.translate("ProgressDialog", u"Progress", None))
        self.abortButton.setText(QCoreApplication.translate("ProgressDialog", u"Abort", None))
        self.itemLine.setText("")
    # retranslateUi

