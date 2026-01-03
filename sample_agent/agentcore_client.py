"""Lightweight AWS AgentCore client scaffold.

This is a placeholder client that knows how to POST events to an
AgentCore HTTP endpoint (if provided). For local development this
keeps interactions simple and testable.
"""
from typing import Any, Dict, Optional
import os

try:
    import requests
except Exception:  # pragma: no cover - requests optional
    requests = None  # type: ignore


class AgentCoreClient:
    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None):
        self.endpoint = endpoint or os.environ.get("AGENTCORE_ENDPOINT")
        self.api_key = api_key or os.environ.get("AGENTCORE_API_KEY")

    def send_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send an event to AgentCore. Returns parsed JSON or a simple dict on fallback.

        The method uses `requests` if available; otherwise it returns a local stub response.
        """
        if not self.endpoint or requests is None:
            return {"status": "ok", "endpoint": self.endpoint, "payload": payload}

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
