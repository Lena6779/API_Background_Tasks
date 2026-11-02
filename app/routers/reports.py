# app/routers/reports.py

"""Report and notification routes with simulated background processing.

Reports are stored in memory, so they reset whenever the server restarts.
Activity and notifications are written to log files by utils/notifications.py.
"""

import time
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from utils.notifications import log_activity, read_notification_log, send_notification

router = APIRouter(tags=["reports"])  # prefix is added in main.py

# In-memory "database"
reports_db: dict[str, dict] = {}


class ReportRequest(BaseModel):
    """Body for POST /reports."""
    report_type: str
    rows: int
    user_id: int
    recipient: str


class NotificationRequest(BaseModel):
    """Body for POST /reports/notifications."""
    user_id: int
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
    report = reports_db[report_id]
    time.sleep(1)

    report["status"] = "processing"
    time.sleep(1)  # pretend we're crunching data

    report["result"] = {
        "summary": f"{report_type} report with {rows} rows",
        "rows": rows,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    report["status"] = "complete"


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

    background_tasks.add_task(log_activity, request.user_id, f"created report {report_id}")
    background_tasks.add_task(generate_report, report_id, request.report_type, request.rows)
    background_tasks.add_task(
        send_notification, request.recipient, f"Your {request.report_type} report is ready"
    )
    return {"report_id": report_id, "status": "pending"}


@router.post("/notifications", status_code=202)
def create_notification(request: NotificationRequest, background_tasks: BackgroundTasks):
    """Log the request and send a notification in the background."""
    background_tasks.add_task(
        log_activity, request.user_id, f"requested notification to {request.recipient}"
    )
    background_tasks.add_task(send_notification, request.recipient, request.message)
    return {"status": "queued", "recipient": request.recipient}


@router.get("/notifications/log")
def get_notification_log():
    """Return every notification that has been sent so far."""
    notifications = read_notification_log()
    return {"count": len(notifications), "notifications": notifications}


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


@router.delete("/{report_id}")
def delete_report(report_id: str, user_id: int, background_tasks: BackgroundTasks):
    """Delete a report and log the activity in the background."""
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="Report not found")

    del reports_db[report_id]
    background_tasks.add_task(log_activity, user_id, f"deleted report {report_id}")
    return {"message": "Report deleted", "report_id": report_id}
