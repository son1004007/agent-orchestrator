from .base import CliAgentAdapter


class GeminiAdapter(CliAgentAdapter):
    name = "gemini"
    env_var = "GEMINI_BIN"
    default_binary = "gemini"

    def build_command(self, binary: str, prompt: str) -> list[str]:
        return [binary, "-p", prompt]
