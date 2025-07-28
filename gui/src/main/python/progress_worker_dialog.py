from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QProgressDialog


class ProgressWorkerDialog(QProgressDialog):
    def __init__(self, message: str, parent=None, maximum=0):
        super().__init__(f"{message}...", None, 0, maximum, parent)
        self.setWindowTitle("Please wait")
        self.setWindowModality(Qt.WindowModal)
        self.setCancelButton(None)
        self.setValue(0)
        self.setMinimumWidth(350)

    def set_progress(self, value, message=None):
        if message:
            self.setLabelText(message)
        self.setValue(value)
        QApplication.processEvents()  # Ensure UI updates

    def run(self, work_fn, on_done=None):
        """
        Show the dialog and run work_fn after a short delay, then auto-close.
        If on_done is provided, it will be called with the result or exception.
        """

        def wrapped_work():
            try:
                result = work_fn()
                if on_done:
                    on_done(result)
            except Exception as e:
                if on_done:
                    on_done(e)
            finally:
                self.close()

        self.show()
        QTimer.singleShot(100, wrapped_work)
