import os
import pathlib

from app_settings import PUBLIC_SETTINGS

APP_DATA_PATH: pathlib.Path = (
    pathlib.Path(os.getenv("APPDATA" if os.name == "nt" else "HOME")) / PUBLIC_SETTINGS.app_name
)
