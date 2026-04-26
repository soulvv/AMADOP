"""
Security Agent — Autonomous Threat Detection
Runs in background, queries Prometheus metrics, detects attacks and anomalies,
and pushes critical alerts to the notification service.
"""

import asyncio
import httpx
import logging
import os
from collections import deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)

PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL", "http://prometheus-server.amadop.svc.cluster.local"
)
PROMETHEUS_FALLBACK_URL = os.getenv(
    "PROMETHEUS_FALLBACK_URL", "http://host.docker.internal:9090"
)
NOTIFICATION_SERVICE_URL = os.getenv(
    "NOTIFICATION_SERVICE_URL", "http://notification-service:8004"
)


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class ThreatType(str, Enum):
    BRUTE_FORCE = "BRUTE_FORCE_LOGIN"
    DDOS = "DDOS_TRAFFIC_SPIKE"
    ERROR_STORM = "ERROR_STORM"
    HIGH_LATENCY = "UNUSUAL_LATENCY"
    CRASH_LOOP = "POD_CRASH_LOOP"
    MEMORY_PRESSURE = "MEMORY_PRESSURE"
    SERVICE_DOWN = "SERVICE_DOWN"


@dataclass
class Alert:
    type: str
    severity: str
    service: str
    message: str
    recommended_action: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    resolved: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


# ─── Threat Detection Rules ─────────────────────────────────────────────────

THREAT_RULES = [
    {
        "name": ThreatType.BRUTE_FORCE,
        "query": 'sum(rate(http_requests_total{handler="/login",status="401"}[5m]))',
        "threshold": 0.15,  # > 0.15 req/s (≈ 9 per minute)
        "severity": Severity.CRITICAL,
        "service": "auth_service",
        "message": "Potential brute-force attack detected on login endpoint — elevated 401 rate",
        "action": "Block source IPs, enforce rate-limiting, enable CAPTCHA",
    },
    {
        "name": ThreatType.DDOS,
        "query": "sum(rate(http_requests_total[1m]))",
        "threshold": 200.0,
        "severity": Severity.CRITICAL,
        "service": "all",
        "message": "DDoS-level traffic spike detected — request rate exceeds 200 req/s",
        "action": "Enable WAF rules, scale replicas, engage upstream DDoS protection",
    },
    {
        "name": ThreatType.ERROR_STORM,
        "query": 'sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))',
        "threshold": 0.20,
        "severity": Severity.WARNING,
        "service": "all",
        "message": "Error storm — over 20% of requests returning 5xx errors",
        "action": "Check service logs, roll back recent deployments, investigate root cause",
    },
    {
        "name": ThreatType.HIGH_LATENCY,
        "query": "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))",
        "threshold": 5.0,
        "severity": Severity.WARNING,
        "service": "all",
        "message": "Unusual latency — p99 response time exceeds 5 seconds",
        "action": "Check database performance, review slow queries, scale horizontally",
    },
    {
        "name": ThreatType.CRASH_LOOP,
        "query": 'sum(increase(kube_pod_container_status_restarts_total{namespace="amadop"}[10m]))',
        "threshold": 5.0,
        "severity": Severity.CRITICAL,
        "service": "kubernetes",
        "message": "Pod crash loop detected — containers restarting repeatedly",
        "action": "Check pod logs (kubectl logs), fix OOMKilled or CrashLoopBackOff",
    },
    {
        "name": ThreatType.MEMORY_PRESSURE,
        "query": 'max(container_memory_usage_bytes{namespace="amadop"} / container_spec_memory_limit_bytes{namespace="amadop"})',
        "threshold": 0.90,
        "severity": Severity.WARNING,
        "service": "kubernetes",
        "message": "Memory pressure — a container is using over 90% of its memory limit",
        "action": "Increase memory limits, investigate memory leaks, add HPA",
    },
]


