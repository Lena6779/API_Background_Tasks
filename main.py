"""Entry point for the API_Background_Tasks app.

Creates the FastAPI application and registers the routers.
Run from the project root with: uvicorn main:app --reload
"""

from fastapi import FastAPI

from app.routers import reports

app = FastAPI(
    title="API Background Tasks",
    description="Practice API that simulates report generation and notifications with background tasks.",
)

app.include_router(reports.router, prefix="/reports")

@app.get("/")
def root():
    """Health check: confirm the API is running."""
    return {"message": "API Background Tasks is running"}