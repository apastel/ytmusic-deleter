import logging
import os
import re
import sys
from pathlib import Path

from auth_dialog import AuthDialog
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from generated.ui_main_window import Ui_MainWindow
from progress_dialog import ProgressDialog
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QProcess
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMainWindow
from ytmusic_deleter import constants
from ytmusicapi import YTMusic

APP_DATA_DIR = str(Path(os.getenv("APPDATA")) / "YTMusic Deleter")
progress_re = re.compile("Total complete: (\\d+)%")
item_processing_re = re.compile("(Processing \\w+: .+)")
cli_filename = "ytmusic-deleter-1.4.1.exe"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(Path(APP_DATA_DIR) / "ytmusic-deleter-packager.log"),
        logging.StreamHandler(sys.stdout),
    ],
)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.settings = QSettings("apastel", "YTMusic Deleter")
        try:
            self.resize(self.settings.value("mainwindow/size"))
            self.move(self.settings.value("mainwindow/pos"))
        except Exception:
            pass
        self.log_dir = self.settings.value("log_dir", APP_DATA_DIR)
        self.credential_dir = self.settings.value("credential_dir", APP_DATA_DIR)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        Path(self.credential_dir).mkdir(parents=True, exist_ok=True)

        self.setupUi(self)
        self.p = None
        self.removeLibraryButton.clicked.connect(self.remove_library)
        self.deleteUploadsButton.clicked.connect(self.delete_uploads)
        self.authIndicator.clicked.connect(self.prompt_for_auth)
        self.is_authenticated()

    def is_authenticated(self, prompt=False):
        try:
            YTMusic(Path(self.credential_dir) / constants.HEADERS_FILE)
            self.authIndicator.setText("Authenticated")
            return True
        except (KeyError, AttributeError):
            self.message("Not authorized yet")
            self.authIndicator.setText("Unauthenticated")
            if prompt:
                self.prompt_for_auth()
            return False

    @pyqtSlot()
    def prompt_for_auth(self):
        self.auth_dialog = AuthDialog(self)
        self.message("prompting for auth...")
        self.auth_dialog.show()

    @pyqtSlot()
    def remove_library(self):
        self.launch_process(["remove-library"])

    @pyqtSlot()
    def delete_uploads(self):
        self.launch_process(["delete-uploads"])

    def launch_process(self, args):
        if self.p is None and self.is_authenticated(prompt=True):
            self.message(f"Executing process: {args}")
            self.p = QProcess()
            self.p.readyReadStandardOutput.connect(self.handle_stdout)
            self.p.readyReadStandardError.connect(self.handle_stderr)
            self.p.stateChanged.connect(self.handle_state)
            self.p.finished.connect(self.process_finished)
            self.p.start(
                cli_filename,
                ["-l", self.log_dir, "-c", self.credential_dir, "-p"] + args,
            )
            self.progress_dialog = ProgressDialog(self)
            self.progress_dialog.show()
            if not self.p.waitForStarted():
                self.message(self.p.errorString())

    @pyqtSlot()
    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    @pyqtSlot()
    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        percent_complete = self.get_percent_complete(stdout)
        if percent_complete:
            self.progress_dialog.progressBar.setValue(percent_complete)
        item_processing = self.get_item_processing(stdout)
        if item_processing:
            self.progress_dialog.itemLine.setText(item_processing)
        self.message(stdout)

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: "Not running",
            QProcess.Starting: "Starting",
            QProcess.Running: "Running",
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    @pyqtSlot()
    def process_finished(self):
        self.progress_dialog.close()
        self.message("Process finished.")
        self.p = None

    def message(self, msg):
        msg = msg.rstrip()  # Remove extra newlines
        self.consoleTextArea.appendPlainText(msg)
        logging.info(msg)

    def get_percent_complete(self, output):
        """
        Matches lines using the progress_re regex,
        returning a single integer for the % progress.
        """
        m = progress_re.search(output)
        if m:
            percent_complete = m.group(1)
            return int(percent_complete)

    def get_item_processing(self, output):
        m = item_processing_re.search(output)
        if m:
            return m.group(1)


if __name__ == "__main__":
    appctxt = ApplicationContext()
    window = MainWindow()
    window.show()
    sys.exit(appctxt.app.exec_())
