import os
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox
from PyQt5.QtCore import QProcess, QSettings, pyqtSlot, pyqtSignal, QObject, QThread
from PyQt5 import QtCore
from main_window import Ui_MainWindow
from auth_dialog import Ui_Dialog
import sys
from pathlib import Path
from ytmusicapi import YTMusic
from ytmusic_deleter import constants
import logging

APP_DATA_DIR = Path(os.getenv('APPDATA')) / "YTMusic Deleter"
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(Path(APP_DATA_DIR) / "ytmusic-deleter-packager.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

class YTAuthSetup(QObject):
    auth_signal = pyqtSignal(str)

    def __init__(self, textarea, cred_dir):
        super(YTAuthSetup, self).__init__()
        self.textarea = textarea
        self.headers_file_path = Path(cred_dir) / constants.HEADERS_FILE

    @pyqtSlot()
    def setup_auth(self):
        user_input = self.textarea.toPlainText()
        try:
            YTMusic(YTMusic.setup(filepath=self.headers_file_path, headers_raw=user_input))
            self.auth_signal.emit("Success")
        except Exception as e:
            self.auth_signal.emit(str(e))


class AuthDialog(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super(AuthDialog, self).__init__(parent)
        # self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True) also closes parent window now for some reason
        self.setupUi(self)
        
        # Check again in case auth file was deleted/moved
        self.parentWidget().is_authenticated()

        self.auth_setup = YTAuthSetup(self.headersInputBox, self.parentWidget().credential_dir)
        self.auth_setup.auth_signal.connect(self.auth_finished)

    def accept(self):
        self.thread = QThread(self)
        self.thread.started.connect(self.auth_setup.setup_auth)
        self.thread.start()

    @pyqtSlot(str)
    def auth_finished(self, auth_result):
        if auth_result == "Success":
            self.parentWidget().is_authenticated()
            self.close()
        else:
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Critical)
            error_dialog.setText(auth_result)
            error_dialog.setInformativeText('See https://ytmusicapi.readthedocs.io/en/latest/setup.html#copy-authentication-headers')
            error_dialog.setWindowTitle("Error")
            error_dialog.exec_()


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
            YTMusic(os.path.join(self.credential_dir, constants.HEADERS_FILE))
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
        self.message("prompting for auth...")
        self.auth_dialog = AuthDialog(self)
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
            self.p.start("cli.exe", ["-l", self.log_dir, "-c", self.credential_dir] + args)
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
        self.message(stdout)

    def handle_state(self, state):
        states = {
            QProcess.NotRunning: 'Not running',
            QProcess.Starting: 'Starting',
            QProcess.Running: 'Running',
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    @pyqtSlot()
    def process_finished(self):
        self.message("Process finished.")
        self.p = None

    def message(self, msg):
        self.consoleTextArea.appendPlainText(msg)
        logging.info(msg)
    
if __name__ == '__main__':
    appctxt = ApplicationContext()
    window = MainWindow()
    window.show()
    sys.exit(appctxt.app.exec_())
