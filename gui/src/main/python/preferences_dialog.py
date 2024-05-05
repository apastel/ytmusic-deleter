from generated.ui_preferences_dialog import Ui_PreferencesDialog
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog


class PreferencesDialog(QDialog, Ui_PreferencesDialog):
    save_settings_signal = Signal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.verboseCheckBox.setChecked(parent.settings.value("verbose_logging", False, type=bool))

    def accept(self) -> None:
        self.save_settings_signal.emit(True)
        super().accept()

    def reject(self) -> None:
        super().reject()
