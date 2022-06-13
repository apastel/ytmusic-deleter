# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/main/resources/progress_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ProgressDialog(object):
    def setupUi(self, ProgressDialog):
        ProgressDialog.setObjectName("ProgressDialog")
        ProgressDialog.resize(473, 220)
        self.progressBar = QtWidgets.QProgressBar(ProgressDialog)
        self.progressBar.setGeometry(QtCore.QRect(100, 100, 291, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.pushButton = QtWidgets.QPushButton(ProgressDialog)
        self.pushButton.setGeometry(QtCore.QRect(200, 170, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.itemLine = QtWidgets.QLabel(ProgressDialog)
        self.itemLine.setGeometry(QtCore.QRect(50, 60, 371, 20))
        self.itemLine.setText("")
        self.itemLine.setAlignment(QtCore.Qt.AlignCenter)
        self.itemLine.setObjectName("itemLine")

        self.retranslateUi(ProgressDialog)
        QtCore.QMetaObject.connectSlotsByName(ProgressDialog)

    def retranslateUi(self, ProgressDialog):
        _translate = QtCore.QCoreApplication.translate
        ProgressDialog.setWindowTitle(_translate("ProgressDialog", "Progress"))
        self.pushButton.setText(_translate("ProgressDialog", "Abort"))

