"""
cli/alpaca_cli.py
==================
OptionAlpha Agent — Alpaca CLI Binary Subprocess Wrapper

Wraps Alpaca's official CLI (`apca` or `alpaca`) tool as an automated fallback
when the REST API experiences HTTP 429 rate limits or network issues.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import Dict, List, Optional
from loguru import logger


class AlpacaCLIWrapper:
    """
    Subprocess execution wrapper for the Alpaca CLI tool.
    """

    def __init__(self):
        self._bin = shutil.which("apca") or shutil.which("alpaca")

    @property
    def is_available(self) -> bool:
        return self._bin is not None

    def get_account(self) -> Optional[Dict]:
        if not self.is_available:
            return None
        try:
            res = subprocess.run([self._bin, "get", "account", "-o", "json"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                return json.loads(res.stdout)
        except Exception as e:
            logger.debug("Alpaca CLI account query error: {}", e)
        return None

    def get_positions(self) -> Optional[List[Dict]]:
        if not self.is_available:
            return None
        try:
            res = subprocess.run([self._bin, "get", "positions", "-o", "json"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0:
                return json.loads(res.stdout)
        except Exception as e:
            logger.debug("Alpaca CLI positions query error: {}", e)
        return None
