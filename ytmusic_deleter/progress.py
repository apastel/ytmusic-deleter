import logging

import enlighten
from click import get_current_context

manager = enlighten.get_manager()


def update_progress(progress_bar):
    progress_bar.update()
    if get_current_context().obj["STATIC_PROGRESS"]:
        logging.info(f"Total complete: {round(progress_bar.count / progress_bar.total * 100)}%")
