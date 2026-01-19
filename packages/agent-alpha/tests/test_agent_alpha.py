from lib1 import AgentConfig
from agent_alpha import create_agent


def test_create_agent_with_config():
    """Test agent creation with explicit config."""
    config = AgentConfig(agent_name="test-agent")
    agent = create_agent(config)
    
    assert agent.name == "test-agent"
    assert agent.config.agent_name == "test-agent"


def test_invoke_agent():
    """Test agent invoke returns string response."""
    config = AgentConfig(agent_name="agent-alpha")
    agent = create_agent(config)
    
    response = agent.invoke("test message")
    assert isinstance(response, str)
    assert "agent-alpha" in response
    assert "test message" in response


def test_agent_shutdown():
    """Test agent shutdown completes without error."""
    config = AgentConfig(agent_name="agent-alpha")
    agent = create_agent(config)
    
    # Should not raise exception
    agent.shutdown()

