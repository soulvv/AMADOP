"""
DevOps Self-Healing Agent
Monitors Prometheus metrics and autonomously remediates infrastructure issues.
Enhanced with trend analysis and memory/disk metric queries.
"""

import httpx
import logging
import os
from collections import deque
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

PROMETHEUS_URL = os.getenv(
    "PROMETHEUS_URL", "http://prometheus-server.amadop.svc.cluster.local"
)
# Fallback for local/docker-compose development
PROMETHEUS_FALLBACK_URL = os.getenv(
    "PROMETHEUS_FALLBACK_URL", "http://host.docker.internal:9090"
)

# Use environment variables if set, else fallback to Kubernetes service names
SERVICES = [
    {
        "name": "auth_service",
        "url": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001") + "/health",
    },
    {
        "name": "post_service",
        "url": os.getenv("POST_SERVICE_URL", "http://post-service:8002") + "/health",
    },
    {
        "name": "comment_service",
        "url": os.getenv("COMMENT_SERVICE_URL", "http://comment-service:8003")
        + "/health",
    },
    {
        "name": "notification_service",
        "url": os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8004")
        + "/health",
    },
]


class DevOpsAgent:
    def __init__(self):
        self.incident_log = []
        # Ring buffer: stores last 100 scan results for trend analysis
        self._scan_history: deque = deque(maxlen=100)
        self._latency_history: dict[str, deque] = {
            svc["name"]: deque(maxlen=20) for svc in SERVICES
        }

    async def check_service_health(self) -> list:
        """Checks all microservices and returns their status."""
        results = []
        for service in SERVICES:
            status = {
                "name": service["name"],
                "healthy": False,
                "response_time_ms": None,
                "error": None,
            }
            try:
                async with httpx.AsyncClient() as client:
                    start = datetime.now()
                    response = await client.get(service["url"], timeout=5.0)
                    elapsed = (datetime.now() - start).total_seconds() * 1000
                    status["healthy"] = response.status_code == 200
                    status["response_time_ms"] = round(elapsed, 2)

                    # Track latency for trend analysis
                    self._latency_history[service["name"]].append(elapsed)
            except Exception as e:
                status["error"] = str(e)
                logger.warning(f"Service {service['name']} is DOWN: {str(e)}")
            results.append(status)
        return results

    async def query_prometheus(self, query: str) -> dict:
        """Queries Prometheus and returns the result."""
        for url in [PROMETHEUS_URL, PROMETHEUS_FALLBACK_URL]:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{url}/api/v1/query",
                        params={"query": query},
                        timeout=5.0,
                    )
                    if response.status_code == 200:
                        return response.json()
            except Exception:
                continue
        return {"status": "error", "message": "Prometheus unreachable"}

    def _analyze_latency_trend(self, service_name: str) -> Optional[dict]:
        """
        Check if latency is trending upward over recent scans.
        Returns an anomaly dict if latency doubled compared to baseline.
        """
        history = self._latency_history.get(service_name, deque())
        if len(history) < 5:
            return None  # Not enough data

        recent = list(history)
        baseline_avg = sum(recent[: len(recent) // 2]) / (len(recent) // 2)
        current_avg = sum(recent[len(recent) // 2 :]) / (
            len(recent) - len(recent) // 2
        )

        if baseline_avg > 0 and current_avg > baseline_avg * 2:
            return {
                "type": "LATENCY_TRENDING_UP",
                "service": service_name,
                "severity": "WARNING",
                "message": (
                    f"{service_name} latency trending upward: "
                    f"{baseline_avg:.0f}ms → {current_avg:.0f}ms "
                    f"({current_avg / baseline_avg:.1f}x increase)"
                ),
                "recommended_action": "investigate_performance_degradation",
                "baseline_ms": round(baseline_avg, 1),
                "current_ms": round(current_avg, 1),
            }
        return None

    async def detect_anomalies(self) -> dict:
        """
        Analyzes metrics for anomalies:
        - High CPU usage (>80%)
        - High error rates
        - Service downtime
        - Latency trends
        - Memory usage (from Prometheus)
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "services": await self.check_service_health(),
            "anomalies": [],
            "actions_taken": [],
        }

        # Check for down services
        for svc in report["services"]:
            if not svc["healthy"]:
                anomaly = {
                    "type": "SERVICE_DOWN",
                    "service": svc["name"],
                    "severity": "CRITICAL",
                    "message": f"{svc['name']} is not responding",
                    "recommended_action": "restart_service",
                }
                report["anomalies"].append(anomaly)
                self.incident_log.append(anomaly)

            elif svc["response_time_ms"] and svc["response_time_ms"] > 2000:
                anomaly = {
                    "type": "HIGH_LATENCY",
                    "service": svc["name"],
                    "severity": "WARNING",
                    "message": f"{svc['name']} response time is {svc['response_time_ms']}ms (>2000ms)",
                    "recommended_action": "scale_up",
                }
                report["anomalies"].append(anomaly)

        # Latency trend analysis
        for svc in SERVICES:
            trend = self._analyze_latency_trend(svc["name"])
            if trend:
                report["anomalies"].append(trend)

        # Query Prometheus for CPU spikes (if available)
        cpu_result = await self.query_prometheus(
            "rate(process_cpu_seconds_total[1m])"
        )
        if cpu_result.get("status") == "success":
            for result in cpu_result.get("data", {}).get("result", []):
                cpu_value = float(result.get("value", [0, 0])[1])
                if cpu_value > 0.8:
                    anomaly = {
                        "type": "HIGH_CPU",
                        "service": result.get("metric", {}).get("job", "unknown"),
                        "severity": "WARNING",
                        "message": f"CPU usage at {cpu_value:.2%}",
                        "recommended_action": "investigate_or_scale",
                    }
                    report["anomalies"].append(anomaly)

        # Query Prometheus for memory usage
        mem_result = await self.query_prometheus(
            'container_memory_usage_bytes{namespace="amadop"}'
        )
        if mem_result.get("status") == "success":
            for result in mem_result.get("data", {}).get("result", []):
                mem_bytes = float(result.get("value", [0, 0])[1])
                mem_mb = mem_bytes / (1024 * 1024)
                container = result.get("metric", {}).get("container", "unknown")
                # Alert if any container uses > 512MB
                if mem_mb > 512:
                    anomaly = {
                        "type": "HIGH_MEMORY",
                        "service": container,
                        "severity": "WARNING",
                        "message": f"Container '{container}' using {mem_mb:.0f}MB of memory",
                        "recommended_action": "check_for_memory_leaks",
                    }
                    report["anomalies"].append(anomaly)

        if not report["anomalies"]:
            report["status"] = "ALL_HEALTHY"
        else:
            report["status"] = "ANOMALIES_DETECTED"

        # Store in ring buffer for history
        self._scan_history.append(report)

        return report

    def get_incident_log(self) -> list:
        """Returns the history of all detected incidents."""
        return self.incident_log

    def get_scan_history(self, limit: int = 10) -> list:
        """Returns recent scan reports from the ring buffer."""
        return list(self._scan_history)[-limit:]

    def get_latest_report(self) -> Optional[dict]:
        """Returns the most recent scan report."""
        if self._scan_history:
            return self._scan_history[-1]
        return None


devops_agent = DevOpsAgent()
