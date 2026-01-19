from lib1 import AgentConfig
from agent_beta import create_agent_components, run_once, shutdown, StrandsAgent, AgentCoreClient


def test_strands_agent_invoke():
    """Test Strands agent invocation."""
    config = AgentConfig(agent_name="test-agent")
    agent = StrandsAgent(config=config)
    
    response = agent.invoke("test message")
    assert isinstance(response, str)
    assert "test-agent" in response
    assert "test message" in response


def test_agentcore_client_send_event():
    """Test AgentCore client send_event (stub mode when endpoint missing)."""
    client = AgentCoreClient(endpoint=None)
    
    payload = {"test": "data"}
    response = client.send_event(payload)
    
    assert isinstance(response, dict)
    assert response.get("status") == "ok"
    assert response.get("payload") == payload


def test_create_agent_components():
    """Test component factory creates agent and clients."""
    config = AgentConfig(agent_name="test-agent")
    comps = create_agent_components(config)
    
    assert "agent" in comps
    assert "agentcore" in comps
    assert "config" in comps
    assert isinstance(comps["agent"], StrandsAgent)
    assert isinstance(comps["agentcore"], AgentCoreClient)
    assert isinstance(comps["config"], AgentConfig)


def test_run_once_default():
    """Test run_once executes Strands agent and posts to AgentCore."""
    config = AgentConfig(agent_name="test-agent")
    comps = create_agent_components(config)
    
    result = run_once(comps, message="ping")
    
    assert "langgraph_response" in result
    assert isinstance(result["langgraph_response"], str)
    assert "agentcore_response" in result
    assert isinstance(result["agentcore_response"], dict)
    
    shutdown(comps)


def test_agent_shutdown():
    """Test agent shutdown completes without error."""
    config = AgentConfig(agent_name="test-agent")
    comps = create_agent_components(config)
    
    # Should not raise exception
    shutdown(comps)

