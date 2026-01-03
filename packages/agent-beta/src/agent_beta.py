"""Agent Beta single-module package (migrated from `sample_agent`).

This file consolidates the small runner, agentcore client and lightweight
langgraph wrapper so the package can be delivered as a single module.
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
        if not self.endpoint or requests is None:
            return {"status": "ok", "endpoint": self.endpoint, "payload": payload}

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()


class _StubLangGraph:
    def __init__(self, *args, **kwargs):
        self._state = {}

    def send(self, message: str) -> str:
        return f"echo: {message}"

    def shutdown(self) -> None:
        self._state.clear()


try:
    import langgraph  # type: ignore
    _HAS_LANGGRAPH = hasattr(langgraph, "Agent")
except Exception:
    langgraph = None  # type: ignore
    _HAS_LANGGRAPH = False


if _HAS_LANGGRAPH:
    class LangGraphAgent:
        def __init__(self, config: Dict[str, Any] | None = None):
            self.config = config or {}
            self._agent = langgraph.Agent(**(self.config or {}))

        def send(self, message: str) -> str:
            return self._agent.send(message)

        def shutdown(self) -> None:
            if hasattr(self._agent, "shutdown"):
                self._agent.shutdown()

else:
    class LangGraphAgent:
        def __init__(self, config: Dict[str, Any] | None = None):
            self.config = config or {}
            self._agent = _StubLangGraph()

        def send(self, message: str) -> str:
            return self._agent.send(message)

        def shutdown(self) -> None:
            self._agent.shutdown()


from dataclasses import dataclass


@dataclass
class Config:
    agent_name: str = "agent-beta"
    agentcore_endpoint: Optional[str] = None
    agentcore_api_key: Optional[str] = None
    langgraph_config: Optional[Dict[str, Any]] = None

    @staticmethod
    def from_env() -> "Config":
        return Config(
            agent_name=os.environ.get("AGENT_NAME", "agent-beta"),
            agentcore_endpoint=os.environ.get("AGENTCORE_ENDPOINT"),
            agentcore_api_key=os.environ.get("AGENTCORE_API_KEY"),
            langgraph_config=None,
        )


def create_agent_components(config: Config | None = None) -> Dict[str, Any]:
    config = config or Config.from_env()
    lg = LangGraphAgent(config=config.langgraph_config)
    ac = AgentCoreClient(endpoint=config.agentcore_endpoint, api_key=config.agentcore_api_key)
    return {"langgraph": lg, "agentcore": ac, "config": config}


def run_once(components: Dict[str, Any], message: str = "hello") -> Dict[str, Any]:
    lg: LangGraphAgent = components["langgraph"]
    ac: AgentCoreClient = components["agentcore"]

    response = lg.send(message)
    payload = {"agent": components["config"].agent_name, "input": message, "output": response}
    ac_resp = ac.send_event(payload)
    return {"langgraph_response": response, "agentcore_response": ac_resp}


def shutdown(components: Dict[str, Any]) -> None:
    components["langgraph"].shutdown()


if __name__ == "__main__":
    comps = create_agent_components()
    print(run_once(comps, "hello"))
