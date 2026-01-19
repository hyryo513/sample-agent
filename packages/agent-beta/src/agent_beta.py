"""Agent Beta - Strands-based agent with AgentCore integration.

This agent demonstrates Strands SDK integration with HTTP client for
posting responses to AgentCore platform. Configuration is validated at
Lambda cold start per 12-factor principles.
"""
from typing import Any, Dict, Optional
import os
import logging

try:
    import requests
except ImportError:
    requests = None  # type: ignore

from lib1 import AgentConfig

logger = logging.getLogger(__name__)


class AgentCoreClient:
    """HTTP client for AgentCore platform integration.
    
    Posts agent responses to AgentCore endpoint with optional Bearer token auth.
    """
    
    def __init__(self, endpoint: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize AgentCore client.
        
        Args:
            endpoint: AgentCore HTTP endpoint. Falls back to AGENTCORE_ENDPOINT env var.
            api_key: Bearer token for authentication. Falls back to AGENTCORE_API_KEY env var.
        """
        self.endpoint = endpoint or os.environ.get("AGENTCORE_ENDPOINT")
        self.api_key = api_key or os.environ.get("AGENTCORE_API_KEY")
    
    def send_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send event payload to AgentCore.
        
        Args:
            payload: Event dict with agent response data.
            
        Returns:
            AgentCore response dict. Returns stub response if requests unavailable.
        """
        if not self.endpoint or requests is None:
            return {"status": "ok", "endpoint": self.endpoint, "payload": payload}
        
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"AgentCore event send failed: {e}")
            return {"status": "error", "error": str(e)}


class StrandsAgent:
    """Strands-based agent with AgentCore integration.
    
    Executes Strands strand logic and posts results to AgentCore platform.
    """
    
    def __init__(self, config: AgentConfig, agentcore_client: Optional[AgentCoreClient] = None):
        """Initialize Strands agent.
        
        Args:
            config: AgentConfig with agent identity and endpoints.
            agentcore_client: Optional AgentCoreClient. If None, creates from config.
        """
        self.config = config
        self.name = config.agent_name
        self.agentcore_client = agentcore_client or AgentCoreClient(
            endpoint=config.agentcore_endpoint,
            api_key=config.agentcore_api_key
        )
    
    def invoke(self, message: str) -> str:
        """Invoke Strands agent logic.
        
        Args:
            message: Input message to process via Strands strand.
            
        Returns:
            Agent response.
        """
        # Placeholder for Strands strand execution
        # In production, this invokes Strands SDK to execute defined strands/workflows
        return f"Strands-agent {self.name} processed: {message}"
    
    def run(self, message: str = "default") -> Dict[str, Any]:
        """Execute Strands agent and post to AgentCore.
        
        Args:
            message: Input message for Strands strand.
            
        Returns:
            Dict with langgraph_response and agentcore_response keys (backward compatible).
        """
        response = self.invoke(message)
        payload = {
            "agent": self.name,
            "input": message,
            "output": response
        }
        ac_resp = self.agentcore_client.send_event(payload)
        return {
            "langgraph_response": response,  # Keep key name for backward compat
            "agentcore_response": ac_resp
        }
    
    def shutdown(self) -> None:
        """Clean shutdown of agent resources."""
        pass


def create_agent_components(config: AgentConfig | None = None) -> Dict[str, Any]:
    """Factory to create Strands agent and AgentCore client components.
    
    Args:
        config: Optional AgentConfig. If None, loads from environment.
        
    Returns:
        Dict with initialized agent and client components.
    """
    if config is None:
        config = AgentConfig.from_env()
    
    agent = StrandsAgent(config=config)
    return {
        "agent": agent,
        "agentcore": agent.agentcore_client,
        "config": config
    }


def run_once(components: Dict[str, Any], message: str = "hello") -> Dict[str, Any]:
    """Execute single Strands agent invocation and post to AgentCore.
    
    Args:
        components: Dict from create_agent_components.
        message: Input message for Strands strand.
        
    Returns:
        Agent and AgentCore responses.
    """
    agent: StrandsAgent = components["agent"]
    return agent.run(message)


def shutdown(components: Dict[str, Any]) -> None:
    """Shutdown agent components.
    
    Args:
        components: Dict from create_agent_components.
    """
    agent: StrandsAgent = components["agent"]
    agent.shutdown()


if __name__ == "__main__":
    comps = create_agent_components()
    print(run_once(comps, "hello"))

