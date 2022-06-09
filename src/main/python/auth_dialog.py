from pathlib import Path

from generated.ui_auth_dialog import Ui_AuthDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QDir
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDialogButtonBox
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from ytmusic_deleter import constants
from ytmusicapi import YTMusic


class AuthDialog(QDialog, Ui_AuthDialog):
    def __init__(self, parent):
        super(AuthDialog, self).__init__(parent)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True) # also closes parent window now for some reason
        self.setupUi(self)

        # Check again in case auth file was deleted/moved
        self.parentWidget().is_authenticated()

        self.enable_ok_button()
        self.headersInputBox.textChanged.connect(self.enable_ok_button)

        self.browseButton.clicked.connect(self.choose_auth_file)

        self.auth_setup = YTAuthSetup(
            self.headersInputBox, self.parentWidget().credential_dir
        )
        self.auth_setup.auth_signal.connect(self.auth_finished)

    def accept(self):
        self.thread = QThread(self)
        self.thread.started.connect(self.auth_setup.setup_auth)
        self.thread.start()

    @pyqtSlot()
    def enable_ok_button(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            self.headersInputBox.toPlainText() != ""
        )

    @pyqtSlot()
    def choose_auth_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Auth File", QDir.rootPath(), "*.json"
        )
        self.fileNameField.setText(file_name)

    @pyqtSlot(str)
    def auth_finished(self, auth_result):
        if auth_result == "Success":
            self.parentWidget().is_authenticated()
            self.close()
        else:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText(auth_result)
            error_dialog.setInformativeText(
                "See https://ytmusicapi.readthedocs.io/en/latest/setup.html#copy-authentication-headers"
            )
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()


class YTAuthSetup(QObject):
    auth_signal = pyqtSignal(str)

    def __init__(self, textarea, cred_dir):
        super(YTAuthSetup, self).__init__()
        self.textarea = textarea
        self.headers_file_path = Path(cred_dir) / constants.HEADERS_FILE

    @pyqtSlot()
    def setup_auth(self):
        user_input = self.textarea.toPlainText()
        try:
            YTMusic(
                YTMusic.setup(filepath=self.headers_file_path, headers_raw=user_input)
            )
            self.auth_signal.emit("Success")
        except Exception as e:
            self.auth_signal.emit(str(e))
