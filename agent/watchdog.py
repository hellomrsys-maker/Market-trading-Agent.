"""
agent/watchdog.py
==================
OptionAlpha Agent — Autonomous Process Health Watchdog

Monitors local REST dashboard health endpoint (/api/health).
If the main agent crashes, deadlocks, or stops responding for 3 consecutive intervals,
the watchdog automatically restarts the agent process.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from loguru import logger

from agent.alerting import AlertDispatcher

ROOT = Path(__file__).resolve().parent.parent
HEALTH_URL = "http://127.0.0.1:8080/api/health"
POLL_INTERVAL_S = 30
MAX_FAILURES = 3


class AgentWatchdog:
    """
    Independent health monitoring sidecar daemon.
    """

    def __init__(self, agent_cmd: Optional[list] = None):
        python_bin = sys.executable
        self.agent_cmd = agent_cmd or [python_bin, str(ROOT / "run_agent.py")]
        self.alerts = AlertDispatcher()
        self.failures = 0
        self.process: Optional[subprocess.Popen] = None

    def start_agent(self) -> None:
        """Launches agent in a managed child subprocess."""
        if self.process and self.process.poll() is None:
            logger.info("Agent process already active (PID: {})", self.process.pid)
            return

        logger.info("Watchdog: Starting OptionAlpha Agent process...")
        self.process = subprocess.Popen(
            self.agent_cmd,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        self.alerts.send_alert("Watchdog", f"OptionAlpha Agent started (PID {self.process.pid})", severity="SUCCESS")

    def restart_agent(self) -> None:
        """Kills unresponsive agent and restarts it."""
        logger.warning("Watchdog: Restarting unresponsive agent...")
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5.0)
            except Exception:
                self.process.kill()
        self.start_agent()
        self.failures = 0

    def check_health(self) -> bool:
        """Hits /api/health endpoint."""
        try:
            req = urllib.request.Request(HEALTH_URL, headers={"User-Agent": "OptionAlpha-Watchdog/1.0"})
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def run_loop(self) -> None:
        """Continuous supervision loop."""
        logger.info("OptionAlpha Watchdog active on {}", HEALTH_URL)
        self.start_agent()

        try:
            while True:
                time.sleep(POLL_INTERVAL_S)
                is_healthy = self.check_health()

                if is_healthy:
                    if self.failures > 0:
                        logger.info("Agent health restored")
                    self.failures = 0
                else:
                    self.failures += 1
                    logger.warning("Health check failed ({}/{})", self.failures, MAX_FAILURES)
                    if self.failures >= MAX_FAILURES:
                        self.alerts.send_alert(
                            "Agent Unresponsive",
                            f"Agent failed {MAX_FAILURES} consecutive health checks. Restarting now.",
                            severity="CRITICAL"
                        )
                        self.restart_agent()
        except KeyboardInterrupt:
            logger.info("Watchdog stopping...")
            if self.process:
                self.process.terminate()


if __name__ == "__main__":
    watchdog = AgentWatchdog()
    watchdog.run_loop()
