import atexit
import logging
import re
import sys
import webbrowser
from pathlib import Path
from time import strftime

import error_reporter
import requests
import sentry_sdk
import ytmusic_deleter.actions as actions
import ytmusicapi.auth.oauth.exceptions
import ytmusicapi.exceptions
from app_settings import PUBLIC_SETTINGS
from browser_auth_dialog import BrowserAuthDialog
from generated.ui_main_window import Ui_MainWindow
from library_dialogs.delete_uploads_dialog import DeleteUploadsDialog
from playlist_dialogs.add_all_to_library_dialog import AddAllToLibraryDialog
from playlist_dialogs.add_all_to_playlist_dialog import AddAllToPlaylistDialog
from playlist_dialogs.remove_dupes_dialogs.remove_duplicates_dialog import RemoveDuplicatesDialog
from playlist_dialogs.sort_playlists_dialog import SortPlaylistsDialog
from progress_dialog import ProgressDialog
from progress_worker_dialog import ProgressWorkerDialog
from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QEvent
from PySide6.QtCore import QObject
from PySide6.QtCore import QProcess
from PySide6.QtCore import QRect
from PySide6.QtCore import QSettings
from PySide6.QtCore import Qt
from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtGui import QImage
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QLabel
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QProxyStyle
from PySide6.QtWidgets import QStyle
from report_preview_dialog import DebugReportPreviewDialog
from settings_dialog import SettingsDialog
from ytmusic_deleter import common
from ytmusicapi.auth.types import AuthType

from common import APP_DATA_PATH

AUTH_INVALID_MESSAGE = "Auth file is invalid or expired. Please sign in again."
PLAYLIST_LOADING_MESSAGE = "Loading your playlists"
NETWORK_TIMEOUT_SECONDS = 8


def get_resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent.parent
    return str(base_path / relative_path)


