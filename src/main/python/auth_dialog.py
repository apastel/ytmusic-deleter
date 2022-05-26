# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/main/resources/auth_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(573, 438)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(10, 360, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.headersInputBox = QtWidgets.QPlainTextEdit(Dialog)
        self.headersInputBox.setGeometry(QtCore.QRect(60, 20, 451, 251))
        self.headersInputBox.setObjectName("headersInputBox")
        self.orLabel = QtWidgets.QLabel(Dialog)
        self.orLabel.setGeometry(QtCore.QRect(260, 280, 47, 13))
        self.orLabel.setObjectName("orLabel")
        self.browseButton = QtWidgets.QPushButton(Dialog)
        self.browseButton.setGeometry(QtCore.QRect(230, 310, 75, 23))
        self.browseButton.setObjectName("browseButton")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Authentication"))
        self.orLabel.setText(_translate("Dialog", "Or"))
        self.browseButton.setText(_translate("Dialog", "Browse"))

