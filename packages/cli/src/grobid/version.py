"""Version."""

import os
import sys
from datetime import datetime


def get_version() -> str:
    try:
        if getattr(sys, "frozen", False):
            mtime = os.path.getmtime(sys.executable)
            return datetime.fromtimestamp(mtime).strftime("%Y.%m.%d.%H.%M.%S")
    except OSError:
        pass
    try:
        mtime = os.path.getmtime(os.path.abspath(__file__))
        return datetime.fromtimestamp(mtime).strftime("%Y.%m.%d.%H.%M.%S")
    except OSError:
        pass
    return datetime.now().strftime("%Y.%m.%d.%H.%M.%S")


__version__ = get_version()
