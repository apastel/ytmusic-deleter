# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/main/resources/auth_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AuthDialog(object):
    def setupUi(self, AuthDialog):
        AuthDialog.setObjectName("AuthDialog")
        AuthDialog.resize(569, 438)
        self.buttonBox = QtWidgets.QDialogButtonBox(AuthDialog)
        self.buttonBox.setEnabled(True)
        self.buttonBox.setGeometry(QtCore.QRect(200, 360, 171, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.headersInputBox = QtWidgets.QPlainTextEdit(AuthDialog)
        self.headersInputBox.setGeometry(QtCore.QRect(60, 20, 451, 251))
        self.headersInputBox.setObjectName("headersInputBox")
        self.orLabel = QtWidgets.QLabel(AuthDialog)
        self.orLabel.setGeometry(QtCore.QRect(280, 280, 21, 16))
        self.orLabel.setObjectName("orLabel")
        self.browseButton = QtWidgets.QPushButton(AuthDialog)
        self.browseButton.setGeometry(QtCore.QRect(140, 300, 75, 23))
        self.browseButton.setObjectName("browseButton")
        self.fileNameField = QtWidgets.QLineEdit(AuthDialog)
        self.fileNameField.setEnabled(False)
        self.fileNameField.setGeometry(QtCore.QRect(230, 300, 241, 21))
        self.fileNameField.setObjectName("fileNameField")

        self.retranslateUi(AuthDialog)
        self.buttonBox.accepted.connect(AuthDialog.accept)
        self.buttonBox.rejected.connect(AuthDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AuthDialog)

    def retranslateUi(self, AuthDialog):
        _translate = QtCore.QCoreApplication.translate
        AuthDialog.setWindowTitle(_translate("AuthDialog", "Authentication"))
        self.orLabel.setText(_translate("AuthDialog", "Or"))
        self.browseButton.setText(_translate("AuthDialog", "Browse"))

