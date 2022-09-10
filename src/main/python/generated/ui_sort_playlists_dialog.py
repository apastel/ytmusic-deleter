# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sort_playlists_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QDialog,
    QDialogButtonBox, QListWidget, QListWidgetItem, QSizePolicy,
    QWidget)

class Ui_SortPlaylistsDialog(object):
    def setupUi(self, SortPlaylistsDialog):
        if not SortPlaylistsDialog.objectName():
            SortPlaylistsDialog.setObjectName(u"SortPlaylistsDialog")
        SortPlaylistsDialog.setWindowModality(Qt.ApplicationModal)
        SortPlaylistsDialog.resize(400, 300)
        self.buttonBox = QDialogButtonBox(SortPlaylistsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.playlistList = QListWidget(SortPlaylistsDialog)
        self.playlistList.setObjectName(u"playlistList")
        self.playlistList.setGeometry(QRect(70, 30, 256, 192))
        self.playlistList.setSelectionMode(QAbstractItemView.MultiSelection)
        self.playlistList.setSelectionRectVisible(False)
        self.playlistList.setSortingEnabled(True)

        self.retranslateUi(SortPlaylistsDialog)
        self.buttonBox.accepted.connect(SortPlaylistsDialog.accept)
        self.buttonBox.rejected.connect(SortPlaylistsDialog.reject)

        QMetaObject.connectSlotsByName(SortPlaylistsDialog)
    # setupUi

    def retranslateUi(self, SortPlaylistsDialog):
        SortPlaylistsDialog.setWindowTitle(QCoreApplication.translate("SortPlaylistsDialog", u"Sort Playlists", None))
    # retranslateUi

