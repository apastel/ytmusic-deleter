import sys


# Platform detection
class Platform:
    @staticmethod
    def is_windows():
        return sys.platform == "win32"

    @staticmethod
    def is_linux():
        return sys.platform == "linux"

    @staticmethod
    def is_mac():
        return sys.platform == "darwin"

    @property
    def name(self):
        if self.is_windows():
            return "windows"
        elif self.is_linux():
            return "linux"
        elif self.is_mac():
            return "mac"
        return "unknown"


platform = Platform()


def is_frozen():
    return getattr(sys, "frozen", False)


# App settings - replace FBS PUBLIC_SETTINGS
class AppSettings:
    def __init__(self):
        self.app_name = "YTMusic_Deleter"
        # Version is managed by pdm and written to ytmusic_deleter/_version.py
        try:
            from ytmusic_deleter._version import __version__ as version

            self.version = version
        except ImportError:
            self.version = "dev"

        # Sentry DSN - hardcoded since it's not sensitive
        self.sentry_dsn = "https://8cecdde1e7344deda25e39924c01a73c@o1393803.ingest.sentry.io/6715501"

        # Environment - production for frozen builds, dev otherwise
        self.environment = "production" if is_frozen() else "development"

        self.author = "apastel"


# Global instance
PUBLIC_SETTINGS = AppSettings()
