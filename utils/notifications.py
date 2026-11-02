"""Background task helpers that record activity and notifications in log files."""

import os
import time
from datetime import datetime, timezone

ACTIVITY_LOG_FILE = "activity_log.txt"
NOTIFICATION_LOG_FILE = "notification_log.txt"
NOTIFICATION_DELAY = 2  # In seconds


def _write_log(file_name: str, entry: str) -> None:
    """Append one timestamped line to a log file."""
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(file_name, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {entry}\n")


def log_activity(user_id: int, action: str) -> None:
    """Record what a user did in activity_log.txt."""
    _write_log(ACTIVITY_LOG_FILE, f"user_id={user_id} action={action}")


def send_notification(recipient: str, message: str) -> None:
    """Simulate sending a notification, then record it in notification_log.txt."""
    time.sleep(NOTIFICATION_DELAY)  # Pretend we're talking to an email/SMS service
    _write_log(NOTIFICATION_LOG_FILE, f"to={recipient} message={message}")


def read_notification_log() -> list[str]:
    """Return each line of notification_log.txt, or an empty list if it doesn't exist yet."""
    if not os.path.exists(NOTIFICATION_LOG_FILE):
        return []

    with open(NOTIFICATION_LOG_FILE, encoding="utf-8") as log_file:
        return [line.strip() for line in log_file if line.strip()]
