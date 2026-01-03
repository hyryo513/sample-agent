from lib1 import metadata


def run(name: str = "agent-alpha") -> str:
    meta = metadata()
    return f"{name} ok ({meta.get('library')})"