class InternalCommandWorker(QObject):
    finished = Signal()
    error = Signal(str)
    output = Signal(str)
    progress_changed = Signal(int, str)  # (percent, description)

    def __init__(self, ytmusic, args):
        super().__init__()
        self.ytmusic = ytmusic
        self.args = args
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def _build_context(self):
        return actions.ActionContext(self.ytmusic, static_progress=False, cancelled=lambda: self.cancelled)

    def _parse_int_flag(self, cmd_args, flags, default):
        for i, arg in enumerate(cmd_args):
            if arg in flags and i + 1 < len(cmd_args):
                try:
                    return int(cmd_args[i + 1])
                except ValueError:
                    return default
        return default

    def _setup_signal_logging(self):
        import logging as logging_module

        class SignalHandler(logging_module.Handler):
            def __init__(self, worker):
                super().__init__()
                self.worker = worker

            def emit(self, record):
                try:
                    msg = self.format(record)
                    self.worker.output.emit(msg)
                except Exception:
                    pass

        signal_handler = SignalHandler(self)
        signal_handler.setFormatter(logging_module.Formatter("[%(levelname)s] %(message)s"))
        root_logger = logging_module.getLogger()
        root_logger.addHandler(signal_handler)
        self._signal_handler = signal_handler

    def _teardown_signal_logging(self):
        import logging as logging_module

        if hasattr(self, "_signal_handler"):
            root_logger = logging_module.getLogger()
            root_logger.removeHandler(self._signal_handler)
            self._signal_handler = None

    def _setup_progress_callback(self):
        def on_progress(percent, desc):
            self.progress_changed.emit(percent, desc)
            self.output.emit(f"[PROGRESS] {desc} ({percent}%)")

        from ytmusic_deleter.progress import set_progress_callback

        set_progress_callback(on_progress)

    def _execute_delete_uploads(self, context, cmd_args):
        add_to_library = "-a" in cmd_args or "--add-to-library" in cmd_args
        score_cutoff = self._parse_int_flag(cmd_args, ["-s", "--score-cutoff"], 90)
        actions.delete_uploads(context, add_to_library=add_to_library, score_cutoff=score_cutoff)

    def _execute_sort_playlist(self, context, cmd_args):
        if len(cmd_args) < 1:
            raise ValueError("sort-playlist requires a playlist title")
        playlist_titles = [cmd_args[0]]
        shuffle = "--shuffle" in cmd_args or "-s" in cmd_args
        reverse = "--reverse" in cmd_args or "-r" in cmd_args
        custom_sort = []
        for i, arg in enumerate(cmd_args):
            if arg in ["--custom-sort", "-c"] and i + 1 < len(cmd_args):
                custom_sort.append(cmd_args[i + 1])
        actions.sort_playlist(context, shuffle, tuple(playlist_titles), tuple(custom_sort), reverse)

    def _execute_remove_duplicates(self, context, cmd_args):
        if len(cmd_args) < 1:
            raise ValueError("remove-duplicates requires a playlist title")
        playlist_title = cmd_args[0]
        exact = "--exact" in cmd_args or "-e" in cmd_args
        fuzzy = "--fuzzy" in cmd_args or "-f" in cmd_args
        score_cutoff = self._parse_int_flag(cmd_args, ["--score-cutoff", "-s"], 80)
        actions.remove_duplicates(context, playlist_title, exact, fuzzy, score_cutoff)

    def _execute_add_all_to_playlist(self, context, cmd_args):
        if len(cmd_args) < 1:
            raise ValueError("add-all-to-playlist requires a playlist title")
        playlist_title = cmd_args[0]
        library = "--library" in cmd_args or "-l" in cmd_args
        uploads = "--uploads" in cmd_args or "-u" in cmd_args
        actions.add_all_to_playlist(context, playlist_title, library, uploads)

    def _execute_add_all_to_library(self, context, cmd_args):
        if len(cmd_args) < 1:
            raise ValueError("add-all-to-library requires a playlist title or ID")
        playlist_title_or_id = cmd_args[0]
        actions.add_all_to_library(context, playlist_title_or_id)

    def _dispatch_command(self, context, command, cmd_args):
        command_handlers = {
            "remove-library": lambda: actions.remove_library(context),
            "delete-playlists": lambda: actions.delete_playlists(context),
            "unlike-all": lambda: actions.unlike_all(context),
            "delete-history": lambda: actions.delete_history(context),
            "delete-all": lambda: actions.delete_all(context),
            "delete-uploads": lambda: self._execute_delete_uploads(context, cmd_args),
            "sort-playlist": lambda: self._execute_sort_playlist(context, cmd_args),
            "remove-duplicates": lambda: self._execute_remove_duplicates(context, cmd_args),
            "add-all-to-playlist": lambda: self._execute_add_all_to_playlist(context, cmd_args),
            "add-all-to-library": lambda: self._execute_add_all_to_library(context, cmd_args),
        }
        handler = command_handlers.get(command)
        if not handler:
            raise ValueError(f"Unknown internal command: {command}")
        handler()

    @Slot()
    def run(self):
        try:
            self._setup_signal_logging()
            self._setup_progress_callback()

            from ytmusic_deleter import progress as progress_module

            progress_module.set_static_progress(False)  # Disable static progress logging since we have GUI

            context = self._build_context()
            command = self.args[0] if self.args else None
            cmd_args = self.args[1:]
            self._dispatch_command(context, command, cmd_args)
        except Exception as e:
            self.error.emit(str(e))
            logging.exception(f"Error running internal command: {e}")
        finally:
            self._teardown_signal_logging()
            self.finished.emit()


def is_frozen():
    return getattr(sys, "frozen", False)


