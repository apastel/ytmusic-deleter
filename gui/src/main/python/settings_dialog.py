import os
import subprocess

import fbs_runtime.platform
from generated.ui_settings_dialog import Ui_SettingsDialog
from PySide6.QtCore import Signal
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog

import common


class SettingsDialog(QDialog, Ui_SettingsDialog):
    save_settings_signal = Signal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.verboseCheckBox.setChecked(parent.settings.value("verbose_logging", False, type=bool))
        self.oauthCheckbox.setChecked(parent.settings.value("oauth_enabled", False, type=bool))
        self.oauthCheckbox.checkStateChanged.connect(self.oauth_check_state_changed)
        self.oauth_check_state_changed()
        self.dataDirPathDisplay.setText(str(common.APP_DATA_PATH))
        self.openDataDirButton.clicked.connect(self.open_data_dir)

    def accept(self) -> None:
        self.save_settings_signal.emit(True)
        super().accept()

    def reject(self) -> None:
        super().reject()
        self.close()
        self.deleteLater()

    @Slot()
    def open_data_dir(self) -> None:
        path = str(common.APP_DATA_PATH)
        open_file_browser(path)

    @Slot()
    def oauth_check_state_changed(self) -> None:
        self.clientIdInput.setVisible(self.oauthCheckbox.isChecked())
        self.clientSecretInput.setVisible(self.oauthCheckbox.isChecked())


def open_file_browser(path: str) -> None:
    if fbs_runtime.platform.is_windows():
        os.startfile(path)
    elif fbs_runtime.platform.is_mac():
        subprocess.Popen(["open", path])
    elif fbs_runtime.platform.is_linux():
        subprocess.Popen(["xdg-open", path])
