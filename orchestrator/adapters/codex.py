from .base import CliAgentAdapter


class CodexAdapter(CliAgentAdapter):
    name = "codex"
    env_var = "CODEX_BIN"
    default_binary = "codex"

    def build_command(self, binary: str, prompt: str) -> list[str]:
        # `codex exec` is intended for non-interactive automation.
        return [binary, "exec", prompt]
