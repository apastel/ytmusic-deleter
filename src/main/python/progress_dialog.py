from generated.ui_progress_dialog import Ui_ProgressDialog
from PySide6.QtWidgets import QDialog


class ProgressDialog(QDialog, Ui_ProgressDialog):
    def __init__(self, parent):
        super(ProgressDialog, self).__init__(parent)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True) # also closes parent window now for some reason
        self.setupUi(self)
