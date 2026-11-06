import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator.evidence import RunLedger
from orchestrator.models import AgentResult, StepStatus, WorkflowStep
from orchestrator import supervisor


def test_subscription_workflow_dry_run(monkeypatch, capsys):
    monkeypatch.setattr(supervisor.sys, "argv", [
        "supervisor", "workflows/subscription-safe.yaml", "unused", "--dry-run",
    ])
    monkeypatch.setattr(supervisor.os, "environ", {})
    assert supervisor.main() == 0
    output = capsys.readouterr().out
    assert "PERMITTED_UNVERIFIED_AUTH" in output
    assert "No CLI invoked" in output


def test_exec_codex_only_without_disabled_fallbacks(monkeypatch, tmp_path):
    called = []
    fake = SimpleNamespace(run=lambda prompt, cwd, timeout_seconds:
                           (called.append(prompt) or AgentResult("codex", 0, "done", "")))
    monkeypatch.setattr(supervisor, "ADAPTERS", {"codex": fake})
    monkeypatch.setattr(supervisor.os, "environ", {})
    ledger = RunLedger(tmp_path)
    step = WorkflowStep("implement", "codex", ["claude", "gemini"])
    assert supervisor.execute_step(step, "test feature", Path.cwd(), 5, ledger) == "done"
    assert len(called) == 1
    assert step.status == StepStatus.SUCCEEDED
    record = json.loads(ledger.path.read_text(encoding="utf-8"))
    assert record["attempts"][0]["agent"] == "codex"
    assert record["attempts"][0]["status"] == "CLI_OK_UNVERIFIED"


def test_disallowed_gemini_primary_never_invoked(monkeypatch, tmp_path):
    monkeypatch.setattr(supervisor.os, "environ", {})
    monkeypatch.setattr(supervisor, "ADAPTERS", {
        "gemini": SimpleNamespace(run=lambda *a, **k: pytest.fail("CLI unexpectedly invoked"))
    })
    with pytest.raises(RuntimeError, match="All permitted agents failed"):
        supervisor.execute_step(WorkflowStep("x", "gemini"), "task", tmp_path, 1)
