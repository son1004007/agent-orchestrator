from __future__ import annotations

import os
import sys
from time import monotonic
from pathlib import Path

import yaml

from orchestrator.adapters import ClaudeAdapter, CodexAdapter, GeminiAdapter
from orchestrator.models import StepStatus, WorkflowStep
from orchestrator.evidence import RunLedger
from orchestrator.subscription_policy import SubscriptionPolicyError, availability, check_agent

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


def execute_step(
    step: WorkflowStep, task: str, cwd: Path, timeout: int, ledger: RunLedger | None = None
) -> str:
    prompt = (
        f"Overall task:\n{task}\n\n"
        f"Current workflow step: {step.name}\n"
        "Work only on this step. Inspect repository context first. "
        "Return a concise result with changed files, checks performed, and unresolved risks."
    )
    step.status = StepStatus.RUNNING
    for agent_name in [step.primary, *step.fallback]:
        try:
            check_agent(agent_name)
        except SubscriptionPolicyError as exc:
            print(f"[{step.name}] {agent_name} disabled: {exc}", file=sys.stderr)
            continue
        adapter = ADAPTERS[agent_name]
        start = monotonic()
        result = adapter.run(prompt, cwd=cwd, timeout_seconds=timeout)
        if ledger is not None:
            ledger.append(
                step=step.name,
                agent=agent_name,
                returncode=result.returncode,
                elapsed_ms=int((monotonic() - start) * 1000),
                stdout_chars=len(result.stdout),
                stderr_chars=len(result.stderr),
            )
        if result.ok:
            step.status = StepStatus.SUCCEEDED
            return result.stdout
        print(f"[{step.name}] {agent_name} failed: exit={result.returncode}", file=sys.stderr)
    step.status = StepStatus.FAILED
    raise RuntimeError(f"All permitted agents failed for step: {step.name}")


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: python -m orchestrator.supervisor <workflow.yaml> <task> [--dry-run]")
        return 2

    workflow_path = Path(sys.argv[1]).resolve()
    task = sys.argv[2]
    dry_run = "--dry-run" in sys.argv[3:]
    cwd = Path.cwd()
    timeout = int(os.getenv("AGENT_TIMEOUT_SECONDS", "900"))
    steps = load_steps(workflow_path)

    routes = availability(list(dict.fromkeys(
        agent for step in steps for agent in [step.primary, *step.fallback]
    )))
    if dry_run:
        for step in steps:
            print(f"{step.name}: primary={step.primary} fallback={step.fallback}")
        for agent, status in routes.items():
            print(f"{agent}: {status}")
        print("No CLI invoked; permissions do not confirm active subscription auth.")
        return 0

    # Reject disallowed mandatory routes before spending any model quota.
    for step in steps:
        try:
            check_agent(step.primary)
        except SubscriptionPolicyError as exc:
            print(f"Policy blocked primary for {step.name}: {exc}", file=sys.stderr)
            return 3

    ledger = RunLedger(cwd / "artifacts" / "run-ledger")
    for step in steps:
        print(f"\n=== {step.name} ({step.primary}) ===")
        output = execute_step(step, task, cwd, timeout, ledger)
        print(output)
    print(f"CLI evidence: {ledger.path}; acceptance tests NOT RUN by supervisor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
