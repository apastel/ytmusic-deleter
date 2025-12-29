# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        SettingsDialog.resize(497, 300)
        SettingsDialog.setModal(True)
        self.buttonBox = QDialogButtonBox(SettingsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(390, 20, 81, 71))
        self.buttonBox.setOrientation(Qt.Orientation.Vertical)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.verboseCheckBox = QCheckBox(SettingsDialog)
        self.verboseCheckBox.setObjectName(u"verboseCheckBox")
        self.verboseCheckBox.setGeometry(QRect(30, 20, 241, 41))
        self.oauthCheckbox = QCheckBox(SettingsDialog)
        self.oauthCheckbox.setObjectName(u"oauthCheckbox")
        self.oauthCheckbox.setGeometry(QRect(30, 60, 151, 41))
        self.openDataDirButton = QPushButton(SettingsDialog)
        self.openDataDirButton.setObjectName(u"openDataDirButton")
        self.openDataDirButton.setGeometry(QRect(400, 200, 91, 23))
        self.dataDirPathDisplay = QLineEdit(SettingsDialog)
        self.dataDirPathDisplay.setObjectName(u"dataDirPathDisplay")
        self.dataDirPathDisplay.setEnabled(False)
        self.dataDirPathDisplay.setGeometry(QRect(50, 200, 341, 20))
        self.dataDirPathDisplay.setReadOnly(True)
        self.dataDirLabel = QLabel(SettingsDialog)
        self.dataDirLabel.setObjectName(u"dataDirLabel")
        self.dataDirLabel.setGeometry(QRect(50, 180, 331, 16))
        self.verticalLayoutWidget = QWidget(SettingsDialog)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(50, 100, 331, 52))
        self.verticalLayoutOauth = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayoutOauth.setObjectName(u"verticalLayoutOauth")
        self.verticalLayoutOauth.setContentsMargins(0, 0, 0, 0)
        self.clientIdInput = QLineEdit(self.verticalLayoutWidget)
        self.clientIdInput.setObjectName(u"clientIdInput")

        self.verticalLayoutOauth.addWidget(self.clientIdInput)

        self.clientSecretInput = QLineEdit(self.verticalLayoutWidget)
        self.clientSecretInput.setObjectName(u"clientSecretInput")

        self.verticalLayoutOauth.addWidget(self.clientSecretInput)

        self.oauthInfoButton = QPushButton(SettingsDialog)
        self.oauthInfoButton.setObjectName(u"oauthInfoButton")
        self.oauthInfoButton.setGeometry(QRect(180, 70, 21, 22))
        self.oauthInfoButton.setStyleSheet(u"QPushButton {\n"
"    background-position: center;\n"
"    background-repeat: no-repeat;\n"
"    border-radius: 5px;\n"
"}")

        self.retranslateUi(SettingsDialog)
        self.buttonBox.accepted.connect(SettingsDialog.accept)
        self.buttonBox.rejected.connect(SettingsDialog.reject)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Settings", None))
#if QT_CONFIG(tooltip)
        self.verboseCheckBox.setToolTip(QCoreApplication.translate("SettingsDialog", u"Enables verbose or \"debug\" logging in the application.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.verboseCheckBox.setStatusTip(QCoreApplication.translate("SettingsDialog", u"Enables verbose or \"debug\" logging in the application.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.verboseCheckBox.setWhatsThis(QCoreApplication.translate("SettingsDialog", u"Enables verbose or \"debug\" logging in the application.", None))
#endif // QT_CONFIG(whatsthis)
        self.verboseCheckBox.setText(QCoreApplication.translate("SettingsDialog", u"Enable verbose logging", None))
#if QT_CONFIG(tooltip)
        self.oauthCheckbox.setToolTip(QCoreApplication.translate("SettingsDialog", u"Changes authentication method from browser to OAuth", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.oauthCheckbox.setStatusTip(QCoreApplication.translate("SettingsDialog", u"Changes authentication method from browser to OAuth", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.oauthCheckbox.setWhatsThis(QCoreApplication.translate("SettingsDialog", u"Changes authentication method from browser to OAuth", None))
#endif // QT_CONFIG(whatsthis)
        self.oauthCheckbox.setText(QCoreApplication.translate("SettingsDialog", u"Enable OAuth login", None))
        self.openDataDirButton.setText(QCoreApplication.translate("SettingsDialog", u"Open Folder", None))
        self.dataDirLabel.setText(QCoreApplication.translate("SettingsDialog", u"App data directory: (logs and auth files are saved here)", None))
        self.clientIdInput.setPlaceholderText(QCoreApplication.translate("SettingsDialog", u"client_id", None))
        self.clientSecretInput.setPlaceholderText(QCoreApplication.translate("SettingsDialog", u"client_secret", None))
        self.oauthInfoButton.setText("")
    # retranslateUi

