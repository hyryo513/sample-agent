"""Strands-compatible utility library with 12-factor configuration validation.

This module provides reusable config models and helpers for agents
deployed to AWS Lambda with environment-driven configuration.
"""
from typing import Dict, Optional
from pydantic import BaseModel, Field, field_validator
import os


def metadata() -> Dict[str, str]:
    """Return library metadata."""
    return {"library": "lib1", "version": "0.0.0"}


class AgentConfig(BaseModel):
    """12-factor configuration for Strands-based agents.
    
    Validates environment variables at cold start for AWS Lambda deployment.
    """
    agent_name: str = Field(
        default_factory=lambda: os.environ.get("AGENT_NAME", "default-agent"),
        description="Agent identifier"
    )
    agentcore_endpoint: Optional[str] = Field(
        default_factory=lambda: os.environ.get("AGENTCORE_ENDPOINT"),
        description="AgentCore HTTP endpoint for posting agent responses"
    )
    agentcore_api_key: Optional[str] = Field(
        default_factory=lambda: os.environ.get("AGENTCORE_API_KEY"),
        description="AgentCore Bearer token for API authentication"
    )
    
    @field_validator("agent_name")
    @classmethod
    def validate_agent_name(cls, v: str) -> str:
        """Ensure agent name is not empty."""
        if not v or not v.strip():
            raise ValueError("agent_name cannot be empty")
        return v.strip()
    
    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables (12-factor)."""
        return cls()
    
    def model_dump_env(self) -> Dict[str, Optional[str]]:
        """Export config as environment variable dict for subprocess execution."""
        return {
            "AGENT_NAME": self.agent_name,
            "AGENTCORE_ENDPOINT": self.agentcore_endpoint or "",
            "AGENTCORE_API_KEY": self.agentcore_api_key or "",
        }

