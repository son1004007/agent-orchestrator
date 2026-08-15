from __future__ import annotations

import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path

from orchestrator.models import AgentResult


class CliAgentAdapter(ABC):
    name: str
    env_var: str
    default_binary: str

    @abstractmethod
    def build_command(self, binary: str, prompt: str) -> list[str]:
        raise NotImplementedError

    def run(self, prompt: str, cwd: Path, timeout_seconds: int) -> AgentResult:
        binary = os.getenv(self.env_var, self.default_binary)
        command = self.build_command(binary, prompt)
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                check=False,
            )
            return AgentResult(self.name, completed.returncode, completed.stdout, completed.stderr)
        except FileNotFoundError as exc:
            return AgentResult(self.name, 127, "", str(exc))
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            return AgentResult(self.name, 124, stdout, stderr or "agent timed out")
