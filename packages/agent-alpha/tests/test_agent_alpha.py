from agent_alpha import run


def test_run_default():
    out = run()
    assert isinstance(out, str)
    assert "agent-alpha" in out


def test_run_with_name():
    out = run("custom-name")
    assert out.startswith("custom-name ok")
