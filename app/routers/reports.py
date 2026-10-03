# app/routers/reports.py

"""Report and notification routes with simulated background processing.

Reports and notifications are stored in memory, so they reset
whenever the server restarts.
"""

import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

router = APIRouter(tags=["reports"])  # prefix is added in main.py

# In-memory "databases"
reports_db: dict[str, dict] = {}
notification_log: list[dict] = []


class ReportRequest(BaseModel):
    """Body for POST /reports."""
    report_type: str
    rows: int


class NotificationRequest(BaseModel):
    """Body for POST /reports/notifications."""
    recipient: str
    message: str


# ---------- Background task functions ----------

def generate_report(report_id: str, report_type: str, rows: int) -> None:
    """Simulate generating a report in the background.

    Moves the report's status from "pending" to "processing" to
    "complete", pausing with time.sleep() between each stage.

    Args:
        report_id: ID of the report in reports_db.
        report_type: Kind of report being generated (e.g. "sales").
        rows: Number of rows the finished report contains.
    """
    report = reports_db.setdefault(report_id, {"id": report_id, "type": report_type})
    report["status"] = "pending"
    time.sleep(1)

    report["status"] = "processing"
    time.sleep(1)  # pretend we're crunching data

    report["status"] = "complete"
    report["result"] = {
        "summary": f"{report_type} report with {rows} rows",
        "rows": rows,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


def send_notification(recipient: str, message: str) -> None:
    """Simulate sending a notification and record it in the log.

    Args:
        recipient: Who the notification is sent to (e.g. an email address).
        message: The notification text.
    """
    time.sleep(2)  # pretend we're talking to an email/SMS service

    notification_log.append({
        "recipient": recipient,
        "message": message,
        "sent_at": datetime.now(timezone.utc).isoformat(),
    })


# ---------- Endpoints ----------

@router.post("", status_code=202)
def create_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """Create a report and generate it in the background."""
    report_id = str(uuid.uuid4())
    reports_db[report_id] = {
        "id": report_id,
        "type": request.report_type,
        "status": "pending",
    }

    background_tasks.add_task(generate_report, report_id, request.report_type, request.rows)
    return {"report_id": report_id, "status": "pending"}


@router.post("/notifications", status_code=202)
def create_notification(request: NotificationRequest, background_tasks: BackgroundTasks):
    """Send a notification in the background."""
    background_tasks.add_task(send_notification, request.recipient, request.message)
    return {"status": "queued", "recipient": request.recipient}


@router.get("/notifications/log")
def get_notification_log():
    """Return every notification that has been sent so far."""
    return {"count": len(notification_log), "notifications": notification_log}


@router.get("/{report_id}")
def get_report(report_id: str):
    """Return a report's current status, plus its result once complete."""
    report = reports_db.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    response = {"report_id": report_id, "status": report["status"]}
    if report["status"] == "complete":
        response["result"] = report["result"]
    return response