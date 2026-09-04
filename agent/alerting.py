"""
agent/alerting.py
==================
OptionAlpha Agent — Multi-Channel Alert & Notification Dispatcher

Sends real-time alerts to Discord/Slack webhooks, email, and console logs upon:
  1. Circuit breaker trips (Daily loss limit, VIX breach, portfolio delta)
  2. Order execution and profit-taking events
  3. Reconciled position anomalies
  4. Automatic system watchdog recoveries
"""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime
from typing import Dict, Optional
from loguru import logger


class AlertDispatcher:
    """
    Asynchronous and synchronous webhook alert dispatcher.
    """

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.environ.get("ALERT_WEBHOOK_URL", "")

    def send_alert(
        self,
        title: str,
        message: str,
        severity: str = "INFO",  # "INFO", "WARNING", "CRITICAL", "SUCCESS"
        details: Optional[Dict] = None,
    ) -> bool:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")
        level_map = {
            "INFO": "[INFO]",
            "SUCCESS": "[OK]",
            "WARNING": "[WARN]",
            "CRITICAL": "[CRITICAL]",
        }
        prefix = level_map.get(severity, "[ALERT]")

        # Local Console Log
        log_msg = f"{prefix} {title}: {message}"
        if severity == "CRITICAL":
            logger.critical(log_msg)
        elif severity == "WARNING":
            logger.warning(log_msg)
        elif severity == "SUCCESS":
            logger.success(log_msg)
        else:
            logger.info(log_msg)

        # Webhook payload (Slack/Discord compatible)
        if not self.webhook_url:
            return False

        try:
            payload = {
                "text": f"*{prefix} {title}* ({timestamp})\n>{message}",
                "severity": severity,
                "details": details or {},
            }
            req = urllib.request.Request(
                self.webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json", "User-Agent": "OptionAlpha-Agent/1.0"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                return resp.status == 200
        except Exception as exc:
            logger.debug("Failed to send webhook alert: {}", exc)
            return False
