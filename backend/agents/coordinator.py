"""Coordinator agent that orchestrates specialist agents and consolidates findings."""

import ast
import asyncio
import time
from collections import defaultdict
from typing import Any, Callable

from backend.models import (
    AgentCompletedEvent,
    AgentDelegatedEvent,
    AgentErrorEvent,
    AgentResult,
    AgentStartedEvent,
    AgentType,
    Finding,
    FindingsConsolidatedEvent,
    FinalReportEvent,
    PlanCreatedEvent,
    Severity,
)
from backend.agents.base import BaseAgent


class CoordinatorAgent(BaseAgent):
    """
    Coordinator agent that orchestrates specialist agents.

    The coordinator:
    1. Analyzes code structure
    2. Creates an execution plan
    3. Delegates to specialist agents concurrently
    4. Consolidates findings from all agents
    5. Produces final review report
    """

    def __init__(self, specialists: list[BaseAgent] | None = None):
        """
        Initialize the coordinator agent.

        Args:
            specialists: List of specialist BaseAgent instances to delegate to.
                        If None, coordinator will run with no specialists (useful for testing).
        """
        super().__init__(AgentType.COORDINATOR)
        self.specialists = specialists or []

    async def analyze(
        self,
        code: str,
        context: dict[str, Any],
        event_callback: Callable[[Any], Any],
    ) -> AgentResult:
        """
        Orchestrate code review by delegating to specialist agents.

        Args:
            code: Python code to analyze
            context: Shared context (metadata, previous findings, etc.)
            event_callback: Callback to emit events

        Returns:
            AgentResult with consolidated findings
        """
        start_time = time.time()

        try:
            # Emit agent started
            await event_callback(
                AgentStartedEvent(agent_id=AgentType.COORDINATOR, data={})
            )

            # Step 1: Parse code structure
            code_metadata = self._parse_code(code)

            # Step 2: Create execution plan
            plan_steps = self._create_plan(code_metadata)
            await event_callback(
                PlanCreatedEvent(
                    agent_id=AgentType.COORDINATOR,
                    data={"plan_steps": plan_steps},
                )
            )

            # Step 3: Delegate to specialists concurrently
            specialist_results = await self._delegate_to_specialists(
                code, context, event_callback
            )

            # Step 4: Consolidate findings
            consolidated_findings, conflicts_resolved = self._consolidate_findings(
                specialist_results
            )

            # Emit findings consolidated
            by_severity = self._count_by_severity(consolidated_findings)
            await event_callback(
                FindingsConsolidatedEvent(
                    agent_id=AgentType.COORDINATOR,
                    data={
                        "total_findings": len(consolidated_findings),
                        "by_severity": by_severity,
                        "conflicts_resolved": conflicts_resolved,
                    },
                )
            )

            # Step 5: Generate final report
            critical_findings = [
                f for f in consolidated_findings if f.severity == Severity.CRITICAL
            ]
            fixes_proposed = context.get("fixes_proposed", 0)
            fixes_verified = context.get("fixes_verified", 0)

            summary = f"Code review complete. Found {len(consolidated_findings)} issues."
            if critical_findings:
                summary += f" {len(critical_findings)} critical."

            final_report_data = {
                "summary": summary,
                "total_findings": len(consolidated_findings),
                "by_severity": by_severity,
                "critical_findings": [
                    {
                        "finding_id": f.finding_id,
                        "category": f.category,
                        "severity": f.severity.value,
                        "line": f.line,
                        "description": f.description,
                    }
                    for f in critical_findings
                ],
                "fixes_proposed": fixes_proposed,
                "fixes_verified": fixes_verified,
            }

            await event_callback(
                FinalReportEvent(
                    agent_id=AgentType.COORDINATOR,
                    data=final_report_data,
                )
            )

            # Emit agent completed
            duration_ms = int((time.time() - start_time) * 1000)
            await event_callback(
                AgentCompletedEvent(
                    agent_id=AgentType.COORDINATOR,
                    data={
                        "findings_count": len(consolidated_findings),
                        "duration_ms": duration_ms,
                    },
                )
            )

            return AgentResult(
                agent_id=AgentType.COORDINATOR,
                findings=consolidated_findings,
                metadata={
                    "code_lines": code_metadata["lines"],
                    "functions": code_metadata["functions"],
                    "classes": code_metadata["classes"],
                    "consolidation_conflicts_resolved": conflicts_resolved,
                },
            )

        except Exception as e:
            # Emit error and return empty result
            await event_callback(
                AgentErrorEvent(
                    agent_id=AgentType.COORDINATOR,
                    data={
                        "error": str(e),
                        "traceback": None,
                    },
                )
            )
            return AgentResult(
                agent_id=AgentType.COORDINATOR,
                findings=[],
                errors=[str(e)],
            )

    def _parse_code(self, code: str) -> dict[str, Any]:
        """Parse code structure using AST."""
        try:
            tree = ast.parse(code)
            lines = len(code.splitlines())
            functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            imports = sum(
                1 for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
            )
            return {
                "lines": lines,
                "functions": functions,
                "classes": classes,
                "imports": imports,
            }
        except SyntaxError:
            return {"lines": len(code.splitlines()), "functions": 0, "classes": 0, "imports": 0}

    def _create_plan(self, code_metadata: dict[str, Any]) -> list[dict[str, Any]]:
        """Create execution plan with steps."""
        plan = [
            {
                "step": 1,
                "action": "parse_code",
                "description": "Parse code structure",
            }
        ]

        # Add specialist steps
        for idx, specialist in enumerate(self.specialists, start=2):
            agent_name = specialist.agent_id.value.replace("_agent", "").replace("_", " ").title()
            plan.append(
                {
                    "step": idx,
                    "action": f"{specialist.agent_id.value}_analysis",
                    "description": f"Run {agent_name} analysis",
                    "parallel_with": [i for i in range(2, 2 + len(self.specialists)) if i != idx],
                }
            )

        # Add consolidation step
        plan.append(
            {
                "step": len(plan) + 1,
                "action": "consolidate",
                "description": "Consolidate findings",
            }
        )

        return plan

    async def _delegate_to_specialists(
        self,
        code: str,
        context: dict[str, Any],
        event_callback: Callable[[Any], Any],
    ) -> list[AgentResult]:
        """Delegate to all specialists concurrently."""
        tasks = []

        for specialist in self.specialists:
            # Emit delegation event
            await event_callback(
                AgentDelegatedEvent(
                    agent_id=AgentType.COORDINATOR,
                    data={
                        "delegated_to": specialist.agent_id.value,
                        "task": f"Perform {specialist.agent_id.value.replace('_agent', '')} analysis on provided code",
                    },
                )
            )

            # Create task for this specialist
            tasks.append(specialist.analyze(code, context, event_callback))

        # Run all specialists concurrently
        if tasks:
            return await asyncio.gather(*tasks, return_exceptions=False)
        return []

    def _consolidate_findings(
        self, specialist_results: list[AgentResult]
    ) -> tuple[list[Finding], int]:
        """
        Consolidate findings from all specialists.

        Deduplicates findings with same (category, line), keeping highest severity.
        Returns consolidated findings and count of conflicts resolved.
        """
        findings_by_key = {}
        conflicts_resolved = 0

        for result in specialist_results:
            for finding in result.findings:
                key = (finding.category, finding.line)

                if key in findings_by_key:
                    existing = findings_by_key[key]
                    # Keep the one with higher severity
                    if self._severity_rank(finding.severity) > self._severity_rank(existing.severity):
                        findings_by_key[key] = finding
                        conflicts_resolved += 1
                    else:
                        conflicts_resolved += 1
                else:
                    findings_by_key[key] = finding

        return list(findings_by_key.values()), conflicts_resolved

    def _severity_rank(self, severity: Severity) -> int:
        """Return numeric rank for severity (higher = more severe)."""
        rank = {
            Severity.CRITICAL: 5,
            Severity.HIGH: 4,
            Severity.MEDIUM: 3,
            Severity.LOW: 2,
            Severity.INFO: 1,
        }
        return rank.get(severity, 0)

    def _count_by_severity(self, findings: list[Finding]) -> dict[str, int]:
        """Count findings by severity level."""
        counts = defaultdict(int)
        for finding in findings:
            counts[finding.severity.value] += 1
        return {
            "critical": counts.get("critical", 0),
            "high": counts.get("high", 0),
            "medium": counts.get("medium", 0),
            "low": counts.get("low", 0),
            "info": counts.get("info", 0),
        }
