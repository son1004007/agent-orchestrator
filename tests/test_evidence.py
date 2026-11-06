import json

from orchestrator.evidence import RunLedger


def test_ledger_saves_metadata_not_prompt_or_output(tmp_path):
    ledger = RunLedger(tmp_path)
    ledger.append(step="implement", agent="codex", returncode=0,
                  elapsed_ms=20, stdout_chars=21, stderr_chars=0)
    ledger.append(step="review", agent="codex", returncode=1,
                  elapsed_ms=30, stdout_chars=0, stderr_chars=8)
    saved = json.loads(ledger.path.read_text(encoding="utf-8"))
    assert saved["schema_version"] == 1
    assert len(saved["attempts"]) == 2
    assert saved["attempts"][0]["status"] == "CLI_OK_UNVERIFIED"
    assert saved["attempts"][1]["status"] == "CLI_FAILED"
    assert "prompt" not in ledger.path.read_text(encoding="utf-8")
    assert "stdout" not in saved["attempts"][0]
