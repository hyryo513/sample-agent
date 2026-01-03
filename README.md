# sample-agent

Prototype SDLC automation for AI agents using LangGraph + AWS AgentCore

This repository contains a small, workspace-style scaffold for developing AI agents
and related libraries. Each agent or module is a workspace package under
`packages/` (for example `packages/sample-agent`). The layout is suitable for
multi-agent monorepos and is managed with `uv` as the workspace/package manager.

Key files & layout
- `pyproject.toml` — root project metadata and workspace `tool.uv` settings.
- `packages/` — workspace packages (each package contains its own `pyproject.toml` and `src/`).
- `packages/sample-agent/` — the sample agent package (source at `packages/sample-agent/src/sample_agent`).


Requirements
- Python 3.13 (local development)
- Build backend: `setuptools` (configured in package `pyproject.toml`)
- Optional: `uv` (workspace/package manager; installed from PyPI)


Local setup (recommended)

1. Install Python 3.13. Then create a virtualenv and install dev deps:

```bash
cd sample-agent
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
# install root dev tools or install per-package dev extras
pip install -e 'packages/sample-agent[dev]'
```


Notes on workspace & building
- This repository uses `setuptools` as the PEP 517 build-backend (declared in each package's `pyproject.toml`).
- To build a package wheel/sdist (uses the configured backend):

```bash
python -m pip install --upgrade build
python -m build packages/sample-agent
```

- `uv` (workspace manager) installs and locks workspace dependencies. Example workflows:

```bash
# install uv (one-time)
python -m pip install uv

# install all workspace packages in editable mode and dev deps (if supported by your uv)
uv install

# or install a specific package editable (fallback to pip)
python -m pip install -e packages/sample-agent
```

Run the agent (demo)

```bash
# run the package module (from workspace package)
python -m sample_agent
```

Run tests

```bash
# run package-local tests
pytest packages/sample-agent/tests -q

# or run all workspace tests
pytest -q
```

Configuration & environment
- `AGENTCORE_ENDPOINT` — HTTP endpoint for AgentCore (optional; when omitted agentcore client returns a stub response).
- `AGENTCORE_API_KEY` — API key for AgentCore (optional).
- `AGENT_NAME` — agent name used in payloads; default `sample-agent`.

Behavior notes
Behavior notes
- `packages/sample-agent/src/sample_agent/langgraph_agent.py` uses a real `langgraph.Agent` when available, and falls back to a local stub implementation for unit tests and offline development.
- `packages/sample-agent/src/sample_agent/agentcore_client.py` will POST JSON to `AGENTCORE_ENDPOINT` if provided; otherwise it returns a deterministic stubbed dict useful for CI and unit tests.

Docker (optional)

```bash
docker build -t sample-agent:latest .
docker run --rm sample-agent:latest
```

Git
- Initialize and commit locally then push over SSH to avoid username/password prompts.

Contributing
- Keep PRs small and focused.
- Add tests for any functional change; integration tests that require AgentCore should be opt-in.

If you want, I can initialize `git` and commit the scaffold to `main`, or push a branch and open a PR. Tell me which action you prefer.
