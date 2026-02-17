# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'checkbox_track_listing.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget)

class Ui_CheckboxTrackListingDialog(object):
    def setupUi(self, CheckboxTrackListingDialog):
        if not CheckboxTrackListingDialog.objectName():
            CheckboxTrackListingDialog.setObjectName(u"CheckboxTrackListingDialog")
        CheckboxTrackListingDialog.resize(924, 622)
        self.verticalLayoutWidget = QWidget(CheckboxTrackListingDialog)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(160, 520, 631, 81))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.navigationButtonLayout = QHBoxLayout()
        self.navigationButtonLayout.setObjectName(u"navigationButtonLayout")
        self.navigationButtonLayout.setContentsMargins(-1, 0, -1, -1)
        self.leftButton = QPushButton(self.verticalLayoutWidget)
        self.leftButton.setObjectName(u"leftButton")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leftButton.sizePolicy().hasHeightForWidth())
        self.leftButton.setSizePolicy(sizePolicy)

        self.navigationButtonLayout.addWidget(self.leftButton)

        self.rightButton = QPushButton(self.verticalLayoutWidget)
        self.rightButton.setObjectName(u"rightButton")
        sizePolicy.setHeightForWidth(self.rightButton.sizePolicy().hasHeightForWidth())
        self.rightButton.setSizePolicy(sizePolicy)

        self.navigationButtonLayout.addWidget(self.rightButton)


        self.verticalLayout.addLayout(self.navigationButtonLayout)

        self.okCancelbuttonBox = QDialogButtonBox(self.verticalLayoutWidget)
        self.okCancelbuttonBox.setObjectName(u"okCancelbuttonBox")
        self.okCancelbuttonBox.setOrientation(Qt.Horizontal)
        self.okCancelbuttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.okCancelbuttonBox)

        self.tableWidget = QTableWidget(CheckboxTrackListingDialog)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(30, 40, 860, 440))
        self.instructionsLabel = QLabel(CheckboxTrackListingDialog)
        self.instructionsLabel.setObjectName(u"instructionsLabel")
        self.instructionsLabel.setGeometry(QRect(60, 20, 821, 16))
        self.pageNumberLabel = QLabel(CheckboxTrackListingDialog)
        self.pageNumberLabel.setObjectName(u"pageNumberLabel")
        self.pageNumberLabel.setGeometry(QRect(420, 490, 131, 16))

        self.retranslateUi(CheckboxTrackListingDialog)
        self.okCancelbuttonBox.accepted.connect(CheckboxTrackListingDialog.accept)
        self.okCancelbuttonBox.rejected.connect(CheckboxTrackListingDialog.reject)

        QMetaObject.connectSlotsByName(CheckboxTrackListingDialog)
    # setupUi

    def retranslateUi(self, CheckboxTrackListingDialog):
        CheckboxTrackListingDialog.setWindowTitle(QCoreApplication.translate("CheckboxTrackListingDialog", u"Select Tracks to Remove", None))
        self.leftButton.setText(QCoreApplication.translate("CheckboxTrackListingDialog", u"\u2190", None))
        self.rightButton.setText(QCoreApplication.translate("CheckboxTrackListingDialog", u"\u2192", None))
        self.instructionsLabel.setText(QCoreApplication.translate("CheckboxTrackListingDialog", u"The following tracks are SIMILAR to each other by artist and title. Select the track(s) you want to remove:", None))
        self.pageNumberLabel.setText(QCoreApplication.translate("CheckboxTrackListingDialog", u"Page", None))
    # retranslateUi

