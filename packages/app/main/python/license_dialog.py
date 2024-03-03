import sys
from pathlib import Path

from fbs_runtime import PUBLIC_SETTINGS
from fbs_runtime.licensing import InvalidKey
from fbs_runtime.licensing import unpack_license_key
from generated.ui_license_dialog import Ui_LicenseDialog
from PySide6.QtCore import QDir
from PySide6.QtCore import QObject
from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QLineEdit
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QPlainTextEdit


class LicenseDialog(QDialog, Ui_LicenseDialog):
    def __init__(self):
        super(LicenseDialog, self).__init__()
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True) # also closes parent window now for some reason
        self.setupUi(self)

        self.browseButton.clicked.connect(self.choose_license_file)
        self.submitButton.clicked.connect(self.submit_clicked)

        self.license_check = LicenseCheck(self.licenseInputBox, self.fileNameField)
        self.license_check.check_signal.connect(self.check_finished)

    @Slot()
    def submit_clicked(self):
        self.thread = QThread(self)
        self.thread.started.connect(self.license_check.license_key_is_valid)
        self.thread.start()

    @Slot()
    def reject(self):
        self.close()
        sys.exit()

    @Slot()
    def choose_license_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select License File", QDir.rootPath()
        )
        self.fileNameField.setText(file_name)

    @Slot(str)
    def check_finished(self, check_result):
        if check_result == "VALID":
            self.accept()
        else:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText(check_result)
            error_dialog.setInformativeText(
                "Visit ytmusicdeleter.com to purchase a license."
            )
            error_dialog.setWindowTitle("Error")
            error_dialog.exec()


class LicenseCheck(QObject):
    check_signal = Signal(str)

    def __init__(self, textarea: QPlainTextEdit, filename_field: QLineEdit) -> None:
        super(LicenseCheck, self).__init__()
        self.textarea = textarea
        self.filename_field = filename_field

    def get_license_key(self):
        if self.filename_field.text():
            with open(self.filename_field.text()) as f:
                key_contents = f.read()
        else:
            key_contents = self.textarea.toPlainText()
        unpack_license_key(key_contents, PUBLIC_SETTINGS["licensing_pubkey"])
        return key_contents

    @Slot()
    def license_key_is_valid(self):
        try:
            license_key = self.get_license_key()
        except FileNotFoundError:
            self.check_signal.emit("The file was not found.")
        except InvalidKey:
            self.check_signal.emit("The key was invalid.")
        else:
            self.check_signal.emit("VALID")
            from main import APP_DATA_DIR

            with open(Path(APP_DATA_DIR) / "license_key.txt", "w") as f:
                f.write(license_key)
