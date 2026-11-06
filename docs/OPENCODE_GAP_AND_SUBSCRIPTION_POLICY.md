# OpenCode gap assessment and subscription-only policy (2026-11-07)

## Scope
The user currently pays for ChatGPT Plus and Google AI Pro; Claude Pro/Max is not
subscribed. No metered model API keys or incremental API charges are authorized.
This repo is a minimal sequential CLI supervisor, not a production-ready harness.

## OpenCode comparison
References: https://github.com/anomalyco/opencode (MIT license),
https://docs.opencode.ai/docs/agents/ ,
https://docs.opencode.ai/docs/permissions/ ,
https://docs.opencode.ai/docs/config/ .

| Feature | Current repo (before this PR) | Treatment |
|---|---|---|
| Plan/Build scoped agents | No enforced separation | Future native sandbox profiles |
| Tool-level permissions | AGENTS.md policy only | Future verified sandbox/allowlist |
| Scoped subagents | Sequential CLI processes | Future bounded isolation/worktrees |
| Context compaction | No session manager | Use vendor-native compaction; avoid copying old logs into prompts |
| Session/attempt evidence | No durable ledger | Implemented metadata-only atomic ledger |
| Subscription-aware routing | YAML fallback without guard | Implemented fail-closed CLI execution policy |
| Quota optimization | No tracked outcomes | Record attempts and elapsed time; accepted tasks need actual tests |

Only *ideas* were reused; no OpenCode source copied. MIT permits source reuse
subject to license/copyright notice preservation. Avoid full TypeScript/Bun
fork without an ongoing upstream maintenance and security plan.

## Subscription boundaries (official-source-first)
1. **Codex**: use unmodified native CLI with the user's ChatGPT subscription.
   Reject API-key environment variables. CLI authentication still must be checked:
   this policy cannot distinguish cached API and subscription credentials.
   https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
2. **Claude Code**: unmodified native binary, personal subscription login only
   after subscribed and explicitly opted into this *local personal* workflow.
   Do not collect/intermediate subscription tokens, expose third-party login or
   run on behalf of other users. Review terms before implementing SDK workflows.
   https://code.claude.com/docs/en/legal-and-compliance
3. **AGY / Google AI Pro**: direct native app/CLI and direct scripting/CI are
   supported, but *wrapping consumer AGY inside third-party coding agents/apps*
   is not supported. Do **not** add an AGY CLI adapter here or use unofficial
   OAuth proxy/auth plugins. Run AGY independently under official surfaces.
   https://www.agy.dev/docs/faq/
4. The old `gemini` adapter is retained to read legacy YAML only. This PR
   deliberately blocks its execution under the subscription-only policy.
   It does not represent a working AGY integration.

## Safe commands
Dry-run (no LLM or auth is contacted):

```powershell
python -m orchestrator.supervisor workflows/subscription-safe.yaml "Implement feature" --dry-run
```

Codex-only *single CLI attempt* in an already authenticated environment
(with no API keys in process environment):

```powershell
python -m orchestrator.supervisor workflows/subscription-safe.yaml "Implement feature"
```

The legacy `workflows/feature.yaml` uses Claude/Gemini and will fail its
preflight until updated; this avoids silent spend or unsupported routing.

`artifacts/run-ledger/*.json` records step, CLI name, return code,
elapsed time and stdout/stderr lengths. It never stores the prompt or response.
An exit code 0 means `CLI_OK_UNVERIFIED`, not a verified feature, CI success,
approval, merge or deployment. This metadata is not a token count or pricing
metric and must not be represented as cost data.

## Next steps (not implemented)
- Verify local CLI executable versions and **actual native login type** on the user's machine.
- Implement proper read-only Plan and permission-restricted Build using each
  vendor's official supported sandbox configuration, without bypassing policies.
- Implement tests/CI/acceptance criteria as deterministic completion gates.
- Add durable task checkpoint/restart and cost-per-accepted-task reporting,
  with no assumptions about exact subscription-token accounting.
- Compare OpenCode separately using allowed ChatGPT login, with a synthetic
  public repository and same tasks; keep other vendors' subscription tokens
  out of OpenCode plugins.
