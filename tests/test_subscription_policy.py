import pytest

from orchestrator.subscription_policy import SubscriptionPolicyError, check_agent


def test_codex_allowed_in_clean_subscription_env():
    check_agent("codex", environ={})


@pytest.mark.parametrize("key", [
    "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY",
])
def test_api_keys_blocked_even_for_codex(key):
    with pytest.raises(SubscriptionPolicyError, match="API-key environment"):
        check_agent("codex", environ={key: "example-do-not-use"})


def test_claude_requires_native_subscription_opt_in():
    with pytest.raises(SubscriptionPolicyError, match="explicit"):
        check_agent("claude", environ={})
    check_agent("claude", environ={"AGENT_ALLOW_CLAUDE_NATIVE": "1"})


@pytest.mark.parametrize("agent", ["agy", "gemini", "unknown"])
def test_unsupported_agents_blocked(agent):
    with pytest.raises(SubscriptionPolicyError):
        check_agent(agent, environ={})
