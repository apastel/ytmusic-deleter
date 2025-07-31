import shutil
from pathlib import Path

import ytmusicapi
from generated.ui_auth_dialog import Ui_AuthDialog
from PySide6.QtCore import QDir
from PySide6.QtCore import QObject
from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QDialogButtonBox
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPlainTextEdit
from ytmusic_deleter import common
from ytmusicapi import YTMusic


class BrowserAuthDialog(QDialog, Ui_AuthDialog):
    def __init__(self, parent):
        super().__init__(parent)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True) # also closes parent window now for some reason
        self.setupUi(self)

        # Check again in case auth file was deleted/moved
        self.parentWidget().is_signed_in()

        self.enable_ok_button()
        self.headersInputBox.textChanged.connect(self.enable_ok_button)
        self.fileNameField.textChanged.connect(self.enable_ok_button)

        self.browseButton.clicked.connect(self.choose_auth_file)

        self.auth_setup = YTAuthSetup(self.headersInputBox, self.fileNameField, self.parentWidget().credential_dir)
        self.auth_setup.auth_signal.connect(self.auth_finished)

        self.headersInputBox.setPlaceholderText(
            """

            Paste your raw request headers here and click OK.
            See the links below for instructions.
            Or use Browse to select an existing browser.json file.
            """
        )
        self.instructions_str = (
            "<html>See the <a href=https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html#copy-authentication-headers>"
            "ytmusicapi docs</a> or this <a href=https://youtu.be/FZ7gaMTUYN4>YouTube video</a> for instructions on "
            "obtaining your request headers. You must use Firefox since Chrome/Edge are currently experiencing an issue.</html>"
        )
        self.helpLabel.setText(self.instructions_str)

    def accept(self):
        self.thread = QThread(self)
        self.thread.started.connect(self.auth_setup.setup_auth)
        self.thread.start()

    @Slot()
    def enable_ok_button(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(
            self.headersInputBox.toPlainText() != "" or self.fileNameField.text() != ""
        )

    @Slot()
    def choose_auth_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Auth File", QDir.rootPath(), "*.json")
        self.fileNameField.setText(file_name)

    @Slot(str)
    def auth_finished(self, auth_result):
        if auth_result == "Success":
            self.parentWidget().update_buttons()
            self.close()
        else:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText(auth_result)
            error_dialog.setInformativeText(self.instructions_str)
            error_dialog.setWindowTitle("Error")
            error_dialog.exec()


class YTAuthSetup(QObject):
    auth_signal = Signal(str)

    def __init__(self, textarea: QPlainTextEdit, filename_field: QLineEdit, cred_dir):
        super().__init__()
        self.textarea = textarea
        self.filename_field = filename_field
        self.browser_file_path = Path(cred_dir) / common.BROWSER_FILENAME

    @Slot()
    def setup_auth(self):
        try:
            # Use selected headers_auth.json file
            if self.filename_field.text():
                YTMusic(self.filename_field.text())
                shutil.copy2(self.filename_field.text(), self.browser_file_path)
            # Use pasted headers
            else:
                user_input = self.textarea.toPlainText()
                YTMusic(ytmusicapi.setup(filepath=self.browser_file_path, headers_raw=user_input))

            self.auth_signal.emit("Success")
        except Exception as e:
            self.auth_signal.emit(str(e))
