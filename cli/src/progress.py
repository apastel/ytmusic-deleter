import logging

import enlighten

manager = enlighten.get_manager(no_resize=True)


def update_progress(ctx, progress_bar):
    progress_bar.update()
    if ctx.obj["STATIC_PROGRESS"]:
        logging.info(
            f"Total complete: {round(progress_bar.count / progress_bar.total * 100)}%"
        )
