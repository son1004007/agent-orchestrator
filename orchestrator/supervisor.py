from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml

from orchestrator.adapters import ClaudeAdapter, CodexAdapter, GeminiAdapter
from orchestrator.models import StepStatus, WorkflowStep

ADAPTERS = {
    "codex": CodexAdapter(),
    "claude": ClaudeAdapter(),
    "gemini": GeminiAdapter(),
}


def load_steps(path: Path) -> list[WorkflowStep]:
    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [
        WorkflowStep(
            name=item["name"],
            primary=item["primary"],
            fallback=item.get("fallback", []),
        )
        for item in config["steps"]
    ]


def execute_step(step: WorkflowStep, task: str, cwd: Path, timeout: int) -> str:
    prompt = (
        f"Overall task:\n{task}\n\n"
        f"Current workflow step: {step.name}\n"
        "Work only on this step. Inspect repository context first. "
        "Return a concise result with changed files, checks performed, and unresolved risks."
    )
    step.status = StepStatus.RUNNING
    for agent_name in [step.primary, *step.fallback]:
        adapter = ADAPTERS[agent_name]
        result = adapter.run(prompt, cwd=cwd, timeout_seconds=timeout)
        if result.ok:
            step.status = StepStatus.SUCCEEDED
            return result.stdout
        print(f"[{step.name}] {agent_name} failed: {result.stderr}", file=sys.stderr)
    step.status = StepStatus.FAILED
    raise RuntimeError(f"All agents failed for step: {step.name}")


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: python -m orchestrator.supervisor <workflow.yaml> <task>")
        return 2

    workflow_path = Path(sys.argv[1]).resolve()
    task = sys.argv[2]
    cwd = Path.cwd()
    timeout = int(os.getenv("AGENT_TIMEOUT_SECONDS", "900"))

    for step in load_steps(workflow_path):
        print(f"\n=== {step.name} ({step.primary}) ===")
        output = execute_step(step, task, cwd, timeout)
        print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
