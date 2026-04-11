from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

from devseeker.runtime.modes import AgentMode, ToolRiskClass


PermissionPrompt = Callable[[str], bool]


@dataclass
class ExecutionPolicy:
    risk_rules: Dict[ToolRiskClass, str]
    interactive: bool = True

    @classmethod
    def for_mode(cls, mode: AgentMode, interactive: bool = True) -> "ExecutionPolicy":
        if mode in {AgentMode.ASK, AgentMode.PLAN, AgentMode.REVIEW}:
            return cls(
                risk_rules={
                    ToolRiskClass.READ_ONLY: "allow",
                    ToolRiskClass.WRITE: "deny",
                    ToolRiskClass.SHELL: "deny",
                    ToolRiskClass.NETWORK: "deny",
                },
                interactive=interactive,
            )

        return cls(
            risk_rules={
                ToolRiskClass.READ_ONLY: "allow",
                ToolRiskClass.WRITE: "ask",
                ToolRiskClass.SHELL: "ask",
                ToolRiskClass.NETWORK: "deny",
            },
            interactive=interactive,
        )

    def authorize(
        self,
        risk: ToolRiskClass,
        action: str,
        prompt_fn: Optional[PermissionPrompt] = None,
    ) -> bool:
        decision = self.risk_rules.get(risk, "deny")
        if decision == "allow":
            return True
        if decision == "deny":
            return False
        if not self.interactive or prompt_fn is None:
            return False
        return prompt_fn(action)


class ToolExecutor:
    def __init__(
        self,
        policy: ExecutionPolicy,
        prompt_fn: Optional[PermissionPrompt] = None,
        event_logger: Optional[Callable[[str, ToolRiskClass, bool, str], None]] = None,
    ):
        self.policy = policy
        self.prompt_fn = prompt_fn
        self.event_logger = event_logger

    def run(
        self,
        name: str,
        risk: ToolRiskClass,
        action: str,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        allowed = self.policy.authorize(risk, action, self.prompt_fn)
        if self.event_logger is not None:
            self.event_logger(name, risk, allowed, action)
        if not allowed:
            raise PermissionError(f"Blocked {risk.value} action: {action}")
        return func(*args, **kwargs)
