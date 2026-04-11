from __future__ import annotations

import difflib
import json
import re

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel

from devseeker.applications.cli.cli_agent import CliAgent
from devseeker.core.default.disk_execution_env import DiskExecutionEnv
from devseeker.core.files_dict import FilesDict
from devseeker.core.prompt import Prompt
from devseeker.runtime.modes import AgentMode, ToolRiskClass
from devseeker.runtime.permissions import ToolExecutor
from devseeker.runtime.repo_map import RepoMap, RepoMapBuilder
from devseeker.runtime.sessions import SessionRecord, SessionStore

PLANNER_SYSTEM_PROMPT = """You are DevSeeker's planning engine.
Return strict JSON with keys:
- summary: short string
- selected_files: array of relative file paths
- steps: array of objects with title, mode, objective, status
- verification: array of short checks
Keep the plan concrete and scoped to the current repository.
Never include markdown fences."""

ASK_SYSTEM_PROMPT = """You are DevSeeker in ask mode.
Answer the user's question using the repository map and selected file context.
Do not propose writes or commands."""

REVIEW_SYSTEM_PROMPT = """You are DevSeeker in review mode.
Review the proposed code changes against the user's request.
Return strict JSON with keys:
- verdict: pass or fail
- summary: short string
- issues: array of short strings
Never include markdown fences."""


@dataclass
class PlanStep:
    title: str
    mode: str
    objective: str
    status: str = "pending"


@dataclass
class ExecutionPlan:
    summary: str
    selected_files: List[str] = field(default_factory=list)
    steps: List[PlanStep] = field(default_factory=list)
    verification: List[str] = field(default_factory=list)

    def to_instruction_text(self) -> str:
        lines = [f"Plan summary: {self.summary}", "Steps:"]
        for step in self.steps:
            lines.append(f"- [{step.mode}] {step.title}: {step.objective}")
        if self.selected_files:
            lines.append("Selected files:")
            lines.extend(f"- {path}" for path in self.selected_files)
        if self.verification:
            lines.append("Verification:")
            lines.extend(f"- {item}" for item in self.verification)
        return "\n".join(lines)

    def to_rows(self) -> List[dict]:
        return [
            {
                "title": step.title,
                "mode": step.mode,
                "objective": step.objective,
                "status": step.status,
            }
            for step in self.steps
        ]


@dataclass
class AgentLoopResult:
    session_id: str
    mode: AgentMode
    message: str = ""
    plan: Optional[ExecutionPlan] = None
    files_before: Optional[FilesDict] = None
    files_after: Optional[FilesDict] = None
    selected_files: List[str] = field(default_factory=list)


