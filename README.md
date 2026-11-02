# API Background Tasks

A FastAPI practice project that uses background tasks to simulate report generation and notifications. Each `POST` and `DELETE` endpoint responds right away, while logging and other slow work continue after the response is sent.

## Features

- Creates reports that move through `pending`, `processing`, and `complete`
- Sends simulated notifications with a 2-second delay
- Writes timestamped user activity to `activity_log.txt`
- Writes timestamped notifications to `notification_log.txt`
- Deletes reports and logs the deletion in the background

## Project structure

```text
API_Background_Tasks/
├── app/
│   └── routers/
│       └── reports.py        # Report and notification endpoints
├── utils/
│   └── notifications.py      # log_activity() and send_notification()
├── activity_log.txt          # Created when activity is logged
├── notification_log.txt      # Created when a notification is sent
├── main.py                   # Creates the app and registers the router
└── requirements.txt
```

## Setup

Run these commands in PowerShell from the project root:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Open the interactive docs at <http://127.0.0.1:8000/docs>.

## Endpoints

| Method | Path | Description | Background work |
|---|---|---|---|
| `GET` | `/` | Confirm the API is running | None |
| `POST` | `/reports` | Create a report | Log activity, generate the report, send a notification |
| `GET` | `/reports/{report_id}` | Get a report's status, plus its result when complete | None |
| `DELETE` | `/reports/{report_id}?user_id=1` | Delete a report | Log activity |
| `POST` | `/reports/notifications` | Send a notification | Log activity, send the notification |
| `GET` | `/reports/notifications/log` | List the notifications in `notification_log.txt` | None |

### Example request bodies

`POST /reports`

```json
{
  "report_type": "sales",
  "rows": 100,
  "user_id": 1,
  "recipient": "lena@example.com"
}
```

`POST /reports/notifications`

```json
{
  "user_id": 1,
  "recipient": "lena@example.com",
  "message": "Your report is ready."
}
```

## Log files

The app creates both log files in the folder where the server is started. Timestamps are in UTC.

`activity_log.txt`

```text
[2026-11-02T21:44:05+00:00] user_id=1 action=created report c4b0c12b-08d1-436c-89da-e0c29a13d063
[2026-11-02T21:46:50+00:00] user_id=1 action=deleted report c4b0c12b-08d1-436c-89da-e0c29a13d063
```

`notification_log.txt`

```text
[2026-11-02T21:44:09+00:00] to=lena@example.com message=Your sales report is ready
```

## Verifying the background tasks

With the server running, use a second PowerShell window to time a request:

```powershell
Measure-Command { Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/reports -ContentType "application/json" -Body '{"report_type":"sales","rows":100,"user_id":1,"recipient":"lena@example.com"}' } | Select-Object TotalSeconds
```

The response returns well before the background work finishes. The report takes about 2 seconds and the notification about 2 more, so the entry appears in `notification_log.txt` about 4 seconds after the request.

## Notes

Reports are stored in memory, so they are cleared when the server restarts. The log files are kept, and new entries are added to the end of each file.
