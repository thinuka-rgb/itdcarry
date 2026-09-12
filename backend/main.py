from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.settings import get_settings


settings = get_settings()
app = FastAPI(
    title="ITDCarry API",
    version="0.1.0",
    description="Non-clinical synthetic FLT3-ITD observability proof of concept",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "itdcarry-api",
        "integrations": {
            "daytona_configured": settings.daytona_configured,
            "neo4j_configured": settings.neo4j_configured,
        },
        "clinical_use": False,
    }

