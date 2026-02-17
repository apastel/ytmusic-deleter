# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'track_listing.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QHeaderView, QLabel, QSizePolicy,
    QTableWidget, QTableWidgetItem, QWidget)

class Ui_TrackListingDialog(object):
    def setupUi(self, TrackListingDialog):
        if not TrackListingDialog.objectName():
            TrackListingDialog.setObjectName(u"TrackListingDialog")
        TrackListingDialog.resize(924, 622)
        self.buttonBox = QDialogButtonBox(TrackListingDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(370, 560, 161, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.trackListTable = QTableWidget(TrackListingDialog)
        self.trackListTable.setObjectName(u"trackListTable")
        self.trackListTable.setGeometry(QRect(30, 70, 860, 440))
        self.trackListTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.trackListTable.setColumnCount(0)
        self.descriptionLabel = QLabel(TrackListingDialog)
        self.descriptionLabel.setObjectName(u"descriptionLabel")
        self.descriptionLabel.setGeometry(QRect(30, 0, 851, 61))

        self.retranslateUi(TrackListingDialog)
        self.buttonBox.accepted.connect(TrackListingDialog.accept)
        self.buttonBox.rejected.connect(TrackListingDialog.reject)

        QMetaObject.connectSlotsByName(TrackListingDialog)
    # setupUi

    def retranslateUi(self, TrackListingDialog):
        TrackListingDialog.setWindowTitle(QCoreApplication.translate("TrackListingDialog", u"Remove Exact Duplicates", None))
        self.descriptionLabel.setText(QCoreApplication.translate("TrackListingDialog", u"The following tracks will be removed because they are exact duplicates of another track in the playlist:", None))
    # retranslateUi

