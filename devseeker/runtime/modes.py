from enum import Enum


class AgentMode(str, Enum):
    AUTO = "auto"
    ASK = "ask"
    PLAN = "plan"
    EDIT = "edit"
    FIX = "fix"
    REVIEW = "review"

    @classmethod
    def parse(cls, value: str) -> "AgentMode":
        normalized = value.strip().lower()
        for mode in cls:
            if mode.value == normalized:
                return mode
        raise ValueError(f"Unsupported agent mode: {value}")


class ToolRiskClass(str, Enum):
    READ_ONLY = "read_only"
    WRITE = "write"
    SHELL = "shell"
    NETWORK = "network"
