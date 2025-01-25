import atexit
import logging
import os
import re
import shutil
import subprocess
import sys
import webbrowser
from importlib.metadata import version
from json import JSONDecodeError
from pathlib import Path
from time import strftime
from typing import List

import requests
from add_all_to_playlist_dialog import AddAllToPlaylistDialog
from browser_auth_dialog import BrowserAuthDialog
from fbs_runtime import PUBLIC_SETTINGS
from fbs_runtime.application_context import cached_property
from fbs_runtime.application_context import is_frozen
from fbs_runtime.application_context.PySide6 import ApplicationContext
from fbs_runtime.excepthook.sentry import SentryExceptionHandler
from generated.ui_main_window import Ui_MainWindow
from progress_dialog import ProgressDialog
from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QEvent
from PySide6.QtCore import QProcess
from PySide6.QtCore import QRect
from PySide6.QtCore import QSettings
from PySide6.QtCore import Qt
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtGui import QImage
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QCheckBox
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMessageBox
from remove_duplicates_dialog import RemoveDuplicatesDialog
from settings_dialog import SettingsDialog
from sort_playlists_dialog import SortPlaylistsDialog
from ytmusic_deleter import common as const
from ytmusicapi import YTMusic
from ytmusicapi.auth.oauth import OAuthCredentials
from ytmusicapi.auth.oauth import RefreshingToken
from ytmusicapi.auth.types import AuthType

from common import APP_DATA_DIR


