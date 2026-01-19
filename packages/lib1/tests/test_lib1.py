from lib1 import metadata, AgentConfig


def test_metadata():
    """Test metadata function returns expected dict."""
    m = metadata()
    assert isinstance(m, dict)
    assert m.get("library") == "lib1"


def test_agent_config_defaults():
    """Test AgentConfig creation with default environment."""
    config = AgentConfig(
        agent_name="test-agent",
        agentcore_endpoint="http://localhost:8000",
        agentcore_api_key="test-key"
    )
    
    assert config.agent_name == "test-agent"
    assert config.agentcore_endpoint == "http://localhost:8000"
    assert config.agentcore_api_key == "test-key"


def test_agent_config_validation():
    """Test AgentConfig validates agent_name not empty."""
    try:
        config = AgentConfig(agent_name="")
        assert False, "Should raise ValueError for empty agent_name"
    except ValueError as e:
        assert "cannot be empty" in str(e)


def test_agent_config_model_dump_env():
    """Test AgentConfig exports environment variable dict."""
    config = AgentConfig(
        agent_name="test-agent",
        agentcore_endpoint="http://localhost:8000",
        agentcore_api_key="test-key"
    )
    
    env_vars = config.model_dump_env()
    assert env_vars["AGENT_NAME"] == "test-agent"
    assert env_vars["AGENTCORE_ENDPOINT"] == "http://localhost:8000"
    assert env_vars["AGENTCORE_API_KEY"] == "test-key"

