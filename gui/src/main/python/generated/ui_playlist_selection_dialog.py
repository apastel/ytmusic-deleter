# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'playlist_selection_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QButtonGroup, QDialog,
    QDialogButtonBox, QLabel, QListWidget, QListWidgetItem,
    QRadioButton, QSizePolicy, QSpinBox, QToolButton,
    QWidget)

class Ui_PlaylistSelectionDialog(object):
    def setupUi(self, PlaylistSelectionDialog):
        if not PlaylistSelectionDialog.objectName():
            PlaylistSelectionDialog.setObjectName(u"PlaylistSelectionDialog")
        PlaylistSelectionDialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        PlaylistSelectionDialog.resize(400, 353)
        self.buttonBox = QDialogButtonBox(PlaylistSelectionDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(50, 310, 341, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.playlistList = QListWidget(PlaylistSelectionDialog)
        self.playlistList.setObjectName(u"playlistList")
        self.playlistList.setGeometry(QRect(25, 21, 351, 221))
        self.playlistList.setSelectionRectVisible(False)
        self.playlistList.setSortingEnabled(True)
        self.radioButtonA = QRadioButton(PlaylistSelectionDialog)
        self.radioButtonGroup = QButtonGroup(PlaylistSelectionDialog)
        self.radioButtonGroup.setObjectName(u"radioButtonGroup")
        self.radioButtonGroup.addButton(self.radioButtonA)
        self.radioButtonA.setObjectName(u"radioButtonA")
        self.radioButtonA.setEnabled(True)
        self.radioButtonA.setGeometry(QRect(50, 280, 91, 17))
        self.radioButtonA.setChecked(True)
        self.radioButtonB = QRadioButton(PlaylistSelectionDialog)
        self.radioButtonGroup.addButton(self.radioButtonB)
        self.radioButtonB.setObjectName(u"radioButtonB")
        self.radioButtonB.setEnabled(True)
        self.radioButtonB.setGeometry(QRect(150, 280, 101, 17))
        self.radioButtonB.setChecked(False)
        self.radioButtonLabel = QLabel(PlaylistSelectionDialog)
        self.radioButtonLabel.setObjectName(u"radioButtonLabel")
        self.radioButtonLabel.setEnabled(True)
        self.radioButtonLabel.setGeometry(QRect(50, 260, 121, 20))
        self.scoreCutoffLabel = QLabel(PlaylistSelectionDialog)
        self.scoreCutoffLabel.setObjectName(u"scoreCutoffLabel")
        self.scoreCutoffLabel.setEnabled(False)
        self.scoreCutoffLabel.setGeometry(QRect(50, 300, 131, 21))
        self.scoreCutoffInput = QSpinBox(PlaylistSelectionDialog)
        self.scoreCutoffInput.setObjectName(u"scoreCutoffInput")
        self.scoreCutoffInput.setEnabled(False)
        self.scoreCutoffInput.setGeometry(QRect(180, 300, 42, 22))
        self.scoreCutoffInput.setMaximum(100)
        self.scoreCutoffInput.setValue(90)
        self.infoButton = QToolButton(PlaylistSelectionDialog)
        self.infoButton.setObjectName(u"infoButton")
        self.infoButton.setGeometry(QRect(180, 260, 24, 24))
        self.infoButton.setAutoRaise(True)

        self.retranslateUi(PlaylistSelectionDialog)
        self.buttonBox.accepted.connect(PlaylistSelectionDialog.accept)
        self.buttonBox.rejected.connect(PlaylistSelectionDialog.reject)

        QMetaObject.connectSlotsByName(PlaylistSelectionDialog)
    # setupUi

    def retranslateUi(self, PlaylistSelectionDialog):
        PlaylistSelectionDialog.setWindowTitle(QCoreApplication.translate("PlaylistSelectionDialog", u"Select Playlist(s)", None))
        self.radioButtonA.setText(QCoreApplication.translate("PlaylistSelectionDialog", u"Option A", None))
        self.radioButtonB.setText(QCoreApplication.translate("PlaylistSelectionDialog", u"Option B", None))
        self.radioButtonLabel.setText(QCoreApplication.translate("PlaylistSelectionDialog", u"Radio Button Label", None))
        self.scoreCutoffLabel.setText(QCoreApplication.translate("PlaylistSelectionDialog", u"Match score cutoff:", None))
        self.infoButton.setText(QCoreApplication.translate("PlaylistSelectionDialog", u"...", None))
    # retranslateUi

