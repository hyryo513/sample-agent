"""LangGraph agent wrapper (lightweight scaffold).

This module provides a minimal wrapper around `langgraph` if available,
and a safe fallback implementation for local development and testing.
"""
from typing import Any, Dict


class _StubLangGraph:
    def __init__(self, *args, **kwargs):
        self._state = {}

    def send(self, message: str) -> str:
        # simple echo behavior for testing
        return f"echo: {message}"

    def shutdown(self) -> None:
        self._state.clear()


try:
    import langgraph  # type: ignore
    _HAS_LANGGRAPH = hasattr(langgraph, "Agent")
except Exception:
    langgraph = None  # type: ignore
    _HAS_LANGGRAPH = False


if _HAS_LANGGRAPH:
    class LangGraphAgent:
        def __init__(self, config: Dict[str, Any] | None = None):
            self.config = config or {}
            # try to initialize using the library's Agent API; callers
            # will see runtime errors if the API signature differs.
            self._agent = langgraph.Agent(**(self.config or {}))

        def send(self, message: str) -> str:
            return self._agent.send(message)

        def shutdown(self) -> None:
            # Some implementations may not have shutdown; guard it.
            if hasattr(self._agent, "shutdown"):
                self._agent.shutdown()

else:
    # Fallback stub for environments without `langgraph` or with
    # a package that doesn't expose the expected `Agent` class.
    class LangGraphAgent:
        def __init__(self, config: Dict[str, Any] | None = None):
            self.config = config or {}
            self._agent = _StubLangGraph()

        def send(self, message: str) -> str:
            return self._agent.send(message)

        def shutdown(self) -> None:
            self._agent.shutdown()
