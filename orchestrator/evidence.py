"""Atomic metadata-only agent attempt ledger: excludes prompts, tokens and output."""
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4


class RunLedger:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / f"{uuid4().hex}.json"
        self.entries: list[dict] = []

    def append(
        self,
        *,
        step: str,
        agent: str,
        returncode: int,
        elapsed_ms: int,
        stdout_chars: int,
        stderr_chars: int,
    ) -> None:
        """Exit 0 is a successful CLI call, *not* successful acceptance testing."""
        self.entries.append({
            "step": step,
            "agent": agent,
            "returncode": returncode,
            "elapsed_ms": max(0, elapsed_ms),
            "stdout_chars": stdout_chars,
            "stderr_chars": stderr_chars,
            "status": "CLI_OK_UNVERIFIED" if returncode == 0 else "CLI_FAILED",
        })
        with NamedTemporaryFile(
            "w", encoding="utf-8", dir=self.root, delete=False,
            prefix=".run-", suffix=".tmp",
        ) as tmp:
            json.dump({"schema_version": 1, "attempts": self.entries}, tmp, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            temp_path = Path(tmp.name)
        try:
            temp_path.replace(self.path)
        finally:
            temp_path.unlink(missing_ok=True)