internal_directory = os.path.dirname(os.path.abspath(__file__))
CLI_EXECUTABLE = f"{internal_directory}/ytmusic-deleter" if is_frozen() else "ytmusic-deleter"
progress_re = re.compile(r"Total complete: (\d+)%")
item_processing_re = re.compile(r"(Processing .+)")


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        # Initialize settings
        self.settings = QSettings("apastel", PUBLIC_SETTINGS["app_name"])
        try:
            self.resize(self.settings.value("mainwindow/size"))
            self.move(self.settings.value("mainwindow/pos"))
        except Exception:
            pass
        self.load_settings()

        # Ensure directory exists where we're storing logs and writing creds
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        Path(self.credential_dir).mkdir(parents=True, exist_ok=True)

        # Initialize a logger
        logging.basicConfig(
            level=logging.DEBUG if self.verbose_logging else logging.INFO,
            format="[%(asctime)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler(Path(APP_DATA_DIR) / f"ytmusic-deleter-gui_{strftime('%Y-%m-%d')}.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        # Add a handler for unhandled exceptions
        sys.excepthook = self.log_unhandled_exception

        # Initailize UI from generated files
        self.setupUi(self)
        self.p = None

        self.centralWidget.installEventFilter(self)
        self.photo_button_stylesheet = self.accountPhotoButton.styleSheet()
        self.signOutButton.setStyleSheet(
            "QPushButton { background-color: #666666; border-radius: 20px; border: 1px solid; }"
        )
        self.accountNameLabel.setStyleSheet("QLabel { border: none; color: black; }")
        self.channelHandleLabel.setStyleSheet("QLabel { border: none; color: black; }")
        self.accountWidgetCloseButton.setStyleSheet(
            "QPushButton { border: none; background-color: none; color: black; }"
        )
        self.accountPhotoButton.clicked.connect(self.account_button_clicked)
        self.signOutButton.clicked.connect(self.sign_out)
        self.accountWidgetCloseButton.clicked.connect(self.accountWidget.close)
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.save_settings_signal.connect(self.save_settings)
        self.actionSettings.triggered.connect(self.settings_dialog.exec)
        self.actionExit.triggered.connect(QCoreApplication.quit)
        self.removeLibraryButton.clicked.connect(self.prepare_to_invoke)
        self.deleteUploadsButton.clicked.connect(self.prepare_to_invoke)
        self.deletePlaylistsButton.clicked.connect(self.prepare_to_invoke)
        self.unlikeAllButton.clicked.connect(self.prepare_to_invoke)
        self.deleteHistoryButton.clicked.connect(self.prepare_to_invoke)
        self.deleteAllButton.clicked.connect(self.prepare_to_invoke)
        self.sortPlaylistButton.clicked.connect(self.prepare_to_invoke)
        self.removeDupesButton.clicked.connect(self.prepare_to_invoke)
        self.addAllToPlaylistButton.clicked.connect(self.prepare_to_invoke)

        # Create donate button
        self.donateLabel = ClickableLabel(self.centralWidget, "https://www.buymeacoffee.com/jewbix.cube")
        self.donateLabel.setObjectName("donateLabel")
        self.donateLabel.setGeometry(QRect(40, 30, 260, 50))
        base_url = "https://img.buymeacoffee.com/button-api/"
        params = {
            "text": "Buy me a beer!",
            "emoji": "🍺",
            "slug": "jewbix.cube",
            "button_colour": "FFDD00",
            "font_colour": "000000",
            "font_family": "Cookie",
            "outline_colour": "000000",
            "coffee_colour": "ffffff",
        }
        try:
            r = requests.get(base_url, params=params)
            r.raise_for_status()
            img = QImage()
            img.loadFromData(r.content)
            self.donateLabel.setPixmap(QPixmap.fromImage(img))
        except requests.exceptions.RequestException as e:
            self.message(f"Error getting image for donate button: {e}")
            self.donateLabel.setText("Click me to donate 5 bucks!")
        self.donateLabel.setToolTip(
            "It's a donate button! If this tool saved you a lot of time, consider buying me a beer!"
        )

        self.signInButton.clicked.connect(self.prompt_for_auth)
        self.accountWidget.hide()

        self.add_to_library = False

        self.update_buttons()

        self.message(f"GUI version: {PUBLIC_SETTINGS['version']}")
        cli_path = shutil.which(CLI_EXECUTABLE)
        if cli_path:
            self.message(f"CLI path: {cli_path}")
            try:
                p = subprocess.Popen(
                    [CLI_EXECUTABLE, "-n", "--version"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                )
                version_str = p.stdout.read().decode("UTF-8")
                self.message(f"CLI version: {version_str}")
            except subprocess.CalledProcessError as e:
                self.message(f"Error getting the version of the CLI executable, {e}")
        else:
            self.message(
                f"{CLI_EXECUTABLE!r} executable not found. It's possible that it's not installed and none of the functions will work."  # noqa
            )
        self.message(f"ytmusicapi version: {version('ytmusicapi')}")

    def eventFilter(self, obj, event):
        """Closes accountWidget when clicking outside of it."""
        # Alternative to this is setting the Qt.Popup flag but that causes
        # the accountWidget to appear way outside the bounds of the app.
        if obj == self.centralWidget and event.type() == QEvent.MouseButtonRelease:
            if not self.accountWidget.geometry().contains(event.position().toPoint()):
                self.accountWidget.close()
        return super().eventFilter(obj, event)

    def is_signed_in(self, display_message=False) -> bool:
        """Check if user is signed in. If true, display their account info."""
        try:
            # Check for browser.json / oauth.json
            self.ytmusic = YTMusic(str(Path(self.credential_dir) / self.auth_file_name))
        except JSONDecodeError:
            # User is not signed in
            if display_message:
                self.message("Click the 'Sign In' button to connect to your account.")
            return False

        # Display account name in popover
        if self.ytmusic.auth_type in AuthType.oauth_types():
            try:
                account_info: dict = self.ytmusic.get_account_info()
            except Exception as e:
                message = "Failed to get user's account info. Clearing login state then log back in."
                self.message(message + "\n" + str(e))
                logging.exception(message, e)
                self.sign_out()
                return False
            account_name = account_info["accountName"]
            self.accountNameLabel.setText(account_name)
            channel_handle = account_info["channelHandle"]
            if channel_handle:
                self.channelHandleLabel.setText(f"({channel_handle})")
            else:
                self.channelHandleLabel.setText("")

            # Display account photo
            response = requests.get(account_info["accountPhotoUrl"])
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            pixmap = pixmap.scaled(self.accountPhotoButton.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            photo_path = str(Path(Path(APP_DATA_DIR) / "account_photo.jpg"))
            pixmap.save(photo_path)
            background_photo_style = f"\nQPushButton {{ background-image: url({Path(photo_path).as_posix()}); }}"
            self.accountPhotoButton.setStyleSheet(self.photo_button_stylesheet + background_photo_style)

            if display_message:
                self.message(f"Signed in as {account_name!r}")
        else:
            pixmap = QPixmap(AppContext._instance.get_resource("person.png"))
            pixmap = pixmap.scaled(self.accountPhotoButton.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon = QIcon(pixmap)
            self.accountPhotoButton.setIcon(icon)
            self.accountPhotoButton.setIconSize(pixmap.size())
            self.accountNameLabel.setText("Signed in")
            self.channelHandleLabel.setText("")
            if display_message:
                self.message("Signed in.")

        return True

    def update_buttons(self, display_message=True):
        """Update the display status of the buttons when initializing or signing in/out"""
        is_signed_in = self.is_signed_in(display_message)
        self.accountPhotoButton.setVisible(is_signed_in)
        self.signInButton.setVisible(not is_signed_in)
        self.removeLibraryButton.setEnabled(is_signed_in)
        self.deleteUploadsButton.setEnabled(is_signed_in)
        self.deletePlaylistsButton.setEnabled(is_signed_in)
        self.unlikeAllButton.setEnabled(is_signed_in)
        self.deleteHistoryButton.setEnabled(is_signed_in)
        self.deleteAllButton.setEnabled(is_signed_in)
        self.sortPlaylistButton.setEnabled(is_signed_in)
        self.removeDupesButton.setEnabled(is_signed_in)
        self.addAllToPlaylistButton.setEnabled(is_signed_in)

    @Slot()
    def account_button_clicked(self):
        """Hide/show accountWidget when clicking profile photo"""
        if self.accountWidget.isVisible():
            self.accountWidget.hide()
        else:
            self.accountWidget.show()

    @Slot()
    def sign_out(self):
        Path.unlink(Path(Path(self.credential_dir) / self.auth_file_name))
        self.message("Signed out of YTMusic Deleter.")
        self.accountWidget.hide()
        self.accountPhotoButton.hide()
        self.signInButton.show()
        self.update_buttons(False)

    @Slot()
    def prompt_for_auth(self):
        self.message("Showing login prompt.")
        if self.oauth_enabled:
            oauth = OAuthCredentials()
            code = oauth.get_code()

            url_prompt = QMessageBox()
            url_prompt.setIcon(QMessageBox.Information)
            url = f"{code['verification_url']}?user_code={code['user_code']}"
            url_prompt.setText(
                f"<html>Go to <a href={url!r}>{url}</a>, follow the instructions, and click OK in this window when done.</html>"
            )
            url_prompt.setInformativeText(
                "<html>This OAuth flow uses the <a href='https://developers.google.com/youtube/v3/guides/auth/devices'>Google API flow for TV devices</a>.</html>"  # noqa
            )
            url_prompt.exec()

            raw_token = oauth.token_from_code(code["device_code"])
            try:
                ref_token = RefreshingToken(credentials=oauth, **raw_token)
                # store the token in oauth.json
                ref_token.store_token(Path(Path(self.credential_dir) / const.OAUTH_FILENAME))
                if self.is_signed_in():
                    self.message("Successfully signed in.")
                else:
                    self.message("Failed to sign in. Try again.")
            except Exception as e:
                logging.exception(e)
                self.message("Failed to sign in. Try again.\n" + str(e))

            self.update_buttons()
        else:
            self.auth_dialog = BrowserAuthDialog(self)
            self.auth_dialog.show()

    @Slot()
    def prepare_to_invoke(self):
        button_text = self.sender().text()
        self.message(f"{button_text} clicked.")
        # Turn "Remove Library" into "remove-library" for example
        self.show_dialog([button_text.lower().replace(" ", "-")])

    def show_dialog(self, args: List[str]):
        if self.p is None and self.is_signed_in():
            if args[0] == "sort-playlist":
                self.sort_playlists_dialog = SortPlaylistsDialog(self)
                self.sort_playlists_dialog.show()

            elif args[0] == "remove-duplicates":
                self.remove_duplicates_dialog = RemoveDuplicatesDialog(self)
                self.remove_duplicates_dialog.show()

            elif args[0] == "add-all-to-playlist":
                self.add_all_to_playlist_dialog = AddAllToPlaylistDialog(self)
                self.add_all_to_playlist_dialog.show()

            else:
                self.message("Showing confirmation dialog")
                if self.confirm(args) == QMessageBox.Ok:
                    if args[0] == "delete-uploads" and self.add_to_library:
                        args += ["-a"]
                        self.add_to_library_checked(False)
                    self.launch_process(args)

    def confirm(self, args: List[str]):
        confirmation_dialog = QMessageBox()
        confirmation_dialog.setIcon(QMessageBox.Warning)
        if args[0] == "remove-library":
            text = 'This is the same as clicking "Remove from library" on all albums that you have added to your library by clicking "Add to library" within YT Music. This will not delete your uploads.'  # noqa
        elif args[0] == "delete-uploads":
            text = "This will delete all your uploaded music. "
            checkbox = QCheckBox("Add uploads to library first")
            checkbox.toggled.connect(self.add_to_library_checked)
            confirmation_dialog.setCheckBox(checkbox)
        elif args[0] == "delete-playlists":
            text = "This will delete all your playlists, which may also include playlists in regular YouTube.com that have music."
        elif args[0] == "unlike-all":
            text = "This will reset all your Liked songs back to neutral."
        elif args[0] == "delete-history":
            text = """
            This will delete your play history. This does not currently work with brand accounts.
            Note that the API can only retrieve 200 history items at a time, so the process will appear to start over and repeat multiple times as necessary until all history is deleted."
            """  # noqa
        elif args[0] == "delete-all":
            text = (
                "This will run Remove Library, Delete Uploads, Delete Playlists, Unlike All Songs, and Delete History."
            )
        else:
            raise ValueError("Unexpected argument provided to confirmation window.")
        confirmation_dialog.setText(f"{text}")
        confirmation_dialog.setInformativeText("Are you sure you want to continue?")
        confirmation_dialog.setWindowTitle("Alert")
        confirmation_dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        return confirmation_dialog.exec()

    def launch_process(self, args: List[str]):
        self.p = QProcess()
        self.p.readyReadStandardOutput.connect(self.handle_stdout)
        self.p.readyReadStandardError.connect(self.handle_stderr)
        self.p.stateChanged.connect(self.handle_state)
        self.p.finished.connect(self.process_finished)
        cli_args: List[str] = (
            [
                "-l",
                self.log_dir,
                "-c",
                self.credential_dir,
                "-p",
                "-n",
            ]
            + (["-v"] if self.verbose_logging else [])
            + (["-o"] if self.oauth_enabled else [])
            + args
        )
        self.message(f"Executing process: {CLI_EXECUTABLE} {' '.join(cli_args)}")
        self.p.start(CLI_EXECUTABLE, cli_args)
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
        stderr = bytes(data).decode("ISO-8859-1")
        self.message(stderr)

    @Slot()
    def handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("ISO-8859-1")
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

    @Slot()
    def save_settings(self):
        self.settings.setValue("verbose_logging", self.settings_dialog.verboseCheckBox.isChecked())
        self.settings.setValue("oauth_enabled", self.settings_dialog.oauthCheckbox.isChecked())
        self.load_settings()

    def load_settings(self):
        self.log_dir = self.settings.value("log_dir", APP_DATA_DIR)
        self.credential_dir = self.settings.value("credential_dir", APP_DATA_DIR)
        self.verbose_logging = self.settings.value("verbose_logging", False, type=bool)
        self.oauth_enabled = self.settings.value("oauth_enabled", False, type=bool)

        logging.getLogger().setLevel(logging.DEBUG if self.verbose_logging else logging.INFO)
        self.auth_file_name = const.OAUTH_FILENAME if self.oauth_enabled else const.BROWSER_FILENAME

    def log_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        logging.exception("Unhandled exception occurred", exc_info=(exc_type, exc_value, exc_traceback))


class AppContext(ApplicationContext):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

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


class ClickableLabel(QLabel):
    def __init__(self, parent, link):
        QLabel.__init__(self, parent)
        self.link = link

    def mousePressEvent(self, event):
        webbrowser.open(self.link)


def flush_sentry():
    """Necessary because fbs disables Sentry's Atexit handler"""
    import sentry_sdk

    sentry_sdk.flush()


atexit.register(flush_sentry)

if __name__ == "__main__":
    appctxt = AppContext()
    appctxt.run()
