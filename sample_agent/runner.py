"""Runner that wires up LangGraphAgent + AgentCoreClient and provides a minimal loop.

This runner is intentionally small so it can be easily tested and extended.
"""
from typing import Dict, Any
from .config import Config
from .langgraph_agent import LangGraphAgent
from .agentcore_client import AgentCoreClient


def create_agent_components(config: Config | None = None) -> Dict[str, Any]:
    config = config or Config.from_env()
    lg = LangGraphAgent(config=config.langgraph_config)
    ac = AgentCoreClient(endpoint=config.agentcore_endpoint, api_key=config.agentcore_api_key)
    return {"langgraph": lg, "agentcore": ac, "config": config}


def run_once(components: Dict[str, Any], message: str = "hello") -> Dict[str, Any]:
    """Single-step run: send a message to the LangGraph agent and forward result to AgentCore.

    Returns a dict with the agent response and the agentcore response (or stub).
    """
    lg: LangGraphAgent = components["langgraph"]
    ac: AgentCoreClient = components["agentcore"]

    response = lg.send(message)
    payload = {"agent": components["config"].agent_name, "input": message, "output": response}
    ac_resp = ac.send_event(payload)
    return {"langgraph_response": response, "agentcore_response": ac_resp}


def shutdown(components: Dict[str, Any]) -> None:
    components["langgraph"].shutdown()
