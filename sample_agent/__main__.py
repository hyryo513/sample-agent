"""Module entrypoint: run the sample agent as a simple script.

Usage:
    python -m sample_agent
"""
from .config import Config
from .runner import create_agent_components, run_once, shutdown


def main():
    cfg = Config.from_env()
    components = create_agent_components(cfg)
    # perform one run for demo purposes
    result = run_once(components, message="startup-check")
    print(result)
    shutdown(components)


if __name__ == "__main__":
    main()
