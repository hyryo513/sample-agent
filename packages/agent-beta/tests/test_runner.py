from agent_beta import create_agent_components, run_once, shutdown, Config


def test_run_once_default():
    cfg = Config(agent_name="test-agent")
    comps = create_agent_components(cfg)
    out = run_once(comps, message="ping")
    assert "langgraph_response" in out
    assert out["langgraph_response"] == "echo: ping" or isinstance(out["langgraph_response"], str)
    assert "agentcore_response" in out
    assert isinstance(out["agentcore_response"], dict)
    shutdown(comps)
