#!/usr/bin/env python3
"""Entry point."""

try:
    from .cli import main
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from grobid.cli import main

__all__ = ["main"]

if __name__ == "__main__":
    import sys

    sys.exit(main())
