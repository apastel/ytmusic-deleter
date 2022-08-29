# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'auth_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.3.1
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QLineEdit, QPlainTextEdit, QPushButton,
    QSizePolicy, QWidget)

class Ui_AuthDialog(object):
    def setupUi(self, AuthDialog):
        if not AuthDialog.objectName():
            AuthDialog.setObjectName(u"AuthDialog")
        AuthDialog.resize(569, 438)
        self.buttonBox = QDialogButtonBox(AuthDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setEnabled(True)
        self.buttonBox.setGeometry(QRect(200, 360, 171, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.headersInputBox = QPlainTextEdit(AuthDialog)
        self.headersInputBox.setObjectName(u"headersInputBox")
        self.headersInputBox.setGeometry(QRect(60, 20, 451, 251))
        self.orLabel = QLabel(AuthDialog)
        self.orLabel.setObjectName(u"orLabel")
        self.orLabel.setGeometry(QRect(280, 280, 21, 16))
        self.browseButton = QPushButton(AuthDialog)
        self.browseButton.setObjectName(u"browseButton")
        self.browseButton.setGeometry(QRect(140, 300, 75, 23))
        self.fileNameField = QLineEdit(AuthDialog)
        self.fileNameField.setObjectName(u"fileNameField")
        self.fileNameField.setEnabled(False)
        self.fileNameField.setGeometry(QRect(230, 300, 241, 21))

        self.retranslateUi(AuthDialog)
        self.buttonBox.accepted.connect(AuthDialog.accept)
        self.buttonBox.rejected.connect(AuthDialog.reject)

        QMetaObject.connectSlotsByName(AuthDialog)
    # setupUi

    def retranslateUi(self, AuthDialog):
        AuthDialog.setWindowTitle(QCoreApplication.translate("AuthDialog", u"Authentication", None))
        self.orLabel.setText(QCoreApplication.translate("AuthDialog", u"Or", None))
        self.browseButton.setText(QCoreApplication.translate("AuthDialog", u"Browse", None))
    # retranslateUi

