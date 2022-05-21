from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QProcess
from ui_form import Ui_MainWindow
import sys


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.p = None
        self.removeLibraryButton.clicked.connect(self.remove_library)
        self.deleteUploadsButton.clicked.connect(self.delete_uploads)

    def launch_process(self, args):
        if self.p is None:
            self.message("Executing process.")
            self.p = QProcess()
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)
            self.p.start("ytmusic-deleter", args)

    def remove_library(self):
        self.launch_process(["remove-library"])
    
    def delete_uploads(self):
        self.launch_process(["delete-uploads"])

    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.message(stdout)

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    def process_finished(self):
        self.message("Process finished.")
        self.p = None

    def message(self, msg):
        self.consoleTextArea.appendPlainText(msg)
    
if __name__ == '__main__':
    appctxt = ApplicationContext()
    window = MainWindow()
    window.show()
    sys.exit(appctxt.app.exec_())
