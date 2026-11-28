"""Which commit a running server was started from.

`/health` reports the package version, and two servers can report the same
version from different commits: the hosted instances follow a branch, one of
them is updated by hand, and a release covers many commits. The commit is read
once at start-up so a deployment can be compared with its branch.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

_COMMIT_ENV = "ECUADOR_MCP_COMMIT"
# Render sets RENDER_GIT_COMMIT on every deploy.
_HOST_COMMIT_ENVS = (_COMMIT_ENV, "RENDER_GIT_COMMIT")
_SHA_RE = re.compile(r"[0-9a-f]{7,40}")


def get_commit() -> str | None:
    """The commit SHA of this server, or None when it cannot be known.

    Taken from ECUADOR_MCP_COMMIT or the host's own variable when set (a Docker
    image has no .git), else from `git rev-parse HEAD` in a checkout. A PyPI or
    MCPB install has neither and reports None; its version says what it is.
    """
    for name in _HOST_COMMIT_ENVS:
        value = os.getenv(name, "").strip().lower()
        if _SHA_RE.fullmatch(value):
            return value
    root = Path(__file__).resolve().parent.parent
    if not (root / ".git").exists():
        return None
    try:
        done = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    value = done.stdout.strip().lower()
    return value if done.returncode == 0 and _SHA_RE.fullmatch(value) else None