progress_re = re.compile(r"Total complete: (\d+)%")
item_processing_re = re.compile(r"(Processing .+)")


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        # Initialize settings
        self.settings = QSettings(PUBLIC_SETTINGS.app_name, PUBLIC_SETTINGS.app_name)
        try:
            self.resize(self.settings.value("mainwindow/size"))
            self.move(self.settings.value("mainwindow/pos"))
        except Exception:
            pass
        self.load_settings()

        # Ensure directory exists where we're storing logs and writing creds
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        Path(self.credential_dir).mkdir(parents=True, exist_ok=True)
        self.account_photo_dir.mkdir(parents=True, exist_ok=True)

        # Initialize a logger
        self.log_file_path = Path(self.log_dir) / f"ytmusic-deleter-gui_{strftime('%Y-%m-%d')}.log"
        logging.basicConfig(
            level=logging.DEBUG if self.verbose_logging else logging.INFO,
            format="[%(asctime)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.FileHandler(self.log_file_path, delay=True),
                logging.StreamHandler(sys.stdout),
            ],
        )
        # Add a handler for unhandled exceptions
        sys.excepthook = self.log_unhandled_exception

        # Initailize UI from generated files
        self.setupUi(self)
        self.p = None
        self._is_running = False
        self.remove_duplicates_dialog = None
        self.apply_visual_theme()

        self.centralWidget.installEventFilter(self)
        self.photo_button_stylesheet = self.accountPhotoButton.styleSheet()
        self.signOutButton.setStyleSheet(
            "QPushButton { background-color: #585b70; border-radius: 20px; border: 1px solid #45475a; color: #cdd6f4; }"
        )
        self.accountNameLabel.setStyleSheet("QLabel { border: none; color: #cdd6f4; }")
        self.channelHandleLabel.setStyleSheet("QLabel { border: none; color: #a6adc8; }")
        self.accountWidgetCloseButton.setStyleSheet(
            "QPushButton { border: none; background-color: none; color: #a6adc8; }"
        )
        self.accountPhotoButton.clicked.connect(self.account_button_clicked)
        self.signOutButton.clicked.connect(self.sign_out)
        self.accountWidgetCloseButton.clicked.connect(self.accountWidget.close)
        self.actionSettings.triggered.connect(self.open_settings_clicked)
        self.actionExit.triggered.connect(QCoreApplication.quit)
        self.reportButton.clicked.connect(self.on_report_issue_clicked)
        self.removeLibraryButton.clicked.connect(self.prepare_to_invoke)
        self.deleteUploadsButton.clicked.connect(self.prepare_to_invoke)
        self.deletePlaylistsButton.clicked.connect(self.prepare_to_invoke)
        self.unlikeAllButton.clicked.connect(self.prepare_to_invoke)
        self.deleteHistoryButton.clicked.connect(self.prepare_to_invoke)
        self.deleteAllButton.clicked.connect(self.prepare_to_invoke)
        self.sortPlaylistButton.clicked.connect(self.prepare_to_invoke)
        self.removeDupesButton.clicked.connect(self.prepare_to_invoke)
        self.addAllToPlaylistButton.clicked.connect(self.prepare_to_invoke)
        self.addAllToLibraryButton.clicked.connect(self.prepare_to_invoke)

        # Create donate button
        self.donateLabel = ClickableLabel(self.centralWidget, "https://www.buymeacoffee.com/jewbix.cube")
        self.donateLabel.setObjectName("donateLabel")
        self.donateLabel.setGeometry(QRect(40, 30, 260, 50))
        base_url = "https://img.buymeacoffee.com/button-api/"
        params = {
            "text": "Buy me a beer",
            "emoji": "🍺",
            "slug": "jewbix.cube",
            "button_colour": "FFDD00",
            "font_colour": "000000",
            "font_family": "Cookie",
            "outline_colour": "000000",
            "coffee_colour": "ffffff",
        }
        try:
            r = requests.get(base_url, params=params, timeout=NETWORK_TIMEOUT_SECONDS)
            r.raise_for_status()
            img = QImage()
            img.loadFromData(r.content)
            self.donateLabel.setPixmap(QPixmap.fromImage(img))
        except requests.exceptions.RequestException as e:
            self.message(f"Error getting image for donate button: {e}")
            self.donateLabel.setText("Click me to donate 5 bucks!")
        self.donateLabel.setToolTip("If this tool saved you a lot of time, consider buying me a beer!")

        self.signInButton.clicked.connect(self.prompt_for_auth)
        self.accountWidget.hide()

        self.add_to_library = False

        self.update_buttons()

        self.message(f"GUI version: {PUBLIC_SETTINGS.version}")
        self.message(f"Log file path: {self.log_file_path}")

    def eventFilter(self, obj, event):
        """Closes accountWidget when clicking outside of it."""
        # Alternative to this is setting the Qt.Popup flag but that causes
        # the accountWidget to appear way outside the bounds of the app.
        if obj == self.centralWidget and event.type() == QEvent.Type.MouseButtonRelease:
            if not self.accountWidget.geometry().contains(event.position().toPoint()):
                self.accountWidget.close()
        return super().eventFilter(obj, event)

    def is_signed_in(self, display_message=False) -> bool:
        """Check if user is signed in. If true, display their account info."""
        try:
            # Check for browser.json / oauth.json
            self.message(f"Checking auth file at: {self.auth_file_path}")
            self.ytmusic = ytmusicapi.YTMusic(
                str(self.auth_file_path),
                oauth_credentials=ytmusicapi.OAuthCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                ),
            )
            # Check that credential is still valid
            try:
                self.ytmusic.get_library_playlists(limit=1)
            except TypeError as e:
                self.message(AUTH_INVALID_MESSAGE)
                # Show error dialog to the user
                QMessageBox.critical(
                    self,
                    "Authentication Error",
                    AUTH_INVALID_MESSAGE,
                )
                self.sign_out()
                raise ytmusicapi.exceptions.YTMusicUserError(
                    AUTH_INVALID_MESSAGE
                ) from e
        except ytmusicapi.exceptions.YTMusicUserError:
            # User is not signed in
            if display_message:
                self.message("Click the 'Sign In' button to connect to your account.")
            return False

        # Display account name in popover
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
        try:
            response = requests.get(account_info["accountPhotoUrl"], timeout=NETWORK_TIMEOUT_SECONDS)
            response.raise_for_status()
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            pixmap = pixmap.scaled(
                self.accountPhotoButton.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            photo_path: Path = self.account_photo_dir / "account_photo.jpg"
            pixmap.save(str(photo_path))
            background_photo_style = f"\nQPushButton {{ background-image: url({photo_path.as_posix()}); }}"
            self.accountPhotoButton.setIcon(QIcon())
            self.accountPhotoButton.setStyleSheet(self.photo_button_stylesheet + background_photo_style)
        except requests.exceptions.RequestException as err:
            self.message(f"Failed to load account photo: {err}")
            self.accountPhotoButton.setStyleSheet(self.photo_button_stylesheet)

        if display_message:
            auth_str = "OAuth" if self.ytmusic.auth_type == AuthType.OAUTH_CUSTOM_CLIENT else "browser authentication"
            self.message(f"Signed in using {auth_str} as {account_name!r}")

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
        self.addAllToLibraryButton.setEnabled(is_signed_in)

    @Slot()
    def account_button_clicked(self):
        """Hide/show accountWidget when clicking profile photo"""
        if self.accountWidget.isVisible():
            self.accountWidget.hide()
        else:
            self.accountWidget.show()

    @Slot()
    def sign_out(self):
        self.message(f"Deleting auth file at: {self.auth_file_path}")
        Path.unlink(self.auth_file_path, missing_ok=True)
        del self.ytmusic
        self.message("Signed out of YTMusic Deleter.")
        self.accountWidget.hide()
        self.accountPhotoButton.hide()
        self.signInButton.show()
        self.update_buttons(False)

    @Slot()
    def prompt_for_auth(self):
        self.message("Showing login prompt.")
        if self.oauth_enabled:
            oauth = ytmusicapi.OAuthCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret,
            )
            try:
                code = oauth.get_code()
            except (
                ytmusicapi.auth.oauth.exceptions.BadOAuthClient,
                ytmusicapi.auth.oauth.exceptions.UnauthorizedOAuthClient,
            ) as e:
                self.message(str(e))
                raise

            url_prompt = QMessageBox(self)
            url_prompt.setWindowTitle("Link Your Google Account")
            url_prompt.setIcon(QMessageBox.Icon.Information)
            url = f"{code['verification_url']}?user_code={code['user_code']}"
            url_prompt.setText(
                f"Go to <a href={url!r}>{url}</a>, follow the instructions, and click OK in this window when done."
            )
            url_prompt.exec()

            try:
                raw_token = oauth.token_from_code(code["device_code"])
                ref_token = ytmusicapi.auth.oauth.RefreshingToken(credentials=oauth, **raw_token)
                # store the token in oauth.json
                ref_token.store_token(self.auth_file_path)
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
    def open_settings_clicked(self):
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.save_settings_signal.connect(self.save_settings)
        self.settings_dialog.exec()

    @Slot()
    def prepare_to_invoke(self):
        if self._is_running:
            self.message("An operation is already running. Please wait for it to finish.")
            return
        button_text = self.sender().text()
        self.message(f"{button_text} clicked.")
        # Turn "Remove Library" into "remove-library" for example
        self.show_dialog([button_text.lower().replace(" ", "-")])

    def show_dialog(self, args: list[str]):
        if self.p is None and self.is_signed_in():
            match args[0]:
                case "delete-uploads":
                    self.delete_uploads_dialog = DeleteUploadsDialog(self)
                    self.delete_uploads_dialog.show()

                case "sort-playlist":
                    please_wait_dialog = ProgressWorkerDialog(PLAYLIST_LOADING_MESSAGE, self)

                    def load_window():
                        self.remove_duplicates_dialog = SortPlaylistsDialog(self)
                        self.remove_duplicates_dialog.show()

                    please_wait_dialog.run(load_window)

                case "remove-duplicates":
                    please_wait_dialog = ProgressWorkerDialog(PLAYLIST_LOADING_MESSAGE, self)

                    def load_window():
                        self.remove_duplicates_dialog = RemoveDuplicatesDialog(self)
                        self.remove_duplicates_dialog.show()

                    please_wait_dialog.run(load_window)

                case "add-all-to-playlist":
                    please_wait_dialog = ProgressWorkerDialog(PLAYLIST_LOADING_MESSAGE, self)

                    def load_window():
                        self.remove_duplicates_dialog = AddAllToPlaylistDialog(self)
                        self.remove_duplicates_dialog.show()

                    please_wait_dialog.run(load_window)

                case "add-all-to-library":
                    please_wait_dialog = ProgressWorkerDialog(PLAYLIST_LOADING_MESSAGE, self)

                    def load_window():
                        self.remove_duplicates_dialog = AddAllToLibraryDialog(self)
                        self.remove_duplicates_dialog.show()

                    please_wait_dialog.run(load_window)

                case _:
                    self.message("Showing confirmation dialog")
                    if self.confirm(args) == QMessageBox.StandardButton.Ok:
                        if args[0] == "delete-uploads" and self.add_to_library:
                            args += ["-a"]
                            self.add_to_library_checked(False)
                        self.launch_process(args)

    def confirm(self, args: list[str]):
        confirmation_dialog = QMessageBox()
        confirmation_dialog.setIcon(QMessageBox.Icon.Warning)
        if args[0] == "remove-library":
            text = "This will remove all your library songs and albums. This will not delete your uploads."
        elif args[0] == "delete-playlists":
            text = "This will delete all your playlists, which may also include playlists in regular YouTube.com that have music."
        elif args[0] == "unlike-all":
            text = (
                "This will reset all your liked songs back to neutral.\n\n"
                "You will see many [WARNING] messages in the log as it takes several "
                "retries for the API to unlike a song."
            )
        elif args[0] == "delete-history":
            text = (
                "This will delete your play history. This does not currently work with brand accounts.\n\n"
                "Note that the API can only retrieve 200 history items at a time, so the process "
                "will appear to start over and repeat multiple times as necessary until all history is deleted."
            )
        elif args[0] == "delete-all":
            text = (
                "This will run Remove Library, Delete Uploads, Delete Playlists, Unlike All Songs, and Delete History."
            )
        else:
            raise ValueError("Unexpected argument provided to confirmation window.")
        confirmation_dialog.setText(f"{text}")
        confirmation_dialog.setInformativeText("Are you sure you want to continue?")
        confirmation_dialog.setWindowTitle("Alert")
        confirmation_dialog.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        return confirmation_dialog.exec()

    def launch_process(self, args: list[str]):
        # Try internal command execution first
        if self.launch_internal(args):
            return

    def launch_internal(self, args: list[str]) -> bool:
        if not args:
            return False

        self._set_busy_state(True, args[0])
        self.progress_dialog = ProgressDialog(self)
        self.progress_dialog.show()

        self._internal_thread = QThread()
        self._internal_worker = InternalCommandWorker(self.ytmusic, args)
        self._internal_worker.moveToThread(self._internal_thread)
        self._internal_thread.started.connect(self._internal_worker.run)
        self._internal_worker.finished.connect(self._internal_thread.quit)
        self._internal_worker.finished.connect(self.process_finished)
        self._internal_worker.error.connect(self._on_internal_error)
        self._internal_worker.output.connect(self.message)
        self._internal_worker.progress_changed.connect(self._on_internal_progress)
        self._internal_thread.finished.connect(self._internal_thread.deleteLater)
        self._internal_thread.start()

        self.message(f"Executing internal command: {args[0]}")
        return True

    @Slot(int, str)
    def _on_internal_progress(self, percent: int, desc: str):
        """Update progress bar from worker thread signals."""
        if hasattr(self, "progress_dialog") and self.progress_dialog is not None:
            try:
                if hasattr(self.progress_dialog, "progressBar"):
                    self.progress_dialog.progressBar.setValue(percent)
                if hasattr(self.progress_dialog, "itemLine"):
                    self.progress_dialog.itemLine.setText(desc)
            except Exception:
                pass

    @Slot(str)
    def _on_internal_error(self, err_msg: str):
        self.message(f"Internal command error: {err_msg}")
        self.progress_dialog.close()
        self._set_busy_state(False)

    @Slot()
    def add_to_library_checked(self, is_checked):
        if is_checked:
            self.add_to_library = True
        else:
            self.add_to_library = False

    def _on_action_progress(self, percent, desc):
        if hasattr(self, "progress_dialog") and self.progress_dialog is not None:
            try:
                self.progress_dialog.progressBar.setValue(percent)
                self.progress_dialog.itemLine.setText(desc)
            except Exception:
                pass

    @Slot()
    def handle_stderr(self):
        if self.p is not None:
            data = self.p.readAllStandardError()
            stderr = bytes(data).decode("ISO-8859-1")
            percent_complete = self.get_percent_complete(stderr)
            if percent_complete:
                self.progress_dialog.progressBar.setValue(percent_complete)
            item_processing = self.get_item_processing(stderr)
            if item_processing:
                self.progress_dialog.itemLine.setText(item_processing)
            self.message(stderr)

    def handle_state(self, state):
        states = {
            QProcess.ProcessState.NotRunning: "Not running",
            QProcess.ProcessState.Starting: "Starting",
            QProcess.ProcessState.Running: "Running",
        }
        state_name = states[state]
        self.message(f"State changed: {state_name}")

    @Slot()
    def process_finished(self):
        self.progress_dialog.close()
        self.message("Process finished.")
        self._set_busy_state(False)
        self.p = None

    def _set_busy_state(self, busy: bool, action_name: str = ""):
        self._is_running = busy
        buttons = [
            self.removeLibraryButton,
            self.deleteUploadsButton,
            self.deletePlaylistsButton,
            self.unlikeAllButton,
            self.deleteHistoryButton,
            self.deleteAllButton,
            self.sortPlaylistButton,
            self.removeDupesButton,
            self.addAllToPlaylistButton,
            self.addAllToLibraryButton,
            self.signInButton,
            self.signOutButton,
            self.accountPhotoButton,
        ]
        for button in buttons:
            button.setEnabled(not busy)

        if busy and action_name:
            self.message(f"Running {action_name}...")
        elif not busy:
            self.update_buttons(display_message=False)

    def apply_visual_theme(self):
        self.setStyleSheet(
            """
            QMainWindow { background: #1e1e2e; }
            QWidget { background: #1e1e2e; color: #cdd6f4; }
            QLabel { color: #cdd6f4; }
            QLabel#accountNameLabel { font-weight: 700; color: #cdd6f4; }
            QLabel#channelHandleLabel { color: #a6adc8; }
            QLabel#playlistFunctionsLabel { color: #a6adc8; }
            QLabel#consoleLabel { color: #a6adc8; }
            QLabel#orLabel { color: #a6adc8; }
            QPushButton {
                background: #1f6a5a;
                color: #ffffff;
                border: 1px solid #155043;
                border-radius: 10px;
                padding: 8px 14px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover { background: #25806c; }
            QPushButton:pressed { background: #155043; }
            QPushButton:disabled {
                background: #3b3b4f;
                color: #6c7086;
                border-color: #45475a;
            }
            QPlainTextEdit {
                background: #181825;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 8px;
                font-family: 'Menlo', 'Consolas', monospace;
                font-size: 12px;
            }
            QMenuBar {
                background: #181825;
                color: #cdd6f4;
                border-bottom: 1px solid #45475a;
            }
            QMenuBar::item:selected { background: #313244; }
            QMenu {
                background: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
            }
            QMenu::item:selected { background: #313244; }
            QStatusBar { background: #181825; color: #a6adc8; }
            QMessageBox { background: #1e1e2e; color: #cdd6f4; }
            QDialog { background: #1e1e2e; color: #cdd6f4; }
            QProgressBar {
                background: #313244;
                border: 1px solid #45475a;
                border-radius: 5px;
                text-align: center;
                color: #cdd6f4;
            }
            QProgressBar::chunk {
                background: #1f6a5a;
                border-radius: 4px;
            }
            QLineEdit, QTextEdit {
                background: #181825;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QCheckBox { color: #cdd6f4; }
            QCheckBox::indicator {
                border: 1px solid #45475a;
                border-radius: 3px;
                background: #181825;
            }
            QCheckBox::indicator:checked {
                background: #1f6a5a;
                border-color: #155043;
            }
            QComboBox {
                background: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QComboBox QAbstractItemView {
                background: #1e1e2e;
                color: #cdd6f4;
                selection-background-color: #313244;
            }
            QScrollBar:vertical {
                background: #181825;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #45475a;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover { background: #585b70; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            """
        )

    def message(self, msg, exc_info=None):
        msg = msg.rstrip()  # Remove extra newlines
        self.consoleTextArea.appendPlainText(msg)
        if exc_info:
            logging.exception("Unhandled exception occurred", exc_info=exc_info)

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
        self.settings.setValue("client_id", self.settings_dialog.clientIdInput.text().strip())
        self.settings.setValue("client_secret", self.settings_dialog.clientSecretInput.text().strip())
        self.load_settings()
        self.update_buttons()

    def load_settings(self):
        self.log_dir = APP_DATA_PATH / "logs"
        self.credential_dir = APP_DATA_PATH / "credentials"
        self.account_photo_dir = APP_DATA_PATH / "resources"
        self.verbose_logging = self.settings.value("verbose_logging", False, type=bool)
        self.oauth_enabled = self.settings.value("oauth_enabled", False, type=bool)
        self.client_id = self.settings.value("client_id", "", type=str)
        self.client_secret = self.settings.value("client_secret", "", type=str)

        logging.getLogger().setLevel(logging.DEBUG if self.verbose_logging else logging.INFO)
        self.auth_file_path = Path(
            self.credential_dir / (common.OAUTH_FILENAME if self.oauth_enabled else common.BROWSER_FILENAME)
        )

    def log_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        self.message(
            "Unhandled exception occurred, check the logs or click 'Report a Problem'",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

    def on_report_issue_clicked(self):
        # Read the app log file
        log_preview = ""
        if self.log_file_path.exists():
            try:
                with open(self.log_file_path, encoding="latin-1", errors="replace") as f:
                    log_preview = f.read()
                self.message(f"Read {len(log_preview)} bytes from log file for error report.")
            except Exception as e:
                self.message(f"Failed to read log file: {e}")
                log_preview = f"Error reading log file: {e}"
        else:
            self.message(f"Log file not found at {self.log_file_path}")
            log_preview = "Log file not found"

        dialog = DebugReportPreviewDialog(log_preview)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = dialog.get_user_title()
            description = dialog.get_user_description()
            contact = dialog.get_user_contact()
            app_log = dialog.get_edited_logs()

            yt_auth: ytmusicapi.YTMusic | None = self.ytmusic if hasattr(self, "ytmusic") else None

            def send_report():
                return error_reporter.send_debug_report(self, yt_auth, app_log, title, description, contact)

            def on_report_sent(result):
                if isinstance(result, Exception):
                    logging.exception("Failed to send debug report", exc_info=result)
                    QMessageBox.warning(
                        self,
                        "Report Failed",
                        "Failed to send the debug report. Please copy the logs from the Console Log and report the"
                        " issue on GitHub or Discord.",
                    )
                elif result:
                    QMessageBox.information(
                        self, "Report Sent", f"Thank you! Your report has been sent.\nReference ID: {result}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Report Failed",
                        "Failed to send the debug report. Please copy the logs from the Console Log and report the"
                        " issue on GitHub or Discord.",
                    )

            progress = ProgressWorkerDialog("Building and sending debug report", self)
            progress.run(send_report, on_report_sent)


class AppContext:
    def __init__(self):

        self.app = QApplication(sys.argv)
        icon_path = get_resource_path("icons/Icon.ico")
        app_icon = QIcon(icon_path)
        self.app.setWindowIcon(app_icon)

        self.window = MainWindow()
        self.window.setWindowIcon(app_icon)

        # Setup Sentry if DSN is available and frozen
        if is_frozen() and PUBLIC_SETTINGS.sentry_dsn:
            sentry_sdk.init(
                dsn=PUBLIC_SETTINGS.sentry_dsn,
                release=PUBLIC_SETTINGS.version,
                environment="production",
            )

    def run(self):
        self.app.setStyle("Fusion")
        self.app.setStyle(InstantToolTipStyle(self.app.style()))
        self.window.show()
        return self.app.exec()


class InstantToolTipStyle(QProxyStyle):
    def styleHint(self, hint, option=None, widget=None, return_data=None):
        if hint == QStyle.StyleHint.SH_ToolTip_WakeUpDelay:
            return 0
        return super().styleHint(hint, option, widget, return_data)


class ClickableLabel(QLabel):
    def __init__(self, parent, link):
        QLabel.__init__(self, parent)
        self.link = link

    def mousePressEvent(self, event):
        webbrowser.open(self.link)


def flush_sentry():
    sentry_sdk.flush()


atexit.register(flush_sentry)

if __name__ == "__main__":
    appctxt = AppContext()
    appctxt.run()
