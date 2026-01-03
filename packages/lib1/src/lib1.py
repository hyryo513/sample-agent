"""Small reusable library module (lib1).

This mirrors the previous `common` package but uses a single-module layout
so multiple small libs can coexist in the workspace as `lib1`, `lib2`, ...
"""
from typing import Dict


def metadata() -> Dict[str, str]:
    return {"library": "lib1", "version": "0.0.0"}
