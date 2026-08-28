from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.models import base
from app.api import auth, teams, tickets, ws, analytics, users, sla

app = FastAPI(title="Smart Ticket Triage System", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ws.router)
app.include_router(auth.router)
app.include_router(teams.router)
app.include_router(tickets.router)
app.include_router(analytics.router)
app.include_router(users.router)
app.include_router(sla.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT
    }