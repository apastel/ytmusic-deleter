from importlib.metadata import PackageNotFoundError
from importlib.metadata import version


def get_version() -> str:
    try:
        return version("ytmusic-deleter")
    except PackageNotFoundError:
        return "dev"
