# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'add_all_to_playlist_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
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
    QDialogButtonBox, QLabel, QRadioButton, QSizePolicy,
    QSpinBox, QToolButton, QWidget)

class Ui_AddAllSongsToPlaylistDialog(object):
    def setupUi(self, AddAllSongsToPlaylistDialog):
        if not AddAllSongsToPlaylistDialog.objectName():
            AddAllSongsToPlaylistDialog.setObjectName(u"AddAllSongsToPlaylistDialog")
        AddAllSongsToPlaylistDialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        AddAllSongsToPlaylistDialog.resize(400, 185)
        self.buttonBox = QDialogButtonBox(AddAllSongsToPlaylistDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(50, 140, 341, 32))
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)
        self.uploadsButton = QRadioButton(AddAllSongsToPlaylistDialog)
        self.radioButtonGroup = QButtonGroup(AddAllSongsToPlaylistDialog)
        self.radioButtonGroup.setObjectName(u"radioButtonGroup")
        self.radioButtonGroup.addButton(self.uploadsButton)
        self.uploadsButton.setObjectName(u"uploadsButton")
        self.uploadsButton.setEnabled(True)
        self.uploadsButton.setGeometry(QRect(40, 40, 91, 17))
        self.uploadsButton.setChecked(True)
        self.libraryButton = QRadioButton(AddAllSongsToPlaylistDialog)
        self.radioButtonGroup.addButton(self.libraryButton)
        self.libraryButton.setObjectName(u"libraryButton")
        self.libraryButton.setEnabled(True)
        self.libraryButton.setGeometry(QRect(140, 40, 101, 17))
        self.libraryButton.setChecked(False)
        self.radioButtonLabel = QLabel(AddAllSongsToPlaylistDialog)
        self.radioButtonLabel.setObjectName(u"radioButtonLabel")
        self.radioButtonLabel.setEnabled(True)
        self.radioButtonLabel.setGeometry(QRect(40, 20, 121, 20))
        self.infoButton = QToolButton(AddAllSongsToPlaylistDialog)
        self.infoButton.setObjectName(u"infoButton")
        self.infoButton.setGeometry(QRect(170, 20, 24, 24))
        self.infoButton.setAutoRaise(True)
        self.maxPlaylistSizeBox = QSpinBox(AddAllSongsToPlaylistDialog)
        self.maxPlaylistSizeBox.setObjectName(u"maxPlaylistSizeBox")
        self.maxPlaylistSizeBox.setGeometry(QRect(160, 80, 61, 23))
        self.maxPlaylistSizeBox.setMinimum(1)
        self.maxPlaylistSizeBox.setMaximum(5000)
        self.maxPlaylistSizeBox.setValue(5000)
        self.maxPlaylistSizeLabel = QLabel(AddAllSongsToPlaylistDialog)
        self.maxPlaylistSizeLabel.setObjectName(u"maxPlaylistSizeLabel")
        self.maxPlaylistSizeLabel.setGeometry(QRect(40, 70, 111, 41))

        self.retranslateUi(AddAllSongsToPlaylistDialog)
        self.buttonBox.accepted.connect(AddAllSongsToPlaylistDialog.accept)
        self.buttonBox.rejected.connect(AddAllSongsToPlaylistDialog.reject)

        QMetaObject.connectSlotsByName(AddAllSongsToPlaylistDialog)
    # setupUi

    def retranslateUi(self, AddAllSongsToPlaylistDialog):
        AddAllSongsToPlaylistDialog.setWindowTitle(QCoreApplication.translate("AddAllSongsToPlaylistDialog", u"Select Playlist(s)", None))
        self.uploadsButton.setText(QCoreApplication.translate("AddAllSongsToPlaylistDialog", u"Uploads", None))
        self.libraryButton.setText(QCoreApplication.translate("AddAllSongsToPlaylistDialog", u"Library", None))
        self.radioButtonLabel.setText(QCoreApplication.translate("AddAllSongsToPlaylistDialog", u"Add all songs from...", None))
        self.infoButton.setText(QCoreApplication.translate("AddAllSongsToPlaylistDialog", u"...", None))
        self.maxPlaylistSizeLabel.setText(QCoreApplication.translate("AddAllSongsToPlaylistDialog", u"Max Playlist Size:", None))
    # retranslateUi

