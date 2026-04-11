from devseeker.runtime.modes import AgentMode, ToolRiskClass
from devseeker.runtime.permissions import ExecutionPolicy, ToolExecutor


def test_plan_mode_denies_write_actions():
    policy = ExecutionPolicy.for_mode(AgentMode.PLAN, interactive=True)
    assert policy.authorize(ToolRiskClass.READ_ONLY, "Read repository")
    assert not policy.authorize(ToolRiskClass.WRITE, "Write file")


def test_edit_mode_asks_before_write():
    prompts = []
    policy = ExecutionPolicy.for_mode(AgentMode.EDIT, interactive=True)

    allowed = policy.authorize(
        ToolRiskClass.WRITE,
        "Apply generated changes",
        prompt_fn=lambda action: prompts.append(action) or True,
    )

    assert allowed
    assert prompts == ["Apply generated changes"]


def test_tool_executor_logs_and_blocks_denied_actions():
    events = []
    policy = ExecutionPolicy.for_mode(AgentMode.ASK, interactive=False)
    executor = ToolExecutor(
        policy,
        event_logger=lambda name, risk, allowed, action: events.append(
            (name, risk.value, allowed, action)
        ),
    )

    try:
        executor.run(
            "write_file",
            ToolRiskClass.WRITE,
            "Write file",
            lambda: "ok",
        )
    except PermissionError as exc:
        assert "Blocked write action" in str(exc)
    else:
        raise AssertionError("Expected PermissionError")

    assert events == [("write_file", "write", False, "Write file")]
