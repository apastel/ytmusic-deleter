import os
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtCore import QProcess, QSettings
from main_window import Ui_MainWindow
from auth_dialog import Ui_Dialog
import sys
from pathlib import Path
from ytmusicapi import YTMusic
from ytmusic_deleter import constants

DEFAULT_LOG_DIR = os.path.join(os.getenv('APPDATA'), "YTMusic Deleter")

class AuthDialog(QDialog, Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("apastel", "YTMusic Deleter")
        try:
            self.resize(self.settings.value("mainwindow/size"))
            self.move(self.settings.value("mainwindow/pos"))
        except Exception:
            pass
        self.log_dir = self.settings.value("log_dir", DEFAULT_LOG_DIR)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)

        self.setupUi(self)
        self.p = None
        self.removeLibraryButton.clicked.connect(self.remove_library)
        self.deleteUploadsButton.clicked.connect(self.delete_uploads)
        self.authIndicator.clicked.connect(self.ensure_auth)
        self.auth_dialog = AuthDialog()
        self.authorized = self.check_auth()

    def check_auth(self):
        try:
            YTMusic(constants.HEADERS_FILE)
        except (KeyError, AttributeError):
            self.message("Not authorized yet")


    def ensure_auth(self):
        self.message("prompting for auth...")
        self.auth_dialog.show()


    def launch_process(self, args):
        if self.p is None:
            self.ensure_auth()
            self.message(f"Executing process: {args}")
            self.p = QProcess()
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)
            self.p.start("cli.exe", ["-l", self.log_dir] + args)
            if not self.p.waitForStarted():
                self.message(self.p.errorString())


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
