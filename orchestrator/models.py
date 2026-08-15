from dataclasses import dataclass, field
from enum import Enum


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(slots=True)
class AgentResult:
    agent: str
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


@dataclass(slots=True)
class WorkflowStep:
    name: str
    primary: str
    fallback: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
