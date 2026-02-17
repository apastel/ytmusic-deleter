# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'delete_uploads_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
    QDialogButtonBox, QLabel, QSizePolicy, QSpinBox,
    QToolButton, QWidget)

class Ui_DeleteUploadsDialog(object):
    def setupUi(self, DeleteUploadsDialog):
        if not DeleteUploadsDialog.objectName():
            DeleteUploadsDialog.setObjectName(u"DeleteUploadsDialog")
        DeleteUploadsDialog.resize(393, 215)
        self.buttonBox = QDialogButtonBox(DeleteUploadsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 160, 341, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.infoLabel = QLabel(DeleteUploadsDialog)
        self.infoLabel.setObjectName(u"infoLabel")
        self.infoLabel.setGeometry(QRect(40, 20, 281, 31))
        self.addUploadsCheckBox = QCheckBox(DeleteUploadsDialog)
        self.addUploadsCheckBox.setObjectName(u"addUploadsCheckBox")
        self.addUploadsCheckBox.setGeometry(QRect(40, 80, 201, 16))
        self.scoreCutoffLabel = QLabel(DeleteUploadsDialog)
        self.scoreCutoffLabel.setObjectName(u"scoreCutoffLabel")
        self.scoreCutoffLabel.setEnabled(False)
        self.scoreCutoffLabel.setGeometry(QRect(40, 100, 131, 21))
        self.scoreCutoffInput = QSpinBox(DeleteUploadsDialog)
        self.scoreCutoffInput.setObjectName(u"scoreCutoffInput")
        self.scoreCutoffInput.setEnabled(False)
        self.scoreCutoffInput.setGeometry(QRect(170, 100, 42, 22))
        self.scoreCutoffInput.setMaximum(100)
        self.scoreCutoffInput.setValue(85)
        self.infoButton = QToolButton(DeleteUploadsDialog)
        self.infoButton.setObjectName(u"infoButton")
        self.infoButton.setGeometry(QRect(240, 90, 24, 24))
        self.infoButton.setAutoRaise(True)

        self.retranslateUi(DeleteUploadsDialog)
        self.buttonBox.accepted.connect(DeleteUploadsDialog.accept)
        self.buttonBox.rejected.connect(DeleteUploadsDialog.reject)

        QMetaObject.connectSlotsByName(DeleteUploadsDialog)
    # setupUi

    def retranslateUi(self, DeleteUploadsDialog):
        DeleteUploadsDialog.setWindowTitle(QCoreApplication.translate("DeleteUploadsDialog", u"Delete Uploads", None))
        self.infoLabel.setText(QCoreApplication.translate("DeleteUploadsDialog", u"This will delete all your uploaded music.", None))
        self.addUploadsCheckBox.setText(QCoreApplication.translate("DeleteUploadsDialog", u"Add uploads to library first", None))
        self.scoreCutoffLabel.setText(QCoreApplication.translate("DeleteUploadsDialog", u"Match score cutoff:", None))
        self.infoButton.setText(QCoreApplication.translate("DeleteUploadsDialog", u"...", None))
    # retranslateUi

