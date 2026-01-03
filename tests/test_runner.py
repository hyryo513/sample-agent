from sample_agent.runner import create_agent_components, run_once, shutdown
from sample_agent.config import Config


def test_run_once_default():
    cfg = Config(agent_name="test-agent")
    comps = create_agent_components(cfg)
    out = run_once(comps, message="ping")
    assert "langgraph_response" in out
    assert out["langgraph_response"] == "echo: ping" or isinstance(out["langgraph_response"], str)
    assert "agentcore_response" in out
    # agentcore_response is a dict stub when no real endpoint is provided
    assert isinstance(out["agentcore_response"], dict)
    shutdown(comps)
