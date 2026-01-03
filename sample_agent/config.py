"""Configuration helpers for the sample agent."""
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class Config:
    agent_name: str = "sample-agent"
    agentcore_endpoint: Optional[str] = None
    agentcore_api_key: Optional[str] = None
    langgraph_config: Optional[dict] = None

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            agent_name=os.environ.get("AGENT_NAME", "sample-agent"),
            agentcore_endpoint=os.environ.get("AGENTCORE_ENDPOINT"),
            agentcore_api_key=os.environ.get("AGENTCORE_API_KEY"),
            langgraph_config=None,
        )
