# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferences_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QSizePolicy, QWidget)

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        if not PreferencesDialog.objectName():
            PreferencesDialog.setObjectName(u"PreferencesDialog")
        PreferencesDialog.setWindowModality(Qt.ApplicationModal)
        PreferencesDialog.resize(497, 300)
        PreferencesDialog.setModal(True)
        self.buttonBox = QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(390, 20, 81, 241))
        self.buttonBox.setOrientation(Qt.Vertical)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.verboseCheckBox = QCheckBox(PreferencesDialog)
        self.verboseCheckBox.setObjectName(u"verboseCheckBox")
        self.verboseCheckBox.setGeometry(QRect(30, 20, 241, 41))
        self.oauthCheckbox = QCheckBox(PreferencesDialog)
        self.oauthCheckbox.setObjectName(u"oauthCheckbox")
        self.oauthCheckbox.setGeometry(QRect(30, 60, 351, 41))

        self.retranslateUi(PreferencesDialog)
        self.buttonBox.accepted.connect(PreferencesDialog.accept)
        self.buttonBox.rejected.connect(PreferencesDialog.reject)

        QMetaObject.connectSlotsByName(PreferencesDialog)
    # setupUi

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(QCoreApplication.translate("PreferencesDialog", u"Preferences", None))
#if QT_CONFIG(tooltip)
        self.verboseCheckBox.setToolTip(QCoreApplication.translate("PreferencesDialog", u"Enables verbose or \"debug\" logging in the application.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.verboseCheckBox.setStatusTip(QCoreApplication.translate("PreferencesDialog", u"Enables verbose or \"debug\" logging in the application.", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.verboseCheckBox.setWhatsThis(QCoreApplication.translate("PreferencesDialog", u"Enables verbose or \"debug\" logging in the application.", None))
#endif // QT_CONFIG(whatsthis)
        self.verboseCheckBox.setText(QCoreApplication.translate("PreferencesDialog", u"Enable verbose logging", None))
#if QT_CONFIG(tooltip)
        self.oauthCheckbox.setToolTip(QCoreApplication.translate("PreferencesDialog", u"Enables user-friendly authentication using OAuth (may not work)", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.oauthCheckbox.setStatusTip(QCoreApplication.translate("PreferencesDialog", u"Enables user-friendly authentication using OAuth (may not work)", None))
#endif // QT_CONFIG(statustip)
#if QT_CONFIG(whatsthis)
        self.oauthCheckbox.setWhatsThis(QCoreApplication.translate("PreferencesDialog", u"Enables user-friendly authentication using OAuth (may not work)", None))
#endif // QT_CONFIG(whatsthis)
        self.oauthCheckbox.setText(QCoreApplication.translate("PreferencesDialog", u"Enable OAuth login (may not work)", None))
    # retranslateUi

