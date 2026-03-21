import logging
import threading

import enlighten


class NullProgressBar:
    """A null progress bar that does nothing but tracks count."""

    def __init__(self, *args, **kwargs):
        self.count = 0
        self.total = kwargs.get("total", 0)
        self.desc = kwargs.get("desc", "")

    def update(self, incr=1):
        self.count += incr

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class NullManager:
    """A null manager that returns null progress bars."""

    def counter(self, **kwargs):
        return NullProgressBar(**kwargs)


class SmartManager:
    """A manager that checks the current thread and uses enlighten or null accordingly."""

    def __init__(self):
        # Create the real manager lazily on first use
        self._real_manager = None
        self._null_manager = NullManager()

    def _get_manager(self):
        """Get the appropriate manager based on current thread."""
        if threading.current_thread() is threading.main_thread():
            # We're in the main thread, use the real manager
            if self._real_manager is None:
                try:
                    self._real_manager = enlighten.get_manager()
                except Exception:
                    # If enlighten fails for any reason, fall back to null
                    return self._null_manager
            return self._real_manager
        else:
            # We're in a worker thread, use null manager
            return self._null_manager

    def counter(self, **kwargs):
        """Create a progress counter, using the appropriate manager."""
        return self._get_manager().counter(**kwargs)


# Use the smart manager which adapts to the thread at runtime
manager = SmartManager()

STATIC_PROGRESS = False
progress_callback = None


def set_static_progress(enabled: bool):
    global STATIC_PROGRESS
    STATIC_PROGRESS = enabled


def set_progress_callback(callback):
    global progress_callback
    progress_callback = callback


def update_progress(progress_bar):
    progress_bar.update()
    percent = round(progress_bar.count / progress_bar.total * 100) if progress_bar.total else 0
    if STATIC_PROGRESS:
        logging.info(f"Total complete: {percent}%")
    if progress_callback:
        try:
            progress_callback(percent, progress_bar.desc)
        except Exception:
            logging.exception("Failed to run progress callback")
