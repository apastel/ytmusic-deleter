from generated import ui_delete_uploads_dialog
from PySide6 import QtCore
from PySide6 import QtWidgets


class DeleteUploadsDialog(QtWidgets.QDialog, ui_delete_uploads_dialog.Ui_DeleteUploadsDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.enable_score_cutoff()
        self.addUploadsCheckBox.checkStateChanged.connect(self.enable_score_cutoff)

    def accept(self):
        delete_uploads_args = ["delete-uploads"]
        if self.addUploadsCheckBox.isChecked():
            delete_uploads_args += ["-as", str(self.scoreCutoffInput.value())]
        self.parentWidget().launch_process(delete_uploads_args)
        super().accept()

    @QtCore.Slot()
    def enable_score_cutoff(self):
        self.scoreCutoffInput.setValue(85)
        self.scoreCutoffLabel.setVisible(self.addUploadsCheckBox.isChecked())
        self.scoreCutoffInput.setVisible(self.addUploadsCheckBox.isChecked())
