"""Conservative subscription-only CLI execution gates.

Never brokers credentials or copies OAuth tokens.
"""
from collections.abc import Mapping
import os


class SubscriptionPolicyError(ValueError):
    """Execution must stop before potentially billable or unsupported invocation."""


_API_KEYS = frozenset({"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"})


def check_agent(agent: str, environ: Mapping[str, str] | None = None) -> None:
    """Enforce native CLI routes, not proof of active subscription authentication."""
    env = os.environ if environ is None else environ
    if any(env.get(key) for key in _API_KEYS):
        raise SubscriptionPolicyError(
            "API-key environment detected. Refusing subscription-only CLI invocation. "
            "Use an isolated native subscription login; do not change existing keys."
        )
    if agent == "codex":
        return
    if agent == "claude":
        if env.get("AGENT_ALLOW_CLAUDE_NATIVE") == "1":
            return
        raise SubscriptionPolicyError(
            "Native Claude Code requires verified personal Pro/Max login and explicit "
            "AGENT_ALLOW_CLAUDE_NATIVE=1; API fallback is prohibited."
        )
    if agent in {"agy", "gemini"}:
        raise SubscriptionPolicyError(
            "AGY consumer subscription must not be wrapped inside a third-party agent. "
            "Use official Antigravity CLI/App or supported direct scripting/CI separately. "
            "Legacy Gemini CLI is not the authenticated AGY CLI."
        )
    raise SubscriptionPolicyError(f"Unknown agent: {agent!r}")


def availability(agents: list[str], environ: Mapping[str, str] | None = None) -> dict[str, str]:
    """Report routes without launching models or reading stored credentials."""
    status = {}
    for agent in agents:
        try:
            check_agent(agent, environ=environ)
            status[agent] = "PERMITTED_UNVERIFIED_AUTH"
        except SubscriptionPolicyError as exc:
            status[agent] = f"BLOCKED: {exc}"
    return status
