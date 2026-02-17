# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sort_playlist_dialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QCheckBox,
    QDialog, QDialogButtonBox, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QSizePolicy, QWidget)

class Ui_SortPlaylistDialog(object):
    def setupUi(self, SortPlaylistDialog):
        if not SortPlaylistDialog.objectName():
            SortPlaylistDialog.setObjectName(u"SortPlaylistDialog")
        SortPlaylistDialog.setWindowModality(Qt.ApplicationModal)
        SortPlaylistDialog.resize(840, 528)
        self.buttonBox = QDialogButtonBox(SortPlaylistDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(460, 480, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.playlistList = QListWidget(SortPlaylistDialog)
        self.playlistList.setObjectName(u"playlistList")
        self.playlistList.setGeometry(QRect(30, 40, 781, 221))
        self.playlistList.setSelectionRectVisible(False)
        self.playlistList.setSortingEnabled(True)
        self.shuffleCheckBox = QCheckBox(SortPlaylistDialog)
        self.shuffleCheckBox.setObjectName(u"shuffleCheckBox")
        self.shuffleCheckBox.setGeometry(QRect(110, 480, 70, 17))
        self.availableAttributesListWidget = QListWidget(SortPlaylistDialog)
        self.availableAttributesListWidget.setObjectName(u"availableAttributesListWidget")
        self.availableAttributesListWidget.setGeometry(QRect(100, 310, 256, 131))
        self.selectedAttributesListWidget = QListWidget(SortPlaylistDialog)
        self.selectedAttributesListWidget.setObjectName(u"selectedAttributesListWidget")
        self.selectedAttributesListWidget.setGeometry(QRect(500, 310, 256, 131))
        self.selectedAttributesListWidget.setDragEnabled(True)
        self.selectedAttributesListWidget.setDragDropMode(QAbstractItemView.InternalMove)
        self.addButton = QPushButton(SortPlaylistDialog)
        self.addButton.setObjectName(u"addButton")
        self.addButton.setGeometry(QRect(390, 340, 75, 23))
        self.removeButton = QPushButton(SortPlaylistDialog)
        self.removeButton.setObjectName(u"removeButton")
        self.removeButton.setGeometry(QRect(390, 410, 75, 23))
        self.reverseCheckbox = QCheckBox(SortPlaylistDialog)
        self.reverseCheckbox.setObjectName(u"reverseCheckbox")
        self.reverseCheckbox.setGeometry(QRect(210, 480, 81, 17))
        self.label = QLabel(SortPlaylistDialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(30, 10, 751, 31))
        self.label_2 = QLabel(SortPlaylistDialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(100, 275, 231, 31))
        self.label_3 = QLabel(SortPlaylistDialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(500, 275, 311, 31))

        self.retranslateUi(SortPlaylistDialog)
        self.buttonBox.accepted.connect(SortPlaylistDialog.accept)
        self.buttonBox.rejected.connect(SortPlaylistDialog.reject)

        QMetaObject.connectSlotsByName(SortPlaylistDialog)
    # setupUi

    def retranslateUi(self, SortPlaylistDialog):
        SortPlaylistDialog.setWindowTitle(QCoreApplication.translate("SortPlaylistDialog", u"Select Playlist(s)", None))
#if QT_CONFIG(tooltip)
        self.shuffleCheckBox.setToolTip(QCoreApplication.translate("SortPlaylistDialog", u"Shuffle the playlist(s) instead of sorting.", None))
#endif // QT_CONFIG(tooltip)
        self.shuffleCheckBox.setText(QCoreApplication.translate("SortPlaylistDialog", u"Shuffle", None))
#if QT_CONFIG(tooltip)
        self.selectedAttributesListWidget.setToolTip(QCoreApplication.translate("SortPlaylistDialog", u"Rearrange the order of this list to change the sorting priority", None))
#endif // QT_CONFIG(tooltip)
        self.addButton.setText(QCoreApplication.translate("SortPlaylistDialog", u"->", None))
        self.removeButton.setText(QCoreApplication.translate("SortPlaylistDialog", u"<-", None))
#if QT_CONFIG(tooltip)
        self.reverseCheckbox.setToolTip(QCoreApplication.translate("SortPlaylistDialog", u"Reverse the sort order", None))
#endif // QT_CONFIG(tooltip)
        self.reverseCheckbox.setText(QCoreApplication.translate("SortPlaylistDialog", u"Reverse", None))
        self.label.setText(QCoreApplication.translate("SortPlaylistDialog", u"Select one or more playlists to sort:", None))
        self.label_2.setText(QCoreApplication.translate("SortPlaylistDialog", u"Sortable attributes", None))
        self.label_3.setText(QCoreApplication.translate("SortPlaylistDialog", u"Selected attributes (drag to rearrange)", None))
    # retranslateUi

