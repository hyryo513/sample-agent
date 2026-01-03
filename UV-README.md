UV package manager — install & quick setup

This file contains concrete, safe commands to install Python 3.13 (macOS arm64), create a virtual environment, and install the `uv` PyPI package as requested.

Notes:
- These steps assume you will run the commands locally (they require admin for the system installer).
- If you prefer a different `uv` source (private registry or custom CLI), paste the package URL or docs and I will adapt these steps.

1) Confirm architecture

Run:

    uname -m

If it prints `arm64`, use the macOS arm64 installer below.

2) Download & install Python 3.13 (example using Python.org installer)

Replace `3.13.2` with the latest 3.13.x release if you prefer. This requires admin/sudo.

    curl -LO https://www.python.org/ftp/python/3.13.2/python-3.13.2-macos11-arm64.pkg
    sudo installer -pkg python-3.13.2-macos11-arm64.pkg -target /

After installation verify:

    python3.13 --version

3) Create a reusable virtual environment and activate it

    cd sample-agent
    python3.13 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip

4) Install `uv` (PyPI) and developer deps

    pip install uv
    # optional: install placeholder agent deps
    pip install langgraph || true
    pip install -e .

5) Verify test run

    pytest -q

6) Notes about `uv` config

- `uv` is installed from PyPI in this guide. If you expect the `uv` package to be a custom CLI/tool or have a different manifest format (e.g. `uv.toml`), share the docs or example files and I'll add a repo-level config and CI steps.

7) Git & local commit (once Python/env is ready)

    git config --global user.name "GitHub Copilot"
    git config --global user.email "copilot@example.com"
    cd sample-agent
    git init
    git checkout -b sdlc/agentcore-prototype
    git add .
    git commit -m "scaffold: initial sample-agent prototype (LangGraph + Python 3.13)"

If you'd like, after you run the installer and confirm the environment, I can finalize a branch and push the scaffold to your upstream remote (you'll need to provide repo URL/access or enable git on your machine). Paste any `uv` docs if `uv` is not the PyPI package and I'll update the repo accordingly.