class AgentLoop:
    def __init__(
        self,
        agent: CliAgent,
        repo_map_builder: RepoMapBuilder,
        session_store: SessionStore,
        tool_executor: ToolExecutor,
        console: Console,
    ):
        self.agent = agent
        self.repo_map_builder = repo_map_builder
        self.session_store = session_store
        self.tool_executor = tool_executor
        self.console = console

    def run(
        self,
        *,
        session: SessionRecord,
        prompt: Prompt,
        project_path: Path,
        mode: AgentMode,
        improve_mode: bool,
        diff_timeout: int,
        execution_env: DiskExecutionEnv,
    ) -> AgentLoopResult:
        repo_map = self.tool_executor.run(
            "repo_map",
            ToolRiskClass.READ_ONLY,
            "Build repository map",
            self.repo_map_builder.build,
        )
        self.session_store.update_state(
            session.session_id,
            repo_map_summary=repo_map.to_summary(),
        )
        self.session_store.log_turn(session.session_id, "user", prompt.text)

        if mode == AgentMode.ASK:
            answer = self._ask(prompt, repo_map)
            self.session_store.log_turn(session.session_id, "assistant", answer, kind="ask")
            return AgentLoopResult(
                session_id=session.session_id,
                mode=mode,
                message=answer,
            )

        plan = self._build_plan(prompt, repo_map, mode, improve_mode)
        self.session_store.replace_plan(session.session_id, plan.to_rows())
        selected_files = plan.selected_files or repo_map.select_relevant_files(prompt.text)
        self.session_store.update_state(
            session.session_id,
            selected_files=selected_files,
        )

        if mode == AgentMode.PLAN:
            self.session_store.log_turn(
                session.session_id,
                "assistant",
                plan.to_instruction_text(),
                kind="plan",
            )
            return AgentLoopResult(
                session_id=session.session_id,
                mode=mode,
                message=plan.to_instruction_text(),
                plan=plan,
                selected_files=selected_files,
            )

        if improve_mode:
            files_before = FilesDict(self.repo_map_builder.load_files(selected_files))
        else:
            files_before = FilesDict()

        if mode == AgentMode.REVIEW:
            review_text = self._review_existing(repo_map, prompt, files_before)
            self.session_store.log_turn(
                session.session_id,
                "assistant",
                review_text,
                kind="review",
            )
            return AgentLoopResult(
                session_id=session.session_id,
                mode=mode,
                message=review_text,
                plan=plan,
                files_before=files_before,
                selected_files=selected_files,
            )

        self.tool_executor.run(
            "apply_changes",
            ToolRiskClass.WRITE,
            "Apply generated file changes",
            lambda: None,
        )
        execution_prompt = self._enriched_prompt(prompt, plan)
        if improve_mode:
            files_after = self.agent.improve(
                files_before,
                execution_prompt,
                diff_timeout=diff_timeout,
            )
        else:
            files_after = self.agent.init(execution_prompt)

        verification = self._verify(prompt, plan, files_before, files_after)
        if verification["verdict"] == "fail" and mode in {AgentMode.AUTO, AgentMode.FIX}:
            verifier_feedback = "\n".join(verification["issues"])
            fixed_prompt = self._enriched_prompt(prompt, plan, verifier_feedback=verifier_feedback)
            if improve_mode:
                files_after = self.agent.improve(
                    files_after,
                    fixed_prompt,
                    diff_timeout=diff_timeout,
                )
            else:
                files_after = self.agent.improve(
                    files_after,
                    fixed_prompt,
                    diff_timeout=diff_timeout,
                )

        if mode in {AgentMode.AUTO, AgentMode.FIX} and "run.sh" in files_after:
            try:
                self._run_verification_script(session.session_id, execution_env, files_after)
            except PermissionError:
                verification["summary"] = (
                    verification.get("summary", "Verification complete")
                    + "; shell verification skipped by policy"
                )

        summary = self._render_result_message(plan, selected_files, verification)
        self.session_store.log_turn(session.session_id, "assistant", summary, kind="execution")
        return AgentLoopResult(
            session_id=session.session_id,
            mode=mode,
            message=summary,
            plan=plan,
            files_before=files_before if files_before else None,
            files_after=files_after,
            selected_files=selected_files,
        )

    def _ask(self, prompt: Prompt, repo_map: RepoMap) -> str:
        messages = self.agent.ai.start(
            ASK_SYSTEM_PROMPT,
            f"Repository summary:\n{repo_map.to_summary()}\n\nUser request:\n{prompt.text}",
            step_name="ask_mode",
        )
        return self._message_text(messages[-1])

    def _build_plan(
        self,
        prompt: Prompt,
        repo_map: RepoMap,
        mode: AgentMode,
        improve_mode: bool,
    ) -> ExecutionPlan:
        user_prompt = "\n".join(
            [
                f"Mode: {mode.value}",
                f"Improve mode: {improve_mode}",
                "Repository summary:",
                repo_map.to_summary(),
                "",
                f"User request: {prompt.text}",
            ]
        )
        try:
            messages = self.agent.ai.start(
                PLANNER_SYSTEM_PROMPT,
                user_prompt,
                step_name="planner",
            )
            parsed = self._parse_json(self._message_text(messages[-1]))
        except Exception:
            parsed = {}

        if not isinstance(parsed, dict):
            parsed = {}

        selected_files = parsed.get("selected_files") or repo_map.select_relevant_files(prompt.text)
        steps = parsed.get("steps") or self._fallback_steps(mode, improve_mode)
        verification = parsed.get("verification") or ["Diff matches the request", "No unrelated files changed"]

        return ExecutionPlan(
            summary=parsed.get("summary") or self._fallback_summary(prompt.text, improve_mode),
            selected_files=selected_files,
            steps=[
                PlanStep(
                    title=step.get("title", "Step"),
                    mode=step.get("mode", mode.value),
                    objective=step.get("objective", ""),
                    status=step.get("status", "pending"),
                )
                for step in steps
            ],
            verification=verification,
        )

    def _review_existing(self, repo_map: RepoMap, prompt: Prompt, files_before: FilesDict) -> str:
        context = "\n".join(
            [
                "Repository summary:",
                repo_map.to_summary(),
                "",
                "Selected file context:",
                files_before.to_log() if files_before else "(none)",
                "",
                f"User request: {prompt.text}",
            ]
        )
        messages = self.agent.ai.start(
            ASK_SYSTEM_PROMPT,
            context,
            step_name="review_existing",
        )
        return self._message_text(messages[-1])

    def _verify(
        self,
        prompt: Prompt,
        plan: ExecutionPlan,
        files_before: FilesDict,
        files_after: FilesDict,
    ) -> dict:
        diff_text = self._diff_text(files_before, files_after)
        payload = "\n".join(
            [
                f"User request: {prompt.text}",
                "",
                plan.to_instruction_text(),
                "",
                "Diff:",
                diff_text or "(no diff)",
            ]
        )
        try:
            messages = self.agent.ai.start(
                REVIEW_SYSTEM_PROMPT,
                payload,
                step_name="verifier",
            )
            parsed = self._parse_json(self._message_text(messages[-1]))
        except Exception:
            parsed = {}

        if not isinstance(parsed, dict):
            parsed = {}
        verdict = parsed.get("verdict", "pass")
        if files_before == files_after:
            verdict = "fail"
        return {
            "verdict": verdict,
            "summary": parsed.get("summary", "Verification complete"),
            "issues": parsed.get("issues", [] if verdict == "pass" else ["No changes were produced"]),
        }

    def _run_verification_script(
        self,
        session_id: str,
        execution_env: DiskExecutionEnv,
        files_after: FilesDict,
    ) -> None:
        def run_script() -> None:
            stdout, stderr, code = execution_env.upload(files_after).run("sh run.sh")
            if code != 0:
                details = (stderr or stdout).strip() or "run.sh failed"
                self.session_store.update_state(
                    session_id,
                    last_failing_command="sh run.sh",
                )
                raise RuntimeError(details)

        self.tool_executor.run(
            "run_entrypoint",
            ToolRiskClass.SHELL,
            "Execute run.sh for verification",
            run_script,
        )

    def _render_result_message(
        self,
        plan: ExecutionPlan,
        selected_files: List[str],
        verification: dict,
    ) -> str:
        selected = ", ".join(selected_files[:10]) or "none"
        return "\n".join(
            [
                f"Plan: {plan.summary}",
                f"Selected files: {selected}",
                f"Verification: {verification.get('summary', 'Verification complete')}",
            ]
        )

    def _enriched_prompt(
        self,
        prompt: Prompt,
        plan: ExecutionPlan,
        verifier_feedback: str = "",
    ) -> Prompt:
        parts = [prompt.text, "", plan.to_instruction_text()]
        if verifier_feedback:
            parts.extend(["", "Verifier feedback:", verifier_feedback])
        return Prompt(
            text="\n".join(parts),
            image_urls=prompt.image_urls,
            entrypoint_prompt=prompt.entrypoint_prompt,
        )

    def _fallback_summary(self, prompt_text: str, improve_mode: bool) -> str:
        action = "Improve" if improve_mode else "Generate"
        trimmed = prompt_text.strip().splitlines()[0][:120]
        return f"{action} project for: {trimmed}"

    def _fallback_steps(self, mode: AgentMode, improve_mode: bool) -> List[dict]:
        if mode == AgentMode.FIX:
            return [
                {"title": "Inspect current code", "mode": "review", "objective": "Find likely failure points"},
                {"title": "Apply targeted fix", "mode": "fix", "objective": "Modify the smallest set of files"},
                {"title": "Verify behavior", "mode": "review", "objective": "Check the result against the request"},
            ]
        if improve_mode:
            return [
                {"title": "Inspect repo map", "mode": "plan", "objective": "Choose relevant files"},
                {"title": "Edit targeted files", "mode": "edit", "objective": "Apply the requested changes"},
                {"title": "Review diff", "mode": "review", "objective": "Reject unrelated changes"},
            ]
        return [
            {"title": "Plan project structure", "mode": "plan", "objective": "Choose initial files"},
            {"title": "Generate implementation", "mode": "edit", "objective": "Create the required files"},
            {"title": "Verify generated output", "mode": "review", "objective": "Check the generated result"},
        ]

    def _parse_json(self, content: str) -> Any:
        stripped = content.strip()
        if stripped.startswith("```"):
            match = re.search(r"```(?:json)?\n(.*?)```", stripped, re.DOTALL)
            if match:
                stripped = match.group(1).strip()
        return json.loads(stripped)

    def _message_text(self, message: Any) -> str:
        content = getattr(message, "content", message)
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
            return "\n".join(part for part in text_parts if part).strip()
        return str(content).strip()

    def _diff_text(self, files_before: FilesDict, files_after: FilesDict) -> str:
        diff_chunks: List[str] = []
        all_files = sorted(set(files_before.keys()) | set(files_after.keys()))
        for file_name in all_files:
            before = files_before.get(file_name, "").splitlines()
            after = files_after.get(file_name, "").splitlines()
            diff = difflib.unified_diff(
                before,
                after,
                fromfile=file_name,
                tofile=file_name,
                lineterm="",
            )
            chunk = "\n".join(diff).strip()
            if chunk:
                diff_chunks.append(chunk)
        return "\n\n".join(diff_chunks)
