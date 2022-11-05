# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'license_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QLabel, QLineEdit, QPlainTextEdit, QPushButton,
    QSizePolicy, QWidget)

class Ui_LicenseDialog(object):
    def setupUi(self, LicenseDialog):
        if not LicenseDialog.objectName():
            LicenseDialog.setObjectName(u"LicenseDialog")
        LicenseDialog.setWindowModality(Qt.ApplicationModal)
        LicenseDialog.resize(569, 438)
        self.buttonBox = QDialogButtonBox(LicenseDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setEnabled(True)
        self.buttonBox.setGeometry(QRect(200, 360, 171, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.licenseInputBox = QPlainTextEdit(LicenseDialog)
        self.licenseInputBox.setObjectName(u"licenseInputBox")
        self.licenseInputBox.setGeometry(QRect(60, 20, 451, 251))
        self.orLabel = QLabel(LicenseDialog)
        self.orLabel.setObjectName(u"orLabel")
        self.orLabel.setGeometry(QRect(280, 280, 21, 16))
        self.browseButton = QPushButton(LicenseDialog)
        self.browseButton.setObjectName(u"browseButton")
        self.browseButton.setGeometry(QRect(140, 300, 75, 23))
        self.fileNameField = QLineEdit(LicenseDialog)
        self.fileNameField.setObjectName(u"fileNameField")
        self.fileNameField.setEnabled(False)
        self.fileNameField.setGeometry(QRect(230, 300, 241, 21))

        self.retranslateUi(LicenseDialog)
        self.buttonBox.accepted.connect(LicenseDialog.accept)
        self.buttonBox.rejected.connect(LicenseDialog.reject)

        QMetaObject.connectSlotsByName(LicenseDialog)
    # setupUi

    def retranslateUi(self, LicenseDialog):
        LicenseDialog.setWindowTitle(QCoreApplication.translate("LicenseDialog", u"License Key", None))
        self.orLabel.setText(QCoreApplication.translate("LicenseDialog", u"Or", None))
        self.browseButton.setText(QCoreApplication.translate("LicenseDialog", u"Browse", None))
    # retranslateUi

