import datetime
import json
import re
import uuid
from collections import deque
from pathlib import Path
from typing import Any
from typing import TYPE_CHECKING

import requests
from app_settings import platform
from app_settings import PUBLIC_SETTINGS
from ytmusicapi import YTMusic

if TYPE_CHECKING:
    from main import MainWindow


class YTMusicAPILogger:
    def __init__(self, max_size=100):
        """Keep last 100 API calls in memory"""
        self.buffer = deque(maxlen=max_size)

    def log_response(self, endpoint, body, response):
        """Add API response to buffer"""
        self.buffer.append(
            {
                "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
                "endpoint": endpoint,
                "request_body": body,
                "status_code": getattr(response, "status_code", None),
                "response_body": str(response),
            }
        )

    def get_request_logs(self):
        """Get all buffered ytmusicapi request logs"""
        return list(self.buffer)

    def clear(self):
        """Clear buffer after reporting"""
        self.buffer.clear()


# Global logger instance
ytmusic_logger = YTMusicAPILogger()

# Monkey-patch ytmusicapi
original_send_request = YTMusic._send_request


def logged_send_request(self, endpoint, body, additionalParams=""):
    response = original_send_request(self, endpoint, body, additionalParams)

    # Only buffer in memory, not logged anywhere
    ytmusic_logger.log_response(endpoint, body, response)

    return response


YTMusic._send_request = logged_send_request


def safe_count(func, *args, **kwargs):
    """Safely get count from a YTMusic function, return error string on failure.

    Some YTMusic APIs return a dict with a "tracks" key instead of a list,
    so we special-case that format here.
    """
    try:
        result = func(*args, **kwargs)
        # If the result is a dict containing a tracks list, count that instead
        if isinstance(result, dict) and "tracks" in result:
            return len(result.get("tracks", []))
        return len(result)
    except Exception as e:
        return f"Error: {e}"


def collect_debug_context(yt_auth: YTMusic | None) -> dict[str, Any]:
    request_logs = ytmusic_logger.get_request_logs()

    playlist_count = safe_count(yt_auth.get_library_playlists, limit=None) if yt_auth else "unknown"
    upload_count = safe_count(yt_auth.get_library_upload_songs, limit=None) if yt_auth else "unknown"
    liked_count = safe_count(yt_auth.get_liked_songs, limit=None) if yt_auth else "unknown"
    library_count = safe_count(yt_auth.get_library_songs, limit=None) if yt_auth else "unknown"

    return {
        "library stats": {
            "playlist count": playlist_count,
            "upload count": upload_count,
            "liked songs count": liked_count,
            "library songs count": library_count,
        },
        "total_requests": len(request_logs),
        "signin_type": (
            (yt_auth.auth_type.name if hasattr(yt_auth, "auth_type") else "unknown") if yt_auth else "Not signed in"
        ),
        "os": platform.name,
        "account_info": safe_get_account_info(yt_auth),
    }


def safe_get_account_info(yt_auth: YTMusic | None):
    if not yt_auth:
        return "Not signed in"
    try:
        return yt_auth.get_account_info()
    except Exception as e:
        return f"Error: {e}"


def read_app_log(log_file_path: Path) -> str:
    if not log_file_path.exists():
        return f"Log file not found at {log_file_path}"
    try:
        with open(log_file_path, encoding="latin-1", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"Error reading log file: {e}"


def add_debug_context_to_sentry_event(
    event: dict[str, Any],
    hint: dict[str, Any],
    yt_auth: YTMusic | None,
    app_log: str,
):
    """Attach debug-report diagnostics to an automatic Sentry event."""
    try:
        from sentry_sdk.attachments import Attachment

        request_logs = ytmusic_logger.get_request_logs()
        event.setdefault("extra", {}).update(collect_debug_context(yt_auth))

        attachments = hint.setdefault("attachments", [])
        attachments.append(
            Attachment(
                bytes=json.dumps(request_logs, indent=2).encode("utf-8"),
                filename="ytmusicapi-request-logs.json",
                content_type="application/json",
            )
        )
        attachments.append(
            Attachment(
                bytes=app_log.encode("utf-8"),
                filename="ytmusic-deleter-app-logs.txt",
                content_type="text/plain",
            )
        )
    except Exception as e:
        event.setdefault("extra", {})["debug_report_context_error"] = str(e)

    return event


def send_debug_report(
    parent_widget: "MainWindow",
    yt_auth: YTMusic | None,
    app_log: str,
    user_title=None,
    user_description=None,
    user_contact=None,
):
    """
    Send debug report to Sentry
    Args:
        yt_auth: The YTMusic instance for the user (or none if they're not signed in)
        user_title: User-provided issue title (used as Sentry message)
        user_description: Optional user-provided description
        user_contact: Optional contact info for updates
    """

    request_logs = ytmusic_logger.get_request_logs()
    debug_context = collect_debug_context(yt_auth)

    # Build the event payload manually
    event_id = uuid.uuid4().hex

    # Use user's title or default
    message = user_title if user_title else "User-submitted debug report"

    event = {
        "event_id": event_id,
        "platform": "python",
        "level": "info",
        "message": message,
        "culprit": user_description if user_description else "User-submitted debug report",
        "release": PUBLIC_SETTINGS.version,
        "environment": PUBLIC_SETTINGS.environment,
        "extra": {
            **debug_context,
            "description": user_description,
            "contact": user_contact,
        },
    }

    dsn = PUBLIC_SETTINGS.sentry_dsn
    match = re.match(r"https://([^@]+)@([^/]+)/(\d+)", dsn)
    if not match:
        parent_widget.message("Invalid Sentry DSN")
        return None

    key, host, project_id = match.groups()

    event_item_header = {"type": "event"}
    event_item_payload = json.dumps(event)

    # Attachment 1: ytmusicapi logs
    request_logs_bytes = json.dumps(request_logs, indent=2).encode("utf-8")
    ytmusic_attachment_header = {
        "type": "attachment",
        "length": len(request_logs_bytes),
        "filename": "ytmusicapi-request-logs.json",
        "content_type": "application/json",
    }

    # Attachment 2: app log file
    app_log_bytes = app_log.encode("utf-8")
    app_log_attachment_header = {
        "type": "attachment",
        "length": len(app_log_bytes),
        "filename": "ytmusic-deleter-app-logs.txt",
        "content_type": "text/plain",
    }

    # Build the envelope properly
    envelope_header = {}
    envelope_parts = [
        json.dumps(envelope_header),
        json.dumps(event_item_header),
        event_item_payload,
        json.dumps(ytmusic_attachment_header),
        request_logs_bytes.decode("utf-8"),
        json.dumps(app_log_attachment_header),
        app_log_bytes.decode("utf-8"),
    ]

    envelope = "\n".join(envelope_parts)

    # Send to Sentry's envelope endpoint
    url = f"https://{host}/api/{project_id}/envelope/"
    headers = {
        "Content-Type": "application/x-sentry-envelope",
        "X-Sentry-Auth": f"Sentry sentry_version=7, sentry_key={key}, sentry_client=ytmusic-deleter/{PUBLIC_SETTINGS.version}",
    }

    try:
        response = requests.post(url, data=envelope.encode("utf-8"), headers=headers, timeout=10)
        response.raise_for_status()
        return event_id
    except Exception:
        return None
