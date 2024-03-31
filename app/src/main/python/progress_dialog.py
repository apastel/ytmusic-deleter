from generated.ui_progress_dialog import Ui_ProgressDialog
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog


class ProgressDialog(QDialog, Ui_ProgressDialog):
    def __init__(self, parent):
        super().__init__(parent)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True) # also closes parent window now for some reason
        self.setupUi(self)

        self.abortButton.clicked.connect(self.abort)

    @Slot()
    def abort(self):
        self.parentWidget().message("Abort button clicked!")
        self.parentWidget().p.kill()
