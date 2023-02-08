import shutil
from pathlib import Path

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
        self.fileNameField.textChanged.connect(self.enable_ok_button)

        self.browseButton.clicked.connect(self.choose_auth_file)

        self.auth_setup = YTAuthSetup(
            self.headersInputBox, self.fileNameField, self.parentWidget().credential_dir
        )
        self.auth_setup.auth_signal.connect(self.auth_finished)

        self.headersInputBox.setPlaceholderText(
            """
        Paste your raw request headers here and click OK.
        See https://ytmusicapi.readthedocs.io/en/latest/setup.html#copy-authentication-headers
        Alternatively, use Browse to select an existing headers_auth.json file.
        """
        )

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
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Auth File", QDir.rootPath(), "*.json"
        )
        self.fileNameField.setText(file_name)

    @Slot(str)
    def auth_finished(self, auth_result):
        if auth_result == "Success":
            self.parentWidget().is_authenticated()
            self.close()
        else:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText(auth_result)
            error_dialog.setInformativeText(
                "<html>See <a href=https://ytmusicapi.readthedocs.io/en/latest/setup.html#copy-authentication-headers>"
                "https://ytmusicapi.readthedocs.io/en/latest/setup.html#copy-authentication-headers</a> for "
                "instructions on obtaining your request headers.</html>"
            )
            error_dialog.setWindowTitle("Error")
            error_dialog.exec()


class YTAuthSetup(QObject):
    auth_signal = Signal(str)

    def __init__(self, textarea: QPlainTextEdit, filename_field: QLineEdit, cred_dir):
        super(YTAuthSetup, self).__init__()
        self.textarea = textarea
        self.filename_field = filename_field
        self.headers_file_path = Path(cred_dir) / constants.HEADERS_FILE

    @Slot()
    def setup_auth(self):
        try:
            # Use selected headers_auth.json file
            if self.filename_field.text():
                YTMusic(self.filename_field.text())
                from main import APP_DATA_DIR

                shutil.copy2(
                    self.filename_field.text(),
                    str(Path(APP_DATA_DIR) / "headers_auth.json"),
                )
            # Use pasted headers
            else:
                user_input = self.textarea.toPlainText()
                YTMusic(
                    YTMusic.setup(
                        filepath=self.headers_file_path, headers_raw=user_input
                    )
                )

            self.auth_signal.emit("Success")
        except Exception as e:
            self.auth_signal.emit(str(e))
