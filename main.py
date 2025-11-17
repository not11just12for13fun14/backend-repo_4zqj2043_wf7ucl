from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from datetime import datetime, timedelta

from database import db, create_document, get_documents  # noqa: F401  (imported for readiness)
import os

app = FastAPI(title="KPI Dashboard API", version="1.0.0")

# CORS
frontend_url = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "KPI Dashboard API is running", "status": "ok", "timestamp": datetime.utcnow()}


@app.get("/test")
def test_database():
    try:
        # Try to list collections to validate connectivity
        collections = []
        if db is not None:
            collections = db.list_collection_names()
            conn_status = "connected"
        else:
            conn_status = "not_configured"

        return {
            "backend": "fastapi",
            "database": "mongodb",
            "database_url": os.getenv("DATABASE_URL", "not set"),
            "database_name": os.getenv("DATABASE_NAME", "not set"),
            "connection_status": conn_status,
            "collections": collections,
        }
    except Exception as e:
        return {
            "backend": "fastapi",
            "database": "mongodb",
            "connection_status": "error",
            "error": str(e),
        }


@app.get("/kpis")
def get_kpis() -> Dict[str, Any]:
    """Return example KPI metrics and a simple 30-day timeseries.
    This is static/demo data suitable for a working dashboard UI.
    """
    now = datetime.utcnow()
    days = [now - timedelta(days=i) for i in range(29, -1, -1)]

    def series(base: float, variance: float) -> List[Dict[str, Any]]:
        pts = []
        value = base
        for d in days:
            # simple noisy walk
            value = max(0, value + (variance * 0.5) - (variance))
            pts.append({"date": d.strftime("%Y-%m-%d"), "value": round(value, 2)})
        return pts

    data = {
        "summary": [
            {"label": "Revenue", "value": 128430, "delta": 8.4, "format": "currency"},
            {"label": "Active Users", "value": 5421, "delta": 3.1, "format": "number"},
            {"label": "Conversion", "value": 4.7, "delta": -0.6, "format": "percent"},
            {"label": "NPS", "value": 62, "delta": 2.0, "format": "number"},
        ],
        "timeseries": {
            "revenue": series(4000, 450),
            "users": series(120, 12),
            "conversion": series(5.2, 0.4),
        },
        "generated_at": now.isoformat() + "Z",
    }
    return data
