import datetime
import json
import pathlib
import uuid
from collections import deque

import requests
from fbs_runtime import platform
from fbs_runtime import PUBLIC_SETTINGS
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
                "response_body": str(response)[:5000],
            }
        )

    def get_logs(self):
        """Get all buffered logs"""
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
    yt_auth: YTMusic, log_file_path: pathlib.Path, user_title=None, user_description=None, user_contact=None
):
    """
    Send debug report to Sentry
    Args:
        yt_auth: The YTMusic instance to get current state from
        user_title: User-provided issue title (used as Sentry message)
        user_description: Optional user-provided description
        user_contact: Optional contact info for updates
    """

    logs = ytmusic_logger.get_logs()

    # Get additional context from ytmusic instance
    try:
        playlists = yt_auth.get_library_playlists(limit=None)
        playlist_count = len(playlists)
    except Exception as e:
        playlist_count = f"Error: {e}"

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
            "total_requests": len(logs),
            "playlist_count": playlist_count,
            "signin_type": yt_auth.auth_type.name if hasattr(yt_auth, "auth_type") else "unknown",
            "os": platform.name(),
        },
    }

    # Add user report info if provided
    if user_description or user_contact:
        event["extra"]["user_report"] = {"timestamp": datetime.datetime.now(datetime.UTC).isoformat()}
        if user_description:
            event["extra"]["user_report"]["description"] = user_description
        if user_contact:
            event["extra"]["user_report"]["contact"] = user_contact

    # Parse DSN to get project info
    dsn = PUBLIC_SETTINGS["sentry_dsn"]
    # DSN format: https://{key}@{host}/{project_id}
    import re

    match = re.match(r"https://([^@]+)@([^/]+)/(\d+)", dsn)
    if not match:
        print("Invalid Sentry DSN")
        return None

    key, host, project_id = match.groups()

    # Read the app log file
    app_log_content = ""
    if log_file_path.exists():
        try:
            with open(log_file_path, encoding="utf-8") as f:
                app_log_content = f.read()
            print(f"Read {len(app_log_content)} bytes from log file")
        except Exception as e:
            print(f"Failed to read log file: {e}")
            app_log_content = f"Error reading log file: {e}"
    else:
        print(f"Log file not found at {log_file_path}")
        app_log_content = "Log file not found"

    # Create envelope with event and attachment
    # Envelope format: {envelope_header}\n{item_header}\n{item_payload}\n{item_header}\n{item_payload}

    # Envelope header
    envelope_header = {}

    # Event item
    event_item_header = {"type": "event"}
    event_item_payload = json.dumps(event)

    # Attachment 1: ytmusicapi logs
    ytmusic_logs_bytes = json.dumps(logs, indent=2).encode("utf-8")
    ytmusic_attachment_header = {
        "type": "attachment",
        "length": len(ytmusic_logs_bytes),
        "filename": "ytmusicapi_logs.json",
        "content_type": "application/json",
    }

    # Attachment 2: app log file
    app_log_bytes = app_log_content.encode("utf-8")
    app_log_attachment_header = {
        "type": "attachment",
        "length": len(app_log_bytes),
        "filename": log_file_path.name,
        "content_type": "text/plain",
    }

    # Build the envelope properly
    envelope_parts = [
        json.dumps(envelope_header),
        json.dumps(event_item_header),
        event_item_payload,
        json.dumps(ytmusic_attachment_header),
        ytmusic_logs_bytes.decode("utf-8"),
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
        print(f"Sending event {event_id} with attachment to Sentry...")
        response = requests.post(url, data=envelope.encode("utf-8"), headers=headers, timeout=10)
        response.raise_for_status()
        print(f"Successfully sent to Sentry! Status: {response.status_code}")
        return event_id
    except Exception as e:
        print(f"Failed to send to Sentry: {e}")
        if "response" in locals():
            print(f"Response: {response.text}")
        return None
