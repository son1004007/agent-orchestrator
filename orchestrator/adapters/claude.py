from .base import CliAgentAdapter


class ClaudeAdapter(CliAgentAdapter):
    name = "claude"
    env_var = "CLAUDE_BIN"
    default_binary = "claude"

    def build_command(self, binary: str, prompt: str) -> list[str]:
        return [binary, "-p", prompt]
