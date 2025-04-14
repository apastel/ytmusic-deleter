# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'delete_uploads_dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
    QWidget)

class Ui_DeleteUploadsDialog(object):
    def setupUi(self, DeleteUploadsDialog):
        if not DeleteUploadsDialog.objectName():
            DeleteUploadsDialog.setObjectName(u"DeleteUploadsDialog")
        DeleteUploadsDialog.resize(393, 215)
        self.buttonBox = QDialogButtonBox(DeleteUploadsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setGeometry(QRect(30, 160, 341, 32))
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.infoLabel = QLabel(DeleteUploadsDialog)
        self.infoLabel.setObjectName(u"infoLabel")
        self.infoLabel.setGeometry(QRect(40, 20, 281, 31))
        self.addUploadsCheckBox = QCheckBox(DeleteUploadsDialog)
        self.addUploadsCheckBox.setObjectName(u"addUploadsCheckBox")
        self.addUploadsCheckBox.setGeometry(QRect(40, 80, 261, 16))
        self.scoreCutoffLabel = QLabel(DeleteUploadsDialog)
        self.scoreCutoffLabel.setObjectName(u"scoreCutoffLabel")
        self.scoreCutoffLabel.setGeometry(QRect(40, 100, 131, 21))
        self.scoreCutoffInput = QSpinBox(DeleteUploadsDialog)
        self.scoreCutoffInput.setObjectName(u"scoreCutoffInput")
        self.scoreCutoffInput.setGeometry(QRect(170, 100, 42, 22))
        self.scoreCutoffInput.setMaximum(100)
        self.scoreCutoffInput.setValue(85)
        self.hoverOverLabel = QLabel(DeleteUploadsDialog)
        self.hoverOverLabel.setObjectName(u"hoverOverLabel")
        self.hoverOverLabel.setGeometry(QRect(60, 120, 261, 20))
        font = QFont()
        font.setPointSize(7)
        self.hoverOverLabel.setFont(font)

        self.retranslateUi(DeleteUploadsDialog)
        self.buttonBox.accepted.connect(DeleteUploadsDialog.accept)
        self.buttonBox.rejected.connect(DeleteUploadsDialog.reject)

        QMetaObject.connectSlotsByName(DeleteUploadsDialog)
    # setupUi

    def retranslateUi(self, DeleteUploadsDialog):
        DeleteUploadsDialog.setWindowTitle(QCoreApplication.translate("DeleteUploadsDialog", u"Dialog", None))
        self.infoLabel.setText(QCoreApplication.translate("DeleteUploadsDialog", u"This will delete all your uploaded music.", None))
#if QT_CONFIG(tooltip)
        self.addUploadsCheckBox.setToolTip(QCoreApplication.translate("DeleteUploadsDialog", u"This will attempt to add each album or song to your library from YouTube Music's online catalog before deleting it from your uploads. If a match could not be found, the album or song will remain in your uploads.", None))
#endif // QT_CONFIG(tooltip)
        self.addUploadsCheckBox.setText(QCoreApplication.translate("DeleteUploadsDialog", u"Add uploads to library first", None))
#if QT_CONFIG(tooltip)
        self.scoreCutoffLabel.setToolTip(QCoreApplication.translate("DeleteUploadsDialog", u"A value closer to 100 will be more strict regarding matches when searching YTMusic for the song/album. A value of 100 will basically only add exact matches. If you find that not many matches are being found, try lowering this value, but you may end up with albums in your library that are not exact matches. 85 is recommended to start out with.", None))
#endif // QT_CONFIG(tooltip)
        self.scoreCutoffLabel.setText(QCoreApplication.translate("DeleteUploadsDialog", u"Match score cutoff:", None))
#if QT_CONFIG(tooltip)
        self.scoreCutoffInput.setToolTip(QCoreApplication.translate("DeleteUploadsDialog", u"A value closer to 100 will be more strict regarding matches when searching YTMusic for the song/album. A value of 100 will basically only add exact matches. If you find that not many matches are being found, try lowering this value, but you may end up with albums in your library that are not exact matches. 85 is recommended to start out with.", None))
#endif // QT_CONFIG(tooltip)
        self.hoverOverLabel.setText(QCoreApplication.translate("DeleteUploadsDialog", u"(Hover over these options for more info)", None))
    # retranslateUi

