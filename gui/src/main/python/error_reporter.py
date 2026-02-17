import datetime
import json
import re
import uuid
from collections import deque

import requests
from fbs_runtime import platform
from fbs_runtime import PUBLIC_SETTINGS
from main import MainWindow
from ytmusicapi import YTMusic


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


def send_debug_report(
    parent_widget: MainWindow, yt_auth: YTMusic, app_log: str, user_title=None, user_description=None, user_contact=None
):
    """
    Send debug report to Sentry
    Args:
        yt_auth: The YTMusic instance to get current state from
        user_title: User-provided issue title (used as Sentry message)
        user_description: Optional user-provided description
        user_contact: Optional contact info for updates
    """

    request_logs = ytmusic_logger.get_request_logs()

    def safe_count(func, *args, **kwargs):
        """Safely get count from a YTMusic function, return error string on failure"""
        try:
            result = func(*args, **kwargs)
            return len(result)
        except Exception as e:
            return f"Error: {e}"

    playlist_count = safe_count(yt_auth.get_library_playlists, limit=None)
    upload_count = safe_count(yt_auth.get_library_upload_songs, limit=None)
    liked_count = safe_count(yt_auth.get_liked_songs, limit=None)
    library_count = safe_count(yt_auth.get_library_songs, limit=None)

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
        "release": PUBLIC_SETTINGS["version"],
        "environment": PUBLIC_SETTINGS["environment"],
        "extra": {
            "library stats": {
                "playlist count": playlist_count,
                "upload count": upload_count,
                "liked songs count": liked_count,
                "library songs count": library_count,
            },
            "total_requests": len(request_logs),
            "signin_type": yt_auth.auth_type.name if hasattr(yt_auth, "auth_type") else "unknown",
            "os": platform.name(),
            "account_info": yt_auth.get_account_info(),
            "description": user_description,
            "contact": user_contact,
        },
    }

    dsn = PUBLIC_SETTINGS["sentry_dsn"]
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
        "X-Sentry-Auth": f"Sentry sentry_version=7, sentry_key={key}, sentry_client=ytmusic-deleter/{PUBLIC_SETTINGS['version']}",
    }

    try:
        parent_widget.message(f"Sending report {event_id} with attachments to Sentry error reporter...")
        response = requests.post(url, data=envelope.encode("utf-8"), headers=headers, timeout=10)
        response.raise_for_status()
        parent_widget.message(f"Successfully sent error report to Sentry! Status code: {response.status_code}")
        return event_id
    except Exception as e:
        parent_widget.message(f"Failed to send error report to Sentry: {e}")
        if "response" in locals():
            parent_widget.message(f"Response: {response.text}")
        return None
