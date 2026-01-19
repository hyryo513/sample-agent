"""Agent Alpha - Strands-based agent for AWS Lambda deployment.

This agent demonstrates basic Strands SDK integration with lib1 configuration.
"""
from typing import Any, Dict
from lib1 import AgentConfig, metadata


class StrandsAgent:
    """Simple Strands-based agent implementation."""
    
    def __init__(self, config: AgentConfig):
        """Initialize agent with configuration.
        
        Args:
            config: AgentConfig instance with environment-driven settings.
        """
        self.config = config
        self.name = config.agent_name
    
    def invoke(self, message: str) -> str:
        """Invoke agent logic (Strands strand execution).
        
        Args:
            message: Input message to process.
            
        Returns:
            Agent response.
        """
        meta = metadata()
        return f"{self.name} processed: {message} (via {meta.get('library')})"
    
    def shutdown(self) -> None:
        """Clean shutdown of agent resources."""
        pass


def create_agent(config: AgentConfig | None = None) -> StrandsAgent:
    """Factory to create Strands agent instance.
    
    Args:
        config: Optional AgentConfig. If None, loads from environment.
        
    Returns:
        Initialized StrandsAgent instance.
    """
    if config is None:
        config = AgentConfig.from_env()
    return StrandsAgent(config=config)

