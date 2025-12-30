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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QButtonGroup, QCheckBox,
    QDialog, QDialogButtonBox, QLabel, QListWidget,
    QListWidgetItem, QRadioButton, QSizePolicy, QSpinBox,
    QToolButton, QWidget)

class Ui_PlaylistSelectionDialog(object):
    def setupUi(self, PlaylistSelectionDialog):
        if not PlaylistSelectionDialog.objectName():
            PlaylistSelectionDialog.setObjectName(u"PlaylistSelectionDialog")
        PlaylistSelectionDialog.setWindowModality(Qt.ApplicationModal)
        PlaylistSelectionDialog.resize(400, 353)
        self.buttonBox = QDialogButtonBox(PlaylistSelectionDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(50, 310, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.playlistList = QListWidget(PlaylistSelectionDialog)
        self.playlistList.setObjectName(u"playlistList")
        self.playlistList.setGeometry(QRect(25, 21, 351, 221))
        self.playlistList.setSelectionRectVisible(False)
        self.playlistList.setSortingEnabled(True)
        self.radioButtonLibrary = QRadioButton(PlaylistSelectionDialog)
        self.radioButtonGroup = QButtonGroup(PlaylistSelectionDialog)
        self.radioButtonGroup.setObjectName(u"radioButtonGroup")
        self.radioButtonGroup.addButton(self.radioButtonLibrary)
        self.radioButtonLibrary.setObjectName(u"radioButtonLibrary")
        self.radioButtonLibrary.setEnabled(True)
        self.radioButtonLibrary.setGeometry(QRect(50, 280, 82, 17))
        self.radioButtonUploads = QRadioButton(PlaylistSelectionDialog)
        self.radioButtonGroup.addButton(self.radioButtonUploads)
        self.radioButtonUploads.setObjectName(u"radioButtonUploads")
        self.radioButtonUploads.setEnabled(True)
        self.radioButtonUploads.setGeometry(QRect(120, 280, 82, 17))
        self.radioButtonUploads.setChecked(True)
        self.radioButtonLabel = QLabel(PlaylistSelectionDialog)
        self.radioButtonLabel.setObjectName(u"radioButtonLabel")
        self.radioButtonLabel.setEnabled(True)
        self.radioButtonLabel.setGeometry(QRect(55, 260, 111, 20))
        self.fuzzyCheckbox = QCheckBox(PlaylistSelectionDialog)
        self.fuzzyCheckbox.setObjectName(u"fuzzyCheckbox")
        self.fuzzyCheckbox.setGeometry(QRect(30, 260, 141, 21))
        self.scoreCutoffLabel = QLabel(PlaylistSelectionDialog)
        self.scoreCutoffLabel.setObjectName(u"scoreCutoffLabel")
        self.scoreCutoffLabel.setEnabled(False)
        self.scoreCutoffLabel.setGeometry(QRect(30, 290, 131, 21))
        self.scoreCutoffInput = QSpinBox(PlaylistSelectionDialog)
        self.scoreCutoffInput.setObjectName(u"scoreCutoffInput")
        self.scoreCutoffInput.setEnabled(False)
        self.scoreCutoffInput.setGeometry(QRect(160, 290, 42, 22))
        self.scoreCutoffInput.setMaximum(100)
        self.scoreCutoffInput.setValue(90)
        self.infoButton = QToolButton(PlaylistSelectionDialog)
        self.infoButton.setObjectName(u"infoButton")
        self.infoButton.setGeometry(QRect(170, 260, 24, 24))
        self.infoButton.setAutoRaise(True)

        self.retranslateUi(PlaylistSelectionDialog)
        self.buttonBox.accepted.connect(PlaylistSelectionDialog.accept)
        self.buttonBox.rejected.connect(PlaylistSelectionDialog.reject)

        QMetaObject.connectSlotsByName(PlaylistSelectionDialog)
    # setupUi

    def retranslateUi(self, PlaylistSelectionDialog):
        PlaylistSelectionDialog.setWindowTitle(QCoreApplication.translate("PlaylistSelectionDialog", u"Select Playlist(s)", None))
        self.radioButtonLibrary.setText(QCoreApplication.translate("PlaylistSelectionDialog", u"Library", None))
        self.radioButtonUploads.setText(QCoreApplication.translate("PlaylistSelectionDialog", u"Uploads", None))
        self.radioButtonLabel.setText(QCoreApplication.translate("PlaylistSelectionDialog", u"Add all songs from...", None))
        self.fuzzyCheckbox.setText(QCoreApplication.translate("PlaylistSelectionDialog", u"Use fuzzy matching", None))
        self.scoreCutoffLabel.setText(QCoreApplication.translate("PlaylistSelectionDialog", u"Match score cutoff:", None))
        self.infoButton.setText(QCoreApplication.translate("PlaylistSelectionDialog", u"...", None))
    # retranslateUi