class SecurityAgent:
    """Autonomous security agent that detects threats from Prometheus metrics."""

    def __init__(self, cooldown_seconds: int = 300):
        self.alert_history: deque = deque(maxlen=200)
        self.cooldown_seconds = cooldown_seconds
        self._cooldown_tracker: dict[str, datetime] = {}
        self.last_scan_time: Optional[str] = None
        self.total_threats_detected: int = 0

    # ─── Prometheus Query ────────────────────────────────────────────────

    async def _query_prometheus(self, query: str) -> Optional[float]:
        """Execute a PromQL query and return the scalar result."""
        for url in [PROMETHEUS_URL, PROMETHEUS_FALLBACK_URL]:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(
                        f"{url}/api/v1/query", params={"query": query}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("status") == "success":
                            results = data.get("data", {}).get("result", [])
                            if results:
                                value = float(results[0].get("value", [0, 0])[1])
                                return value
                        return None
            except Exception as e:
                logger.debug(f"Prometheus query failed at {url}: {e}")
                continue
        return None

    # ─── Cooldown Logic ──────────────────────────────────────────────────

    def _is_on_cooldown(self, threat_type: str) -> bool:
        """Check if we recently alerted for this threat type."""
        last_time = self._cooldown_tracker.get(threat_type)
        if last_time is None:
            return False
        return (datetime.utcnow() - last_time).total_seconds() < self.cooldown_seconds

    def _mark_alerted(self, threat_type: str):
        self._cooldown_tracker[threat_type] = datetime.utcnow()

    # ─── Notification Push ───────────────────────────────────────────────

    async def _push_notification(self, alert: Alert, admin_user_ids: List[int]):
        """Send a notification to admin users through the notification service."""
        for user_id in admin_user_ids:
            try:
                payload = {
                    "user_id": user_id,
                    "message": f"🚨 [{alert.severity}] {alert.type}: {alert.message}",
                }
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.post(
                        f"{NOTIFICATION_SERVICE_URL}/notifications", json=payload
                    )
                    if resp.status_code in (200, 201):
                        logger.info(
                            f"Security alert sent to user {user_id}: {alert.type}"
                        )
                    else:
                        logger.warning(
                            f"Failed to notify user {user_id}: {resp.status_code}"
                        )
            except Exception as e:
                logger.error(f"Notification push failed for user {user_id}: {e}")

    # ─── Main Scan ───────────────────────────────────────────────────────

    async def scan(self, admin_user_ids: List[int] = None) -> dict:
        """
        Run all threat detection rules against Prometheus.
        Returns a threat report with any active alerts.
        """
        if admin_user_ids is None:
            admin_user_ids = [1]

        scan_time = datetime.utcnow().isoformat()
        self.last_scan_time = scan_time

        active_threats: List[dict] = []
        prometheus_reachable = False

        for rule in THREAT_RULES:
            value = await self._query_prometheus(rule["query"])
            if value is not None:
                prometheus_reachable = True

                if value > rule["threshold"]:
                    alert = Alert(
                        type=rule["name"].value,
                        severity=rule["severity"].value,
                        service=rule["service"],
                        message=f"{rule['message']} (current: {value:.4f}, threshold: {rule['threshold']})",
                        recommended_action=rule["action"],
                    )
                    active_threats.append(alert.to_dict())
                    self.alert_history.append(alert.to_dict())
                    self.total_threats_detected += 1

                    # Push critical alerts (with cooldown)
                    if (
                        alert.severity == Severity.CRITICAL.value
                        and not self._is_on_cooldown(alert.type)
                    ):
                        await self._push_notification(alert, admin_user_ids)
                        self._mark_alerted(alert.type)

                    logger.warning(
                        f"THREAT DETECTED: {alert.type} | {alert.service} | value={value:.4f}"
                    )

        report = {
            "timestamp": scan_time,
            "prometheus_reachable": prometheus_reachable,
            "active_threats": active_threats,
            "threat_count": len(active_threats),
            "total_historical_threats": self.total_threats_detected,
            "status": "THREATS_DETECTED" if active_threats else "ALL_CLEAR",
        }

        if not prometheus_reachable:
            report["status"] = "PROMETHEUS_UNREACHABLE"
            report["note"] = "Cannot evaluate threats — Prometheus is not reachable"

        return report

    # ─── Accessors ───────────────────────────────────────────────────────

    def get_alert_history(self, limit: int = 50) -> List[dict]:
        """Return the most recent alerts."""
        return list(self.alert_history)[-limit:]

    def get_stats(self) -> dict:
        return {
            "total_threats_detected": self.total_threats_detected,
            "alert_history_size": len(self.alert_history),
            "last_scan_time": self.last_scan_time,
            "cooldown_seconds": self.cooldown_seconds,
            "active_cooldowns": {
                k: v.isoformat() for k, v in self._cooldown_tracker.items()
            },
        }


security_agent = SecurityAgent()
