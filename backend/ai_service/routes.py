from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.content_agent import content_agent
from agents.devops_agent import devops_agent
from agents.security_agent import security_agent

router = APIRouter()


class SummarizeRequest(BaseModel):
    content: str


class ModerateRequest(BaseModel):
    text: str


# ─── Content Intelligence Endpoints ──────────────────────────────────────────

@router.post("/summarize")
async def summarize(request: SummarizeRequest):
    summary = content_agent.summarize_post(request.content)
    return {"summary": summary}


@router.post("/moderate")
async def moderate(request: ModerateRequest):
    result = content_agent.moderate_content(request.text)
    return result


# ─── DevOps Agent Endpoints ──────────────────────────────────────────────────

@router.get("/health")
async def basic_health():
    """Simple health check for Kubernetes liveness probe."""
    return {"status": "ok"}


@router.get("/health-check")
async def devops_health_check():
    """Run a health check across all microservices."""
    results = await devops_agent.check_service_health()
    return {"services": results}


@router.get("/anomalies")
async def detect_anomalies():
    """Detect anomalies: service downtime, high latency, CPU spikes."""
    report = await devops_agent.detect_anomalies()
    return report


@router.get("/incidents")
async def get_incidents():
    """Return the history of all detected incidents."""
    return {"incidents": devops_agent.get_incident_log()}


# ─── Security Agent Endpoints ────────────────────────────────────────────────

@router.get("/security/threats")
async def get_security_threats():
    """
    Run an on-demand security threat assessment.
    Queries Prometheus for brute-force, DDoS, error storms, latency,
    crash loops, and memory pressure indicators.
    """
    report = await security_agent.scan()
    return report


@router.get("/security/history")
async def get_security_history():
    """Return the last 50 security alerts from the agent's memory."""
    return {
        "alerts": security_agent.get_alert_history(limit=50),
        "stats": security_agent.get_stats(),
    }


# ─── Background Agent Control Endpoints ──────────────────────────────────────

@router.get("/agent/status")
async def get_agent_status():
    """
    Get the current status of the background monitoring agent:
    running state, scan count, uptime, last scan results.
    """
    # Import scheduler from main to avoid circular import
    from main import scheduler

    status = scheduler.get_status()
    status["security_stats"] = security_agent.get_stats()
    status["devops_history_size"] = len(devops_agent._scan_history)
    return status


@router.post("/agent/trigger")
async def trigger_agent_scan():
    """
    Force an immediate scan cycle outside the regular 30s interval.
    Returns the full DevOps + Security report from the triggered scan.
    """
    from main import scheduler

    if not scheduler._running:
        raise HTTPException(
            status_code=503,
            detail="Background agent is not running. Start the service first.",
        )

    result = await scheduler.trigger_scan()
    return result
