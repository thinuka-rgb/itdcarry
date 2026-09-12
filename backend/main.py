import hashlib
import logging
from datetime import UTC, datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.settings import get_settings
from backend.daytona_runner import run_profiles
from backend.domain import Verdict
from backend.neo4j_store import Neo4jStore
from backend.schemas import HandoffRequest, HandoffResponse, VariantRecord


settings = get_settings()
logger = logging.getLogger(__name__)
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


@app.post(
    "/api/v1/cases/{case_id}/handoff-tests",
    response_model=HandoffResponse,
)
def handoff_test(case_id: str, request: HandoffRequest) -> HandoffResponse:
    if case_id != "AML-DEMO-001" or request.fixture_id != "FLT3-ITD-DEMO-001":
        raise HTTPException(status_code=404, detail="Unknown fictional case or fixture")
    if not settings.daytona_configured or not settings.neo4j_configured:
        raise HTTPException(status_code=503, detail="Required integration is not configured")
    try:
        runs, manifest = run_profiles(request.profiles)
        target_profile = "changed" if "changed" in request.profiles else request.profiles[0]
        target_run = next(run for run in runs if run.profile == target_profile)
        variant_id = "FLT3-ITD-DEMO-001"
        followup_id = "AML-DEMO-001-FOLLOWUP-001"
        store = Neo4jStore(
            settings.neo4j_uri,
            settings.neo4j_username,
            settings.neo4j_password,
            settings.neo4j_database,
        )
        try:
            store.ensure_constraints()
            for run in runs:
                store.write_provenance(
                    {
                        "case_id": case_id,
                        "variant_id": variant_id,
                        "gene": "FLT3",
                        "position": manifest["itd_position"],
                        "length_bp": manifest["itd_length_bp"],
                        "sequence_sha256": hashlib.sha256(manifest["itd_sequence"].encode()).hexdigest(),
                        "followup_id": followup_id,
                        "pipeline_id": f"getitd-1.5.17-{run.profile}",
                        "caller": run.caller,
                        "caller_version": run.caller_version,
                        "config_sha256": run.config_sha256,
                        "challenge_id": run.run_id,
                        "fixture_id": request.fixture_id,
                        "fixture_sha256": run.fixture_sha256,
                        "sandbox_id": run.sandbox_id,
                        "status": run.status,
                        "test_vaf": manifest["intended_variant_fragment_fraction"],
                        "completed_at": datetime.now(UTC).isoformat(),
                        "result_id": f"{run.run_id}-result",
                        "exact_recovery": run.exact_recovery,
                        "error": run.error,
                    }
                )
            verdict = store.get_verdict(
                case_id,
                followup_id,
                f"getitd-1.5.17-{target_profile}",
                variant_id,
                target_run.run_id,
            )
        finally:
            store.close()
        return HandoffResponse(
            case_id=case_id,
            fixture_id=request.fixture_id,
            synthetic=True,
            variant=VariantRecord(
                position=manifest["itd_position"],
                length_bp=manifest["itd_length_bp"],
                sequence=manifest["itd_sequence"],
                test_vaf=manifest["intended_variant_fragment_fraction"],
            ),
            runs=runs,
            verdict=verdict,
            limitations=manifest["limitations"],
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Handoff execution failed")
        raise HTTPException(
            status_code=502,
            detail={
                "status": "failed",
                "stage": "handoff_execution",
                "verdict": Verdict.NO_CONCLUSION,
                "message": "The isolated validation run could not be completed.",
            },
        ) from exc


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
