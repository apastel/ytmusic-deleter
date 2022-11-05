import atexit
import logging
import os
import re
import sys
from pathlib import Path

from auth_dialog import AuthDialog
from fbs_runtime import PUBLIC_SETTINGS
from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context import is_frozen
from fbs_runtime.application_context.PySide6 import ApplicationContext
from fbs_runtime.excepthook.sentry import SentryExceptionHandler
from fbs_runtime.licensing import InvalidKey
from fbs_runtime.licensing import unpack_license_key
from generated.ui_main_window import Ui_MainWindow
from license_dialog import LicenseDialog
from progress_dialog import ProgressDialog
from PySide6.QtCore import QProcess
from PySide6.QtCore import QSettings
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMessageBox
from sort_playlists_dialog import SortPlaylistsDialog
from ytmusic_deleter import constants
from ytmusicapi import YTMusic


APP_DATA_DIR = str(Path(os.getenv("APPDATA")) / "YTMusic Deleter")
progress_re = re.compile("Total complete: (\\d+)%")
item_processing_re = re.compile("(Processing \\w+: .+)")
cli_filename = "ytmusic-deleter-1.5.1.exe"

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
        self.deletePlaylistsButton.clicked.connect(self.delete_playlists)
        self.unlikeAllButton.clicked.connect(self.unlike_all)
        self.deleteAllButton.clicked.connect(self.delete_all)
        self.sortPlaylistButton.clicked.connect(self.sort_playlist)

        self.authIndicator.clicked.connect(self.prompt_for_auth)
        self.is_authenticated()

        self.add_to_library = False

        self.message(f"Starting version {PUBLIC_SETTINGS['version']}")
        if not self.license_key_is_valid():
            self.message("Your license key is invalid.")
            self.license_dialog = LicenseDialog()
            self.license_dialog.show()

    def is_authenticated(self, prompt=False):
        try:
            self.ytmusic = YTMusic(Path(self.credential_dir) / constants.HEADERS_FILE)
            self.authIndicator.setText("Authenticated")
            return True
        except (KeyError, AttributeError):
            self.message("Not authenticated yet")
            self.authIndicator.setText("Unauthenticated")
            if prompt:
                self.prompt_for_auth()
            return False

    @Slot()
    def prompt_for_auth(self):
        self.auth_dialog = AuthDialog(self)
        self.message("prompting for auth...")
        self.auth_dialog.show()

    @Slot()
    def remove_library(self):
        self.show_dialog(["remove-library"])

    @Slot()
    def delete_uploads(self):
        self.show_dialog(["delete-uploads"])

    @Slot()
    def delete_playlists(self):
        self.show_dialog(["delete-playlists"])

    @Slot()
    def unlike_all(self):
        self.show_dialog(["unlike-all"])

    @Slot()
    def delete_all(self):
        self.show_dialog(["delete-all"])

    @Slot()
    def sort_playlist(self):
        self.show_dialog(["sort-playlist"])

    def show_dialog(self, args):
        if self.p is None and self.is_authenticated(prompt=True):
            if args[0] == "sort-playlist":
                self.sort_playlists_dialog = SortPlaylistsDialog(self)
                self.sort_playlists_dialog.show()

            else:
                self.message("Showing confirmation dialog")
                if self.confirm(args) == QMessageBox.Ok:
                    if args[0] == "delete-uploads" and self.add_to_library:
                        args += ["-a"]
                        self.add_to_library_checked(False)
                    self.launch_process(args)

    def confirm(self, args):
        confirmation_dialog = QMessageBox()
        confirmation_dialog.setIcon(QMessageBox.Warning)
        if args[0] == "remove-library":
            text = "This will remove all tracks that you have added to your library from within YouTube Music."
        elif args[0] == "delete-uploads":
            text = "This will delete all your uploaded music. "
            checkbox = QCheckBox("Add uploads to library first")
            checkbox.toggled.connect(self.add_to_library_checked)
            confirmation_dialog.setCheckBox(checkbox)
        elif args[0] == "delete-playlists":
            text = "This will delete all your playlists, and may include playlists in regular YouTube.com that have music."
        elif args[0] == "unlike-all":
            text = "This will reset all your Liked songs back to neutral."
        elif args[0] == "unlike-all":
            text = "This will run Remove Library, Delete Uploads, Delete Playlists, and Unlike All Songs."
            checkbox = QCheckBox("Add uploads to library first")
            checkbox.toggled.connect(self.add_to_library_checked)
            confirmation_dialog.setCheckBox(checkbox)
        else:
            raise ValueError("Unexpected argument provided to confirmation window.")
        confirmation_dialog.setText(text)
        confirmation_dialog.setInformativeText("Are you sure you want to continue?")
        confirmation_dialog.setWindowTitle("Alert")
        confirmation_dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return confirmation_dialog.exec()

    def launch_process(self, args):
        self.p = QProcess()
        self.p.readyReadStandardOutput.connect(self.handle_stdout)
        self.p.readyReadStandardError.connect(self.handle_stderr)
        self.p.stateChanged.connect(self.handle_state)
        self.p.finished.connect(self.process_finished)
        cli_args = ["-l", self.log_dir, "-c", self.credential_dir, "-p"] + args
        self.message(f"Executing process: {Path(cli_filename).resolve()} {cli_args}")
        self.p.start(cli_filename, cli_args)
        self.progress_dialog = ProgressDialog(self)
        self.progress_dialog.show()
        if not self.p.waitForStarted():
            self.message(self.p.errorString())

    @Slot()
    def add_to_library_checked(self, is_checked):
        if is_checked:
            self.add_to_library = True
        else:
            self.add_to_library = False

    @Slot()
    def handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.message(stderr)

    @Slot()
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

    @Slot()
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

    def get_license_key(self):
        with open(Path(APP_DATA_DIR) / "license_key.txt") as f:
            key_contents = f.read()
        return unpack_license_key(key_contents, PUBLIC_SETTINGS["licensing_pubkey"])

    def license_key_is_valid(self):
        try:
            license_key = self.get_license_key()
        except FileNotFoundError:
            self.message("License key file not found. Prompt for new key.")
            return False
        except InvalidKey:
            self.message("License key was invalid. Prompt for new key.")
            return False
        else:
            self.message(f"License key was valid.\n{license_key}")
            return True


class AppContext(ApplicationContext):
    @cached_property
    def window(self):
        return MainWindow()

    @cached_property
    def exception_handlers(self):
        result = super().exception_handlers
        if is_frozen():
            result.append(self.sentry_exception_handler)
        return result

    @cached_property
    def sentry_exception_handler(self):
        return SentryExceptionHandler(
            PUBLIC_SETTINGS["sentry_dsn"],
            PUBLIC_SETTINGS["version"],
            PUBLIC_SETTINGS["environment"],
            callback=self._on_sentry_init,
        )

    def _on_sentry_init(self):
        scope = self.sentry_exception_handler.scope
        from fbs_runtime import platform

        scope.set_extra("os", platform.name())

    def run(self):
        self.window.show()
        return self.app.exec()


def flush_sentry():
    """Necessary because fbs disables Sentry's Atexit handler"""
    import sentry_sdk

    sentry_sdk.flush()


atexit.register(flush_sentry)

if __name__ == "__main__":
    appctxt = AppContext()
    appctxt.run()
