"""
Background Scheduler — Autonomous Agent Loop
Runs DevOps and Security agents on a configurable interval,
collects metrics, detects threats, and pushes notifications.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Optional

from prometheus_client import Counter, Gauge

logger = logging.getLogger(__name__)

# ─── Custom Prometheus Metrics ───────────────────────────────────────────────

SCAN_COUNTER = Counter(
    "amadop_agent_scan_total",
    "Total number of background agent scan cycles completed",
)
ANOMALIES_GAUGE = Gauge(
    "amadop_agent_anomalies_detected",
    "Number of anomalies detected in the last scan cycle",
)
THREATS_GAUGE = Gauge(
    "amadop_agent_threats_detected",
    "Number of security threats detected in the last scan cycle",
)
LAST_SCAN_TIMESTAMP = Gauge(
    "amadop_agent_last_scan_timestamp",
    "Unix timestamp of the last completed scan cycle",
)
AGENT_RUNNING = Gauge(
    "amadop_agent_running",
    "Whether the background agent loop is currently running (1=yes, 0=no)",
)


class BackgroundScheduler:
    """
    Async background loop that periodically runs the DevOps and Security agents.
    Designed to be started/stopped via FastAPI lifespan.
    """

    def __init__(self, interval_seconds: int = 30, admin_user_ids: list = None):
        self.interval = interval_seconds
        self.admin_user_ids = admin_user_ids or [1]
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self.scan_count = 0
        self.start_time: Optional[float] = None
        self.last_devops_report: Optional[dict] = None
        self.last_security_report: Optional[dict] = None

    # ─── Lifecycle ───────────────────────────────────────────────────────

    async def start(self):
        """Start the background loop."""
        if self._running:
            logger.warning("Scheduler already running")
            return

        self._running = True
        self.start_time = time.time()
        AGENT_RUNNING.set(1)
        self._task = asyncio.create_task(self._loop())
        logger.info(
            f"🤖 Background agent scheduler started (interval={self.interval}s)"
        )

    async def stop(self):
        """Gracefully stop the background loop."""
        self._running = False
        AGENT_RUNNING.set(0)
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("🛑 Background agent scheduler stopped")

    # ─── Main Loop ───────────────────────────────────────────────────────

    async def _loop(self):
        """The core scan loop — runs forever until stopped."""
        # Import agents here to avoid circular imports
        from agents.devops_agent import devops_agent
        from agents.security_agent import security_agent

        # Wait a few seconds on startup for services to initialize
        await asyncio.sleep(5)

        while self._running:
            try:
                cycle_start = time.time()
                logger.info(f"━━━ Agent scan cycle #{self.scan_count + 1} ━━━")

                # ── Phase 1: DevOps Health & Anomaly Scan ────────────────
                try:
                    devops_report = await devops_agent.detect_anomalies()
                    self.last_devops_report = devops_report
                    anomaly_count = len(devops_report.get("anomalies", []))
                    ANOMALIES_GAUGE.set(anomaly_count)

                    if anomaly_count > 0:
                        logger.warning(
                            f"  ⚠ DevOps: {anomaly_count} anomalies detected"
                        )
                        for a in devops_report["anomalies"]:
                            logger.warning(
                                f"    → [{a['severity']}] {a['type']}: {a['message']}"
                            )
                    else:
                        logger.info("  ✓ DevOps: All services healthy")
                except Exception as e:
                    logger.error(f"  ✗ DevOps scan failed: {e}")
                    ANOMALIES_GAUGE.set(0)

                # ── Phase 2: Security Threat Scan ────────────────────────
                try:
                    security_report = await security_agent.scan(
                        admin_user_ids=self.admin_user_ids
                    )
                    self.last_security_report = security_report
                    threat_count = security_report.get("threat_count", 0)
                    THREATS_GAUGE.set(threat_count)

                    if threat_count > 0:
                        logger.warning(
                            f"  🚨 Security: {threat_count} threats detected"
                        )
                        for t in security_report.get("active_threats", []):
                            logger.warning(
                                f"    → [{t['severity']}] {t['type']}: {t['message']}"
                            )
                    else:
                        status = security_report.get("status", "UNKNOWN")
                        if status == "PROMETHEUS_UNREACHABLE":
                            logger.info(
                                "  ◌ Security: Prometheus unreachable — skipped threat eval"
                            )
                        else:
                            logger.info("  ✓ Security: No active threats")
                except Exception as e:
                    logger.error(f"  ✗ Security scan failed: {e}")
                    THREATS_GAUGE.set(0)

                # ── Bookkeeping ──────────────────────────────────────────
                self.scan_count += 1
                SCAN_COUNTER.inc()
                LAST_SCAN_TIMESTAMP.set(time.time())

                elapsed = time.time() - cycle_start
                logger.info(f"  Scan cycle completed in {elapsed:.2f}s")

            except Exception as e:
                logger.error(f"Unexpected error in agent loop: {e}", exc_info=True)

            # Sleep until next cycle
            await asyncio.sleep(self.interval)

    # ─── Manual Trigger ──────────────────────────────────────────────────

    async def trigger_scan(self) -> dict:
        """Force an immediate scan cycle outside the regular interval."""
        from agents.devops_agent import devops_agent
        from agents.security_agent import security_agent

        logger.info("Manual scan triggered")

        devops_report = await devops_agent.detect_anomalies()
        self.last_devops_report = devops_report

        security_report = await security_agent.scan(
            admin_user_ids=self.admin_user_ids
        )
        self.last_security_report = security_report

        self.scan_count += 1
        SCAN_COUNTER.inc()
        LAST_SCAN_TIMESTAMP.set(time.time())

        return {
            "devops": devops_report,
            "security": security_report,
            "triggered_at": datetime.utcnow().isoformat(),
        }

    # ─── Status ──────────────────────────────────────────────────────────

    def get_status(self) -> dict:
        uptime = None
        if self.start_time:
            uptime = round(time.time() - self.start_time, 1)

        return {
            "running": self._running,
            "scan_count": self.scan_count,
            "interval_seconds": self.interval,
            "uptime_seconds": uptime,
            "admin_user_ids": self.admin_user_ids,
            "last_devops_status": (
                self.last_devops_report.get("status") if self.last_devops_report else None
            ),
            "last_security_status": (
                self.last_security_report.get("status")
                if self.last_security_report
                else None
            ),
        }
